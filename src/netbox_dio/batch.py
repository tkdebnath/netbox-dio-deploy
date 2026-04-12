"""Batch processor for handling large numbers of devices with automatic chunking.

This module provides:
- Automatic chunking of device lists at 1000 devices per chunk
- Per-device error reporting for batch operations
- Enhanced error aggregation and summary reporting
- Integration with DiodeClient for transmission
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time

from netboxlabs.diode.sdk.ingester import Entity

from .client import DiodeClient, DiodeClientError
from .converter import convert_device_to_entities
from .exceptions import DiodeBatchError


@dataclass
class DeviceError:
    """Error information for a single device in a batch operation.

    Captures errors during conversion or transmission to enable
    granular error reporting and potential retry logic.
    """

    device_name: str
    error_message: str
    original_dict: dict
    stack_trace: Optional[str] = None
    device_type: Optional[str] = None
    timing_ms: Optional[float] = None

    @classmethod
    def from_exception(
        cls,
        device_name: str,
        exc: Exception,
        original_dict: dict,
        stack_trace: Optional[str] = None,
        device_type: Optional[str] = None,
        timing_ms: Optional[float] = None,
    ) -> DeviceError:
        """Create a DeviceError from an exception.

        Args:
            device_name: The name of the device that failed
            exc: The exception that occurred
            original_dict: The original device dictionary
            stack_trace: Optional stack trace string
            device_type: Optional device type from original dict
            timing_ms: Optional timing information in milliseconds
        """
        return cls(
            device_name=device_name,
            error_message=str(exc),
            original_dict=original_dict,
            stack_trace=stack_trace,
            device_type=device_type,
            timing_ms=timing_ms,
        )


@dataclass
class BatchResult:
    """Result of a batch processing operation.

    Tracks the outcome of processing a batch of devices including
    success/failure counts and per-device error details.
    """

    total: int
    success: int
    failed: int
    errors: list[DeviceError]

    def __post_init__(self):
        """Validate result counts."""
        if self.success + self.failed != self.total:
            raise ValueError(
                f"Success count ({self.success}) + failed count ({self.failed}) "
                f"must equal total ({self.total})"
            )

    def get_error_summary(self) -> Dict[str, int]:
        """Get a summary of error types and their counts.

        Returns:
            Dictionary mapping error type names to their counts
        """
        summary: Dict[str, int] = {}
        for error in self.errors:
            # Extract the exception type
            error_type = type(error).__name__
            if error_type not in summary:
                summary[error_type] = 0
            summary[error_type] += 1

        # Also check for specific exception types in error messages
        for error in self.errors:
            if "ValidationError" in error.error_message:
                summary["DiodeValidationError"] = summary.get("DiodeValidationError", 0) + 1
            elif "ConversionError" in error.error_message:
                summary["DiodeConversionError"] = summary.get("DiodeConversionError", 0) + 1
            elif "ClientError" in error.error_message:
                summary["DiodeClientError"] = summary.get("DiodeClientError", 0) + 1
            elif "ServerResponseError" in error.error_message:
                summary["DiodeServerResponseError"] = summary.get("DiodeServerResponseError", 0) + 1

        return summary

    def get_failed_devices(self) -> List[str]:
        """Get a list of failed device names.

        Returns:
            List of device names that failed during processing
        """
        return [error.device_name for error in self.errors]

    def has_errors(self) -> bool:
        """Check if there were any errors in the batch.

        Returns:
            True if any devices failed, False otherwise
        """
        return self.failed > 0


class BatchProcessor:
    """Process batches of devices with automatic chunking.

    Handles large numbers of devices by automatically splitting them
    into chunks of configurable size (default 1000) and processing
    each chunk separately with error tracking.

    Example:
        >>> from netbox_dio import DiodeClient, BatchProcessor
        >>> from netbox_dio.models import DiodeDevice
        >>>
        >>> client = DiodeClient.from_env()
        >>> client.connect()
        >>>
        >>> devices = [
        ...     DiodeDevice(name=f'dev{i}', site='site-a',
        ...                 device_type='cisco-9300', role='core-router')
        ...     for i in range(1500)
        ... ]
        >>>
        >>> processor = BatchProcessor(max_chunk_size=1000)
        >>> result = processor.process_batch(client, devices)
        >>> print(f"Success: {result.success}, Failed: {result.failed}")
    """

    def __init__(self, max_chunk_size: int = 1000) -> None:
        """Initialize the BatchProcessor.

        Args:
            max_chunk_size: Maximum number of devices per chunk.
                           Must be between 1 and 1000. Defaults to 1000.

        Raises:
            ValueError: If max_chunk_size is not between 1 and 1000
        """
        if not 1 <= max_chunk_size <= 1000:
            raise ValueError(
                f"max_chunk_size must be between 1 and 1000, got {max_chunk_size}"
            )
        self._max_chunk_size = max_chunk_size

    @property
    def max_chunk_size(self) -> int:
        """Get the maximum number of devices per chunk."""
        return self._max_chunk_size

    def chunk_devices(self, devices: list) -> list[list]:
        """Split devices into chunks of max_chunk_size.

        Args:
            devices: List of DiodeDevice instances to chunk

        Returns:
            List of device chunks, each containing at most max_chunk_size devices
        """
        return [
            devices[i : i + self._max_chunk_size]
            for i in range(0, len(devices), self._max_chunk_size)
        ]

    def process_single_chunk(
        self, client: DiodeClient, devices: list
    ) -> BatchResult:
        """Process a single chunk of devices.

        Args:
            client: DiodeClient for transmission
            devices: List of DiodeDevice instances to process

        Returns:
            BatchResult with success/failure counts and errors
        """
        success_count = 0
        failed_count = 0
        errors: list[DeviceError] = []

        for device in devices:
            start_time = time.time()
            try:
                # Convert device to entities
                entities = convert_device_to_entities(device)
                # Send to Diode
                client.send_batch(entities)
                success_count += 1
            except Exception as e:
                failed_count += 1
                # Get device type from original dict if available
                device_type = None
                if hasattr(device, "__dict__"):
                    device_type = getattr(device, "device_type", None)
                elif isinstance(device, dict):
                    device_type = device.get("device_type")

                timing_ms = (time.time() - start_time) * 1000
                errors.append(DeviceError.from_exception(
                    device_name=getattr(device, "name", "unknown"),
                    exc=e,
                    original_dict=getattr(device, "__dict__", {}),
                    stack_trace=None,
                    device_type=device_type,
                    timing_ms=timing_ms,
                ))

        return BatchResult(
            total=len(devices),
            success=success_count,
            failed=failed_count,
            errors=errors,
        )

    def process_batch(
        self, client: DiodeClient, devices: list, return_on_first_error: bool = False
    ) -> BatchResult:
        """Process all devices, automatically chunking as needed.

        Args:
            client: DiodeClient for transmission
            devices: List of DiodeDevice instances to process
            return_on_first_error: If True, return immediately on first error

        Returns:
            BatchResult with aggregated results across all chunks
        """
        total_success = 0
        total_failed = 0
        all_errors: list[DeviceError] = []

        chunks = self.chunk_devices(devices)

        for chunk_num, chunk in enumerate(chunks, start=1):
            result = self.process_single_chunk(client, chunk)
            total_success += result.success
            total_failed += result.failed
            all_errors.extend(result.errors)

            # Check if we should return on first error
            if return_on_first_error and result.failed > 0:
                break

        return BatchResult(
            total=len(devices),
            success=total_success,
            failed=total_failed,
            errors=all_errors,
        )

    def get_chunked_payloads(
        self, devices: list
    ) -> list[tuple[int, list[Entity]]]:
        """Get entities for each chunk without transmission.

        Args:
            devices: List of DiodeDevice instances to chunk

        Returns:
            List of (chunk_number, list_of_entities) tuples
        """
        chunks = self.chunk_devices(devices)
        result = []

        for chunk_num, chunk in enumerate(chunks, start=1):
            entities = []
            for device in chunk:
                entities.extend(convert_device_to_entities(device))
            result.append((chunk_num, entities))

        return result


class BatchError(DiodeBatchError):
    """Exception for batch-level failures.

    Aggregates multiple DeviceErrors and provides summary statistics.
    """

    def __init__(
        self,
        message: str,
        errors: Optional[List[DeviceError]] = None,
        total: Optional[int] = None,
        failed: Optional[int] = None,
        summary: Optional[Dict[str, int]] = None,
    ) -> None:
        """Initialize a BatchError.

        Args:
            message: The batch error message
            errors: List of individual device errors
            total: Total number of devices in the batch
            failed: Number of failed devices
            summary: Dictionary summarizing error types and counts
        """
        super().__init__(
            message,
            errors=errors or [],
            total=total,
            failed=failed,
            summary=summary,
        )


def create_message_chunks(devices: list) -> list[tuple[int, list[Entity]]]:
    """Convert devices to entity chunks for batch transmission.

    This convenience function combines chunking and conversion:
    1. Splits devices into chunks of 1000
    2. Converts each chunk to Entity objects
    3. Returns list of (chunk_number, entities) tuples

    Args:
        devices: List of DiodeDevice instances to chunk and convert

    Returns:
        List of (chunk_number, list_of_entities) tuples

    Example:
        >>> from netbox_dio import DiodeDevice, create_message_chunks
        >>> devices = [
        ...     DiodeDevice(name=f'dev{i}', site='site',
        ...                 device_type='type', role='role')
        ...     for i in range(1500)
        ... ]
        >>> chunks = create_message_chunks(devices)
        >>> print(f"Number of chunks: {len(chunks)}")
        >>> print(f"First chunk size: {len(chunks[0][1])}")
    """
    # Use a temporary processor with the standard 1000 chunk size
    processor = BatchProcessor(max_chunk_size=1000)
    return processor.get_chunked_payloads(devices)


__all__ = [
    "BatchProcessor",
    "BatchResult",
    "DeviceError",
    "BatchError",
    "create_message_chunks",
]

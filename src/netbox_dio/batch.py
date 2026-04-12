"""Batch processor for handling large numbers of devices with automatic chunking.

This module provides:
- Automatic chunking of device lists at 1000 devices per chunk
- Per-device error reporting for batch operations
- Integration with DiodeClient for transmission
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from netboxlabs.diode.sdk.ingester import Entity

from .client import DiodeClient, DiodeClientError
from .converter import convert_device_to_entities


@dataclass
class DeviceError:
    """Error information for a single device in a batch operation.

    Captures errors during conversion or transmission to enable
    granular error reporting and potential retry logic.
    """
    device_name: str
    error_message: str
    original_dict: dict

    @classmethod
    def from_exception(cls, device_name: str, exc: Exception, original_dict: dict) -> DeviceError:
        """Create a DeviceError from an exception."""
        return cls(
            device_name=device_name,
            error_message=str(exc),
            original_dict=original_dict,
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
            try:
                # Convert device to entities
                entities = convert_device_to_entities(device)
                # Send to Diode
                client.send_batch(entities)
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(DeviceError.from_exception(
                    device_name=getattr(device, "name", "unknown"),
                    exc=e,
                    original_dict=getattr(device, "__dict__", {}),
                ))

        return BatchResult(
            total=len(devices),
            success=success_count,
            failed=failed_count,
            errors=errors,
        )

    def process_batch(
        self, client: DiodeClient, devices: list
    ) -> BatchResult:
        """Process all devices, automatically chunking as needed.

        Args:
            client: DiodeClient for transmission
            devices: List of DiodeDevice instances to process

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
    "create_message_chunks",
]

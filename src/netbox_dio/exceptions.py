"""Exception hierarchy for Diode errors.

This module defines a comprehensive exception hierarchy for handling errors
throughout the netbox-dio package. All exceptions inherit from DiodeError,
enabling users to catch all Diode-related errors with a single except clause.
"""

from __future__ import annotations

from typing import Optional


class DiodeError(Exception):
    """Base exception for all Diode-related errors.

    This is the root of the exception hierarchy. All other Diode exceptions
    inherit from this class, allowing users to catch all Diode errors with
    a single except clause.

    Example:
        >>> try:
        ...     device = DiodeDevice.from_dict(invalid_data)
        ... except DiodeError as e:
        ...     print(f"Diode error: {e}")
    """

    def __init__(self, message: str, context: Optional[dict] = None) -> None:
        """Initialize a DiodeError.

        Args:
            message: The error message
            context: Optional dictionary with additional context (device_name,
                     field_name, original_dict, etc.)
        """
        super().__init__(message)
        self._message = message
        self._context = context or {}

    @property
    def message(self) -> str:
        """Get the error message."""
        return self._message

    @property
    def context(self) -> dict:
        """Get the error context dictionary."""
        return self._context

    def __str__(self) -> str:
        """Return string representation with context."""
        base = self._message
        if self._context:
            context_str = ", ".join(f"{k}={v}" for k, v in self._context.items())
            return f"{base} [{context_str}]"
        return base


class DiodeValidationError(DiodeError):
    """Exception raised for data validation failures.

    This exception is raised when device data fails validation, including:
    - Missing required fields
    - Invalid field values (e.g., invalid status)
    - Field format violations (e.g., name too long)

    Example:
        >>> try:
        ...     device = DiodeDevice.from_dict({"name": "test"})
        ... except DiodeValidationError as e:
        ...     print(f"Validation failed on field: {e.context.get('field_name')}")
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        value: Optional[str] = None,
        device_name: Optional[str] = None,
    ) -> None:
        """Initialize a DiodeValidationError.

        Args:
            message: The validation error message
            field_name: The name of the field that failed validation
            value: The invalid value that was provided
            device_name: The name of the device being validated
        """
        context = {
            "field_name": field_name,
            "value": value,
            "device_name": device_name,
        }
        # Remove None values from context
        context = {k: v for k, v in context.items() if v is not None}
        super().__init__(message, context)


class DiodeConversionError(DiodeError):
    """Exception raised for conversion failures with source context.

    This exception is raised when converting from Pydantic models to Diode
    SDK protobuf messages. It includes the device name and original dictionary
    to help identify the source of the conversion error.

    Example:
        >>> try:
        ...     entity = convert_device(device)
        ... except DiodeConversionError as e:
        ...     print(f"Failed to convert device '{e.context.get('device_name')}'")
    """

    def __init__(
        self,
        message: str,
        device_name: Optional[str] = None,
        original_dict: Optional[dict] = None,
        conversion_type: Optional[str] = None,
    ) -> None:
        """Initialize a DiodeConversionError.

        Args:
            message: The conversion error message
            device_name: The name of the device being converted
            original_dict: The original dictionary being converted
            conversion_type: The type of conversion (e.g., 'interface', 'vlan')
        """
        context = {
            "device_name": device_name,
            "original_dict": original_dict,
            "conversion_type": conversion_type,
        }
        # Remove None values from context
        context = {k: v for k, v in context.items() if v is not None}
        super().__init__(message, context)


class DiodeClientError(DiodeError):
    """Exception raised for client connection failures.

    This exception wraps lower-level gRPC errors and provides contextual
    information about the connection failure. It can be extended with
    specific error types for different failure modes.

    Example:
        >>> try:
        ...     client.connect()
        ... except DiodeClientError as e:
        ...     print(f"Connection failed: {e}")
    """

    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """Initialize a DiodeClientError.

        Args:
            message: The client error message
            endpoint: The Diode endpoint that failed
            original_error: The original exception that caused this error
        """
        context = {
            "endpoint": endpoint,
            "original_error": str(original_error) if original_error else None,
        }
        # Remove None values from context
        context = {k: v for k, v in context.items() if v is not None}
        super().__init__(message, context)


class DiodeServerResponseError(DiodeError):
    """Exception raised for Diode server errors.

    This exception is raised when the Diode server returns an error response,
    such as authentication failures or resource not found errors.

    Example:
        >>> try:
        ...     result = client.send_single(device)
        ... except DiodeServerResponseError as e:
        ...     print(f"Server error: {e.context.get('request_id')}")
    """

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        device_name: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """Initialize a DiodeServerResponseError.

        Args:
            message: The server error message
            request_id: The request ID from the server
            device_name: The name of the device being sent
            status_code: The HTTP/gRPC status code
        """
        context = {
            "request_id": request_id,
            "device_name": device_name,
            "status_code": status_code,
        }
        # Remove None values from context
        context = {k: v for k, v in context.items() if v is not None}
        super().__init__(message, context)


class DiodeBatchError(DiodeError):
    """Exception raised for batch operation failures with aggregated errors.

    This exception is raised when batch processing fails and contains
    a summary of all individual device errors that occurred during the batch.

    Example:
        >>> try:
        ...     result = processor.process_batch(client, devices)
        ... except DiodeBatchError as e:
        ...     print(f"Batch failed with {len(e.context.get('errors', []))} errors")
    """

    def __init__(
        self,
        message: str,
        errors: Optional[list] = None,
        total: Optional[int] = None,
        failed: Optional[int] = None,
        summary: Optional[dict] = None,
    ) -> None:
        """Initialize a DiodeBatchError.

        Args:
            message: The batch error message
            errors: List of individual device errors
            total: Total number of devices in the batch
            failed: Number of failed devices
            summary: Dictionary summarizing error types and counts
        """
        context = {
            "errors": errors or [],
            "total": total,
            "failed": failed,
            "summary": summary,
        }
        # Remove None values from context
        context = {k: v for k, v in context.items() if v is not None}
        super().__init__(message, context)


# Additional I/O specific exception types
class DiodeConnectionRefusedError(DiodeClientError):
    """Exception raised when connection to Diode is refused.

    This exception is raised when the Diode server actively refuses
    the connection (e.g., port closed, service not running).
    """

    def __init__(self, endpoint: str) -> None:
        """Initialize a DiodeConnectionRefusedError.

        Args:
            endpoint: The endpoint that refused the connection
        """
        super().__init__(
            f"Connection refused to Diode at {endpoint}. "
            "Check that the Diode service is running and accessible.",
            endpoint=endpoint,
        )


class DiodeTimeoutError(DiodeClientError):
    """Exception raised when gRPC connection times out.

    This exception is raised when the connection or request times out
    before completing.
    """

    def __init__(self, endpoint: str, timeout: Optional[float] = None) -> None:
        """Initialize a DiodeTimeoutError.

        Args:
            endpoint: The endpoint that timed out
            timeout: The timeout value that was exceeded
        """
        msg = f"Connection timed out after {timeout}s" if timeout else "Connection timed out"
        msg += f" while connecting to Diode at {endpoint}."
        super().__init__(msg, endpoint=endpoint)


class DiodeAuthenticationError(DiodeClientError):
    """Exception raised for authentication failures.

    This exception is raised when Diode authentication fails due to
    invalid credentials or authentication configuration.
    """

    def __init__(self, message: str, endpoint: Optional[str] = None) -> None:
        """Initialize a DiodeAuthenticationError.

        Args:
            message: The authentication error message
            endpoint: The endpoint where authentication failed
        """
        super().__init__(
            f"Authentication failed: {message}",
            endpoint=endpoint,
        )


# Export all exceptions
__all__ = [
    "DiodeError",
    "DiodeValidationError",
    "DiodeConversionError",
    "DiodeClientError",
    "DiodeServerResponseError",
    "DiodeBatchError",
    "DiodeConnectionRefusedError",
    "DiodeTimeoutError",
    "DiodeAuthenticationError",
]

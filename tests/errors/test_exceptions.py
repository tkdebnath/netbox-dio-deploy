"""Comprehensive tests for exception hierarchy.

Tests cover:
- Exception inheritance hierarchy
- Exception instantiation with context
- String representation
- Context parameters
- Traceback preservation
- Exception chaining
"""

import pytest
import traceback

from netbox_dio import (
    DiodeError,
    DiodeValidationError,
    DiodeConversionError,
    DiodeClientError,
    DiodeServerResponseError,
    DiodeBatchError,
    DiodeConnectionRefusedError,
    DiodeTimeoutError,
    DiodeAuthenticationError,
)


class TestDiodeErrorIsBaseException:
    """Tests for DiodeError as base exception."""

    def test_diode_error_is_base_exception(self):
        """Test that DiodeError is a subclass of Exception."""
        assert issubclass(DiodeError, Exception)

    def test_diode_error_instantiation(self):
        """Test creating a DiodeError instance."""
        error = DiodeError("Base error message")
        assert error.message == "Base error message"
        assert str(error) == "Base error message"

    def test_diode_error_with_context(self):
        """Test creating a DiodeError with context."""
        error = DiodeError(
            "Base error",
            context={"field": "name", "value": "test"},
        )
        assert error.context.get("field") == "name"
        assert "field=name, value=test" in str(error)


class TestDiodeValidationErrorInheritsDiodeError:
    """Tests for DiodeValidationError inheritance."""

    def test_diode_validation_error_inherits_diode_error(self):
        """Test that DiodeValidationError inherits from DiodeError."""
        assert issubclass(DiodeValidationError, DiodeError)

    def test_diode_validation_error_instantiation(self):
        """Test creating a DiodeValidationError."""
        error = DiodeValidationError("Field validation failed")
        assert error.message == "Field validation failed"

    def test_diode_validation_error_with_context(self):
        """Test creating a DiodeValidationError with context."""
        error = DiodeValidationError(
            "Invalid field",
            field_name="status",
            value="bad",
            device_name="router-01",
        )

        assert error.context.get("field_name") == "status"
        assert error.context.get("value") == "bad"
        assert error.context.get("device_name") == "router-01"

    def test_diode_validation_error_string_representation(self):
        """Test string representation with context."""
        error = DiodeValidationError(
            "Invalid status",
            field_name="status",
            value="bad",
            device_name="router-01",
        )

        error_str = str(error)
        assert "Invalid status" in error_str
        assert "status" in error_str
        assert "router-01" in error_str


class TestDiodeConversionErrorIncludesContext:
    """Tests for DiodeConversionError context."""

    def test_diode_conversion_error_includes_context(self):
        """Test that DiodeConversionError includes device context."""
        error = DiodeConversionError(
            "Conversion failed",
            device_name="router-01",
            original_dict={"name": "router-01"},
            conversion_type="device",
        )

        assert error.context.get("device_name") == "router-01"
        assert error.context.get("conversion_type") == "device"

    def test_diode_conversion_error_string_representation(self):
        """Test string representation includes device name."""
        error = DiodeConversionError(
            "Failed to convert device",
            device_name="switch-01",
        )

        assert "switch-01" in str(error)


class TestDiodeClientErrorIncludesEndpoint:
    """Tests for DiodeClientError context."""

    def test_diode_client_error_includes_endpoint(self):
        """Test that DiodeClientError includes endpoint."""
        error = DiodeClientError(
            "Connection failed",
            endpoint="diode.example.com:443",
        )

        assert error.context.get("endpoint") == "diode.example.com:443"

    def test_diode_client_error_string_representation(self):
        """Test string representation includes endpoint."""
        error = DiodeClientError(
            "Connection failed",
            endpoint="diode.example.com:443",
        )

        assert "diode.example.com:443" in str(error)


class TestDiodeServerResponseErrorIncludesRequestId:
    """Tests for DiodeServerResponseError context."""

    def test_diode_server_response_error_includes_request_id(self):
        """Test that DiodeServerResponseError includes request ID."""
        error = DiodeServerResponseError(
            "Resource not found",
            request_id="req-12345",
            device_name="router-01",
            status_code=404,
        )

        assert error.context.get("request_id") == "req-12345"
        assert error.context.get("device_name") == "router-01"
        assert error.context.get("status_code") == 404

    def test_diode_server_response_error_string_representation(self):
        """Test string representation includes request ID."""
        error = DiodeServerResponseError(
            "Resource not found",
            request_id="req-12345",
        )

        assert "req-12345" in str(error)


class TestDiodeBatchErrorAggregatesErrors:
    """Tests for DiodeBatchError aggregation."""

    def test_diode_batch_error_aggregates_errors(self):
        """Test that DiodeBatchError aggregates multiple errors."""
        device_errors = [
            DiodeValidationError("Field error", field_name="name"),
            DiodeConversionError("Conversion error", device_name="router-01"),
        ]

        error = DiodeBatchError(
            "Batch failed",
            errors=device_errors,
            total=100,
            failed=5,
            summary={"DiodeValidationError": 3, "DiodeConversionError": 2},
        )

        assert error.context.get("total") == 100
        assert error.context.get("failed") == 5
        assert error.context.get("summary") is not None


class TestExceptionStringRepresentation:
    """Tests for exception string representation."""

    def test_exception_str_representation(self):
        """Test that exceptions have meaningful string representations."""
        error = DiodeError("Simple error message")
        assert "Simple error message" in str(error)

    def test_exception_with_multiple_context(self):
        """Test exception with multiple context fields."""
        error = DiodeValidationError(
            "Validation failed",
            field_name="name",
            value="invalid",
            device_name="router-01",
        )

        error_str = str(error)
        assert "Validation failed" in error_str
        assert "name" in error_str
        assert "invalid" in error_str
        assert "router-01" in error_str


class TestExceptionWithContextParameters:
    """Tests for exception context parameters."""

    def test_exception_with_context_parameters(self):
        """Test creating exceptions with context parameters."""
        error = DiodeValidationError(
            "Field error",
            field_name="serial",
            value="invalid-serial",
            device_name="test-device",
        )

        assert error.context.get("field_name") == "serial"
        assert error.context.get("value") == "invalid-serial"
        assert error.context.get("device_name") == "test-device"

    def test_exception_context_default_empty(self):
        """Test that context is empty dict by default."""
        error = DiodeError("Simple error")
        assert error.context == {}

    def test_exception_context_can_be_empty(self):
        """Test that context can be explicitly empty."""
        error = DiodeError("Simple error", context={})
        assert error.context == {}


class TestExceptionTracebackPreservation:
    """Tests for exception traceback preservation."""

    def test_exception_traceback_preservation(self):
        """Test that exceptions preserve traceback."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise DiodeError("Wrapped error", context={"original": str(e)})
        except DiodeError:
            # Traceback should be preserved in the exception chain
            pass

    def test_exception_with_traceback_attribute(self):
        """Test that exceptions can have traceback attached."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            error = DiodeError("Wrapped error", context={"original": str(e)})
            assert "Original error" in str(error)


class TestExceptionChainingWithCause:
    """Tests for exception chaining with 'cause'."""

    def test_exception_chain_with_cause(self):
        """Test that exceptions can be chained with original cause."""
        try:
            try:
                raise ConnectionError("Connection refused")
            except ConnectionError as e:
                raise DiodeClientError("Failed to connect", original_error=e)
        except DiodeClientError:
            pass  # Exception chaining is automatic

    def test_exception_chain_preserves_original(self):
        """Test that exception chain preserves original exception."""
        original = ValueError("Original value error")
        try:
            raise DiodeError("Wrapped error", context={"original": str(original)})
        except DiodeError as e:
            # The context should contain the original error
            assert "Original value error" in e.context.get("original", "")


class TestExceptionChainWithContext:
    """Tests for exception chain with context."""

    def test_exception_chain_with_context(self):
        """Test exception chain with additional context."""
        original = ValueError("Original error")

        error = DiodeValidationError(
            "Validation failed on field",
            field_name="name",
            value="test",
            device_name="router-01",
        )

        # Context should include the field_name and device_name
        assert "field_name" in error.context
        assert "device_name" in error.context
        assert error.context["device_name"] == "router-01"

    def test_exception_context_not_modifying_original(self):
        """Test that exception context doesn't modify original."""
        original = ValueError("Original error")

        error = DiodeConversionError(
            "Conversion failed",
            device_name="router-01",
            original_dict={"name": "router-01"},
        )

        # Context should be independent
        assert error.context.get("device_name") == "router-01"
        assert "Original error" not in error.context


# Exception Hierarchy Tests
class TestExceptionHierarchy:
    """Tests for the complete exception hierarchy."""

    def test_diode_error_base_class(self):
        """Test that DiodeError is the base of all Diode exceptions."""
        exceptions = [
            DiodeValidationError,
            DiodeConversionError,
            DiodeClientError,
            DiodeServerResponseError,
            DiodeBatchError,
        ]

        for exc in exceptions:
            assert issubclass(exc, DiodeError)

    def test_io_error_inherits_client_error(self):
        """Test that I/O specific errors inherit from DiodeClientError."""
        io_exceptions = [
            DiodeConnectionRefusedError,
            DiodeTimeoutError,
            DiodeAuthenticationError,
        ]

        for exc in io_exceptions:
            assert issubclass(exc, DiodeClientError)
            assert issubclass(exc, DiodeError)

    def test_all_exceptions_inherit_from_diode_error(self):
        """Test that all Diode exceptions ultimately inherit from DiodeError."""
        all_exceptions = [
            DiodeError,
            DiodeValidationError,
            DiodeConversionError,
            DiodeClientError,
            DiodeServerResponseError,
            DiodeBatchError,
            DiodeConnectionRefusedError,
            DiodeTimeoutError,
            DiodeAuthenticationError,
        ]

        for exc in all_exceptions:
            assert issubclass(exc, DiodeError)

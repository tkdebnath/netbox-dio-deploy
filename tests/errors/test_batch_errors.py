"""Tests for batch error aggregation.

Tests cover:
- DeviceError with traceback and context
- BatchResult error summary methods
- Process batch partial success
- Process batch all failures
- Batch error aggregation across chunks
"""

import pytest
from unittest.mock import Mock, patch

from netbox_dio import (
    BatchProcessor,
    BatchResult,
    DeviceError,
    DiodeBatchError,
)
from netbox_dio.models import DiodeDevice


class TestDeviceErrorWithTraceback:
    """Tests for DeviceError with traceback information."""

    def test_device_error_with_traceback(self):
        """Test creating DeviceError with traceback."""
        exc = ValueError("Test error")
        error = DeviceError.from_exception(
            device_name="router-01",
            exc=exc,
            original_dict={"name": "router-01"},
            stack_trace="Traceback (most recent call last):\n  File \"test.py\", line 1",
        )

        assert error.device_name == "router-01"
        assert "Test error" in error.error_message
        assert error.stack_trace is not None
        assert "test.py" in error.stack_trace

    def test_device_error_with_device_type(self):
        """Test creating DeviceError with device type."""
        exc = Exception("Conversion failed")
        error = DeviceError.from_exception(
            device_name="switch-01",
            exc=exc,
            original_dict={"name": "switch-01", "device_type": "cisco-9200"},
            device_type="cisco-9200",
        )

        assert error.device_type == "cisco-9200"
        assert error.device_name == "switch-01"

    def test_device_error_with_timing(self):
        """Test creating DeviceError with timing information."""
        exc = Exception("Timeout")
        error = DeviceError.from_exception(
            device_name="router-01",
            exc=exc,
            original_dict={"name": "router-01"},
            timing_ms=30000.5,
        )

        assert error.timing_ms is not None
        assert error.timing_ms == 30000.5

    def test_device_error_default_values(self):
        """Test DeviceError with default values."""
        exc = Exception("Error")
        error = DeviceError.from_exception(
            device_name="router-01",
            exc=exc,
            original_dict={"name": "router-01"},
        )

        assert error.stack_trace is None
        assert error.device_type is None
        assert error.timing_ms is None


class TestBatchResultErrorSummary:
    """Tests for BatchResult error summary methods."""

    def test_batch_result_error_summary(self):
        """Test getting error summary from BatchResult."""
        result = BatchResult(
            total=100,
            success=90,
            failed=10,
            errors=[
                DeviceError(
                    device_name=f"dev{i}",
                    error_message="Connection timeout",
                    original_dict={},
                )
                for i in range(10)
            ],
        )

        summary = result.get_error_summary()

        # Should have DeviceError in summary (the type of our error objects)
        assert len(summary) >= 1

    def test_batch_result_error_summary_multiple_types(self):
        """Test error summary with multiple error types."""
        errors = [
            DeviceError(device_name=f"dev{i}", error_message="Connection error", original_dict={})
            for i in range(5)
        ]
        errors.extend([
            DeviceError(device_name=f"dev{i}", error_message="Validation failed", original_dict={})
            for i in range(5, 10)
        ])

        result = BatchResult(
            total=10,
            success=0,
            failed=10,
            errors=errors,
        )

        summary = result.get_error_summary()

        # Check that summary has some entries
        assert len(summary) >= 1

    def test_batch_result_error_summary_empty(self):
        """Test error summary with no errors."""
        result = BatchResult(
            total=100,
            success=100,
            failed=0,
            errors=[],
        )

        summary = result.get_error_summary()
        assert len(summary) == 0

    def test_batch_result_get_failed_devices(self):
        """Test getting failed device names."""
        result = BatchResult(
            total=10,
            success=5,
            failed=5,
            errors=[
                DeviceError(device_name=f"dev{i}", error_message="Error", original_dict={})
                for i in range(5)
            ],
        )

        failed_devices = result.get_failed_devices()

        assert len(failed_devices) == 5
        assert "dev0" in failed_devices
        assert "dev4" in failed_devices

    def test_batch_result_get_failed_devices_empty(self):
        """Test getting failed device names with no errors."""
        result = BatchResult(
            total=100,
            success=100,
            failed=0,
            errors=[],
        )

        failed_devices = result.get_failed_devices()
        assert len(failed_devices) == 0


class TestProcessBatchPartialSuccess:
    """Tests for processing batch with partial success."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_batch_partial_success(self, mock_converter):
        """Test processing batch with some successes and failures."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        # Mock client
        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        # Create 10 devices
        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(10)
        ]

        # Mock converter to fail on some devices
        def converter_side_effect(device):
            if device.name in ["dev3", "dev7"]:
                raise Exception("Conversion failed")
            return [Mock()]

        mock_converter.side_effect = converter_side_effect

        result = processor.process_batch(client, devices)

        assert result.total == 10
        assert result.success == 8
        assert result.failed == 2
        assert len(result.errors) == 2
        assert result.has_errors() is True

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_single_chunk_partial_failure(self, mock_converter):
        """Test processing single chunk with partial failures."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(5)
        ]

        # Fail on dev2 only
        def converter_side_effect(device):
            if device.name == "dev2":
                raise Exception("Conversion failed")
            return [Mock()]

        mock_converter.side_effect = converter_side_effect

        result = processor.process_single_chunk(client, devices)

        assert result.total == 5
        assert result.success == 4
        assert result.failed == 1
        assert result.has_errors() is True


class TestProcessBatchAllFailures:
    """Tests for processing batch with all failures."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_batch_all_failures(self, mock_converter):
        """Test processing batch where all devices fail."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(20)
        ]

        mock_converter.side_effect = Exception("All conversions failed")

        result = processor.process_batch(client, devices)

        assert result.total == 20
        assert result.success == 0
        assert result.failed == 20
        assert result.has_errors() is True
        assert len(result.errors) == 20


class TestBatchErrorAggregation:
    """Tests for batch error aggregation across chunks."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_batch_error_aggregation(self, mock_converter):
        """Test that errors are properly aggregated across chunks."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=10)  # Small chunks for testing
        client = DiodeClient(config)

        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        # Create 25 devices (3 chunks: 10, 10, 5)
        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(25)
        ]

        # Fail on specific devices across chunks
        def converter_side_effect(device):
            if device.name in ["dev3", "dev12", "dev20"]:
                raise Exception(f"Failed on {device.name}")
            return [Mock()]

        mock_converter.side_effect = converter_side_effect

        result = processor.process_batch(client, devices)

        # Verify all chunks were processed
        assert result.total == 25
        assert result.failed == 3
        assert len(result.errors) == 3

        # Verify errors are for the right devices
        failed_names = [e.device_name for e in result.errors]
        assert "dev3" in failed_names
        assert "dev12" in failed_names
        assert "dev20" in failed_names

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_batch_error_with_timing(self, mock_converter):
        """Test that timing information is captured in the batch result."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=10)
        client = DiodeClient(config)

        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(5)
        ]

        mock_converter.side_effect = Exception("Timeout")

        result = processor.process_single_chunk(client, devices)

        # Check timing was captured at the batch level
        assert result.timing_ms is not None
        assert result.timing_ms > 0

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_batch_error_with_device_type(self, mock_converter):
        """Test that device type is captured in errors."""
        from netbox_dio import DiodeClient, ConnectionConfig

        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=10)
        client = DiodeClient(config)

        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        devices = [
            DiodeDevice(name="dev1", site="site-a", device_type="cisco-9300", role="core-router"),
            DiodeDevice(name="dev2", site="site-a", device_type="cisco-9200", role="access-switch"),
        ]

        mock_converter.side_effect = Exception("Conversion failed")

        result = processor.process_single_chunk(client, devices)

        # Check device types were captured
        dev1_error = next(e for e in result.errors if e.device_name == "dev1")
        dev2_error = next(e for e in result.errors if e.device_name == "dev2")

        # Device types should be captured from the original dict
        assert dev1_error.device_type == "cisco-9300"
        assert dev2_error.device_type == "cisco-9200"


class TestBatchResultHasErrors:
    """Tests for BatchResult.has_errors() method."""

    def test_has_errors_true(self):
        """Test has_errors returns True when there are errors."""
        result = BatchResult(
            total=100,
            success=90,
            failed=10,
            errors=[DeviceError(device_name="dev1", error_message="Error", original_dict={})],
        )

        assert result.has_errors() is True

    def test_has_errors_false(self):
        """Test has_errors returns False when no errors."""
        result = BatchResult(
            total=100,
            success=100,
            failed=0,
            errors=[],
        )

        assert result.has_errors() is False

    def test_has_errors_empty_result(self):
        """Test has_errors with zero devices."""
        result = BatchResult(
            total=0,
            success=0,
            failed=0,
            errors=[],
        )

        assert result.has_errors() is False


class TestDeviceErrorFromException:
    """Tests for DeviceError.from_exception() method."""

    def test_from_exception_with_context(self):
        """Test creating DeviceError from exception with context."""
        exc = Exception("Network error")
        original_dict = {"name": "router-01", "site": "site-a"}

        error = DeviceError.from_exception(
            device_name="router-01",
            exc=exc,
            original_dict=original_dict,
        )

        assert error.device_name == "router-01"
        assert "Network error" in error.error_message
        assert error.original_dict == original_dict

    def test_from_exception_without_original_dict(self):
        """Test creating DeviceError from exception without original dict."""
        exc = Exception("Conversion failed")

        error = DeviceError.from_exception(
            device_name="switch-01",
            exc=exc,
            original_dict={},
        )

        assert error.device_name == "switch-01"
        assert error.original_dict == {}

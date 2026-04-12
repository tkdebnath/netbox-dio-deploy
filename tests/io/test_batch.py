"""Tests for BatchProcessor and batch operations.

Tests cover:
- Chunking with <1000 devices (no split)
- Chunking with 1000 devices (exact)
- Chunking with 1500 devices (2 chunks)
- Chunking with 2500 devices (3 chunks)
- Single chunk processing success
- Single chunk processing partial failure
- Full batch processing with errors
- create_message_chunks() with various sizes
- Error aggregation in BatchResult
- Per-device error reporting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from netbox_dio import (
    DiodeClient,
    ConnectionConfig,
    BatchProcessor,
    BatchResult,
    DeviceError,
    create_message_chunks,
)
from netbox_dio.models import DiodeDevice


class TestBatchProcessorChunking:
    """Tests for BatchProcessor chunking functionality."""

    def test_chunk_devices_under_limit(self):
        """Test chunking with fewer devices than limit."""
        processor = BatchProcessor(max_chunk_size=100)

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(50)
        ]

        chunks = processor.chunk_devices(devices)

        assert len(chunks) == 1
        assert len(chunks[0]) == 50

    def test_chunk_devices_over_limit(self):
        """Test chunking with more devices than limit."""
        processor = BatchProcessor(max_chunk_size=100)

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(250)
        ]

        chunks = processor.chunk_devices(devices)

        assert len(chunks) == 3
        assert len(chunks[0]) == 100
        assert len(chunks[1]) == 100
        assert len(chunks[2]) == 50

    def test_chunk_devices_exact_limit(self):
        """Test chunking with exactly the limit."""
        processor = BatchProcessor(max_chunk_size=100)

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(100)
        ]

        chunks = processor.chunk_devices(devices)

        assert len(chunks) == 1
        assert len(chunks[0]) == 100

    def test_chunk_devices_multiple_chunks(self):
        """Test chunking with multiple full chunks."""
        processor = BatchProcessor(max_chunk_size=1000)

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(2500)
        ]

        chunks = processor.chunk_devices(devices)

        assert len(chunks) == 3
        assert len(chunks[0]) == 1000
        assert len(chunks[1]) == 1000
        assert len(chunks[2]) == 500

    def test_chunk_devices_empty_list(self):
        """Test chunking with empty list."""
        processor = BatchProcessor(max_chunk_size=100)

        chunks = processor.chunk_devices([])

        assert len(chunks) == 0

    def test_chunk_devices_single_device(self):
        """Test chunking with single device."""
        processor = BatchProcessor(max_chunk_size=100)

        devices = [DiodeDevice(name="dev0", site="site-a", device_type="cisco-9300", role="core-router")]

        chunks = processor.chunk_devices(devices)

        assert len(chunks) == 1
        assert len(chunks[0]) == 1


class TestBatchProcessorInitialization:
    """Tests for BatchProcessor initialization."""

    def test_processor_default_chunk_size(self):
        """Test default chunk size of 1000."""
        processor = BatchProcessor()

        assert processor.max_chunk_size == 1000

    def test_processor_custom_chunk_size(self):
        """Test custom chunk size."""
        processor = BatchProcessor(max_chunk_size=500)

        assert processor.max_chunk_size == 500

    def test_processor_invalid_chunk_size_zero(self):
        """Test that zero chunk size raises ValueError."""
        with pytest.raises(ValueError, match="must be between 1 and 1000"):
            BatchProcessor(max_chunk_size=0)

    def test_processor_invalid_chunk_size_negative(self):
        """Test that negative chunk size raises ValueError."""
        with pytest.raises(ValueError, match="must be between 1 and 1000"):
            BatchProcessor(max_chunk_size=-100)

    def test_processor_invalid_chunk_size_over_limit(self):
        """Test that chunk size over 1000 raises ValueError."""
        with pytest.raises(ValueError, match="must be between 1 and 1000"):
            BatchProcessor(max_chunk_size=2000)

    def test_processor_chunk_size_boundary(self):
        """Test chunk sizes at boundaries."""
        processor1 = BatchProcessor(max_chunk_size=1)
        assert processor1.max_chunk_size == 1

        processor1000 = BatchProcessor(max_chunk_size=1000)
        assert processor1000.max_chunk_size == 1000


class TestBatchProcessorProcessSingleChunk:
    """Tests for process_single_chunk method."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_single_chunk_success(self, mock_converter):
        """Test processing single chunk with all successes."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        # Mock the client's ingest method and mark as connected
        client._client = Mock()
        client._client.ingest = Mock(return_value=None)
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(50)
        ]

        mock_converter.return_value = [[Mock()]]

        result = processor.process_single_chunk(client, devices)

        assert result.total == 50
        assert result.success == 50
        assert result.failed == 0
        assert len(result.errors) == 0

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_single_chunk_partial_failure(self, mock_converter):
        """Test processing single chunk with some failures."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        # Mock the client's ingest method to fail on certain calls
        mock_ingester = Mock()
        call_count = [0]

        def ingest_side_effect(entities):
            call_count[0] += 1
            if call_count[0] <= 2:
                return None
            else:
                raise Exception("Ingestion failed")

        mock_ingester.ingest = Mock(side_effect=ingest_side_effect)
        client._client = mock_ingester
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(3)
        ]

        mock_converter.return_value = [[Mock()]]

        result = processor.process_single_chunk(client, devices)

        assert result.total == 3
        assert result.success == 2
        assert result.failed == 1
        assert len(result.errors) == 1

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_single_chunk_conversion_failure(self, mock_converter):
        """Test processing single chunk with conversion failure."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(3)
        ]

        mock_converter.side_effect = Exception("Conversion failed")

        result = processor.process_single_chunk(client, devices)

        assert result.total == 3
        assert result.success == 0
        assert result.failed == 3
        assert len(result.errors) == 3

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_single_chunk_error_aggregation(self, mock_converter):
        """Test that errors are properly aggregated."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        mock_ingester = Mock()
        mock_ingester.ingest.side_effect = Exception("Ingestion failed")
        client._client = mock_ingester
        client._connected = True

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(3)
        ]

        mock_converter.return_value = [[Mock()]]

        result = processor.process_single_chunk(client, devices)

        assert len(result.errors) == 3

        for i, error in enumerate(result.errors):
            assert error.device_name == f"dev{i}"
            assert "Ingestion failed" in error.error_message


class TestBatchProcessorProcessBatch:
    """Tests for process_batch method."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_batch_multiple_chunks(self, mock_converter):
        """Test processing batch across multiple chunks."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        mock_ingester = Mock()
        mock_ingester.ingest = Mock(return_value=None)
        client._client = mock_ingester
        client._connected = True

        # 250 devices = 3 chunks (100, 100, 50)
        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(250)
        ]

        mock_converter.return_value = [[Mock()]]

        result = processor.process_batch(client, devices)

        assert result.total == 250
        assert result.success == 250
        assert result.failed == 0

        # Verify ingest was called 250 times (once per device)
        assert mock_ingester.ingest.call_count == 250

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_process_batch_with_errors_accumulated(self, mock_converter):
        """Test that errors accumulate across chunks."""
        config = ConnectionConfig(endpoint="diode.example.com:443")
        processor = BatchProcessor(max_chunk_size=100)
        client = DiodeClient(config)

        mock_ingester = Mock()
        mock_ingester.ingest.side_effect = Exception("Ingestion failed")
        client._client = mock_ingester
        client._connected = True

        # 250 devices = 3 chunks
        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(250)
        ]

        mock_converter.return_value = [[Mock()]]

        result = processor.process_batch(client, devices)

        assert result.total == 250
        assert result.failed == 250
        assert len(result.errors) == 250


class TestBatchResult:
    """Tests for BatchResult class."""

    def test_result_creation(self):
        """Test creating a BatchResult."""
        result = BatchResult(
            total=100,
            success=90,
            failed=10,
            errors=[],
        )

        assert result.total == 100
        assert result.success == 90
        assert result.failed == 10
        assert len(result.errors) == 0

    def test_result_counts_validation(self):
        """Test that BatchResult validates counts."""
        with pytest.raises(ValueError, match="must equal total"):
            BatchResult(
                total=100,
                success=50,
                failed=25,
                errors=[],
            )

    def test_result_errors_list(self):
        """Test that errors list is mutable."""
        result = BatchResult(
            total=100,
            success=90,
            failed=10,
            errors=[],
        )

        result.errors.append(DeviceError(
            device_name="dev1",
            error_message="Test error",
            original_dict={},
        ))

        assert len(result.errors) == 1


class TestDeviceError:
    """Tests for DeviceError class."""

    def test_error_creation(self):
        """Test creating a DeviceError."""
        error = DeviceError(
            device_name="test-device",
            error_message="Connection timeout",
            original_dict={"name": "test-device"},
        )

        assert error.device_name == "test-device"
        assert error.error_message == "Connection timeout"
        assert error.original_dict == {"name": "test-device"}

    def test_error_from_exception(self):
        """Test creating DeviceError from exception."""
        exc = Exception("Network error occurred")

        error = DeviceError.from_exception(
            device_name="test-device",
            exc=exc,
            original_dict={"name": "test-device"},
        )

        assert error.device_name == "test-device"
        assert "Network error occurred" in error.error_message
        assert error.original_dict == {"name": "test-device"}


class TestCreateMessageChunks:
    """Tests for create_message_chunks function."""

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_create_message_chunks_basic(self, mock_converter):
        """Test basic message chunk creation."""
        mock_converter.return_value = [[Mock()]]

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(1500)
        ]

        chunks = create_message_chunks(devices)

        assert len(chunks) == 2
        assert chunks[0][0] == 1
        assert len(chunks[0][1]) == 1000
        assert chunks[1][0] == 2
        assert len(chunks[1][1]) == 500

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_create_message_chunks_under_limit(self, mock_converter):
        """Test message chunk creation under 1000 devices."""
        mock_converter.return_value = [[Mock()]]

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(500)
        ]

        chunks = create_message_chunks(devices)

        assert len(chunks) == 1
        assert chunks[0][0] == 1
        assert len(chunks[0][1]) == 500

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_create_message_chunks_exact_limit(self, mock_converter):
        """Test message chunk creation at exactly 1000 devices."""
        mock_converter.return_value = [[Mock()]]

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(1000)
        ]

        chunks = create_message_chunks(devices)

        assert len(chunks) == 1
        assert chunks[0][0] == 1
        assert len(chunks[0][1]) == 1000

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_create_message_chunks_over_limit(self, mock_converter):
        """Test message chunk creation over 1000 devices."""
        mock_converter.return_value = [[Mock()]]

        devices = [
            DiodeDevice(name=f"dev{i}", site="site-a", device_type="cisco-9300", role="core-router")
            for i in range(2500)
        ]

        chunks = create_message_chunks(devices)

        assert len(chunks) == 3
        assert chunks[0][0] == 1
        assert len(chunks[0][1]) == 1000
        assert chunks[1][0] == 2
        assert len(chunks[1][1]) == 1000
        assert chunks[2][0] == 3
        assert len(chunks[2][1]) == 500

    @patch("netbox_dio.batch.convert_device_to_entities")
    def test_create_message_chunks_empty(self, mock_converter):
        """Test message chunk creation with empty list."""
        mock_converter.return_value = [[Mock()]]

        devices = []

        chunks = create_message_chunks(devices)

        assert len(chunks) == 0

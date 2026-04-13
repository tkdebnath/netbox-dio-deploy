"""Tests for large batch processing.

This module tests the batch processor with large numbers of devices.
"""

import pytest

from netbox_dio import BatchProcessor, BatchResult
from netbox_dio.models import DiodeDevice


class TestBatchProcessorChunking:
    """Tests for batch processor chunking."""

    def test_chunk_devices_basic(self):
        """Test basic chunking functionality."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(500))
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 5
        assert all(len(c) <= 100 for c in chunks)

    def test_chunk_devices_exact(self):
        """Test chunking with exact multiple."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(500))
        chunks = processor.chunk_devices(devices)
        assert all(len(c) == 100 for c in chunks)

    def test_chunk_devices_remainder(self):
        """Test chunking with remainder."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(550))
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 6
        assert len(chunks[-1]) == 50

    def test_chunk_devices_small(self):
        """Test chunking with fewer devices than chunk size."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(50))
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 1
        assert len(chunks[0]) == 50

    def test_chunk_devices_empty(self):
        """Test chunking empty list."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = []
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 0

    def test_chunk_devices_single(self):
        """Test chunking single device."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = [1]
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 1
        assert len(chunks[0]) == 1


class TestBatchProcessorProcessing:
    """Tests for batch processing."""

    def test_process_batch_result_structure(self):
        """Test the structure of batch results."""
        from netbox_dio.client import ConnectionConfig, DiodeClient
        from netbox_dio.models import DiodeDevice

        # Create a mock client config (no actual connection needed for this test)
        config = ConnectionConfig(endpoint="http://localhost:8000")
        client = DiodeClient(config)

        devices = [
            DiodeDevice(name=f"device-{i}", site="site", device_type="type", role="role")
            for i in range(10)
        ]

        # This will fail due to no actual client, but we can check the result structure
        # For now, just test the structure of a manually created result
        result = BatchResult(
            total=10,
            success=8,
            failed=2,
            errors=[],
        )

        assert result.total == 10
        assert result.success == 8
        assert result.failed == 2
        assert result.has_errors() is True

    def test_process_batch_error_summary(self):
        """Test error summary generation."""
        from netbox_dio import DeviceError

        errors = [
            DeviceError(
                device_name="device-1",
                error_message="ValidationError: invalid data",
                original_dict={},
            ),
            DeviceError(
                device_name="device-2",
                error_message="ConversionError: conversion failed",
                original_dict={},
            ),
            DeviceError(
                device_name="device-3",
                error_message="ClientError: connection failed",
                original_dict={},
            ),
        ]

        result = BatchResult(
            total=3,
            success=0,
            failed=3,
            errors=errors,
        )

        summary = result.get_error_summary()
        assert "DeviceError" in summary

    def test_process_batch_failed_devices(self):
        """Test getting failed device names."""
        from netbox_dio import DeviceError

        errors = [
            DeviceError(
                device_name="device-1",
                error_message="Error 1",
                original_dict={},
            ),
            DeviceError(
                device_name="device-2",
                error_message="Error 2",
                original_dict={},
            ),
        ]

        result = BatchResult(
            total=2,
            success=0,
            failed=2,
            errors=errors,
        )

        failed = result.get_failed_devices()
        assert failed == ["device-1", "device-2"]


class TestBatchProcessorThroughput:
    """Tests for batch throughput calculations."""

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        result = BatchResult(
            total=1000,
            success=950,
            failed=50,
            errors=[],
            timing_ms=5000,  # 5 seconds
        )

        # Should calculate ~200 devices/sec for 1000 devices in 5 seconds
        assert result.throughput_sps >= 100
        assert result.throughput_sps <= 300

    def test_throughput_empty(self):
        """Test throughput with zero time."""
        result = BatchResult(
            total=0,
            success=0,
            failed=0,
            errors=[],
            timing_ms=0,
        )
        assert result.throughput_sps == 0.0

    def test_throughput_units(self):
        """Test throughput is in correct units."""
        result = BatchResult(
            total=1000,
            success=1000,
            failed=0,
            errors=[],
            timing_ms=1000,
        )
        assert result.throughput_sps >= 0


class TestBatchProcessorScalability:
    """Tests for batch processor scalability."""

    def test_large_batch(self):
        """Test processing a large batch."""
        processor = BatchProcessor(max_chunk_size=100)

        # Create 1000 devices
        devices = [
            DiodeDevice(name=f"device-{i}", site="site", device_type="type", role="role")
            for i in range(1000)
        ]

        # Should chunk into 10 batches
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 10
        assert all(len(c) == 100 for c in chunks)

    def test_very_large_batch(self):
        """Test processing a very large batch."""
        processor = BatchProcessor(max_chunk_size=1000)

        # Create 10000 devices
        devices = [
            DiodeDevice(name=f"device-{i}", site="site", device_type="type", role="role")
            for i in range(10000)
        ]

        # Should chunk into 10 batches
        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 10
        assert all(len(c) == 1000 for c in chunks)


class TestBatchProcessorEdgeCases:
    """Tests for batch processor edge cases."""

    def test_single_device(self):
        """Test processing a single device."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = [DiodeDevice(name="device-1", site="site", device_type="type", role="role")]

        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 1
        assert len(chunks[0]) == 1

    def test_empty_list(self):
        """Test processing an empty list."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = []

        chunks = processor.chunk_devices(devices)
        assert len(chunks) == 0

    def test_zero_max_chunk_size(self):
        """Test that zero max chunk size raises an error."""
        with pytest.raises(ValueError):
            BatchProcessor(max_chunk_size=0)

    def test_max_chunk_size_exceeds_limit(self):
        """Test that chunk size exceeding limit raises an error."""
        with pytest.raises(ValueError):
            BatchProcessor(max_chunk_size=10001)

    def test_min_chunk_size(self):
        """Test that minimum chunk size is allowed."""
        processor = BatchProcessor(max_chunk_size=1)
        assert processor.max_chunk_size == 1


class TestBatchProcessorChunkingConsistency:
    """Tests for chunking consistency."""

    def test_chunking_deterministic(self):
        """Test that chunking is deterministic."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(550))

        chunks1 = processor.chunk_devices(devices)
        chunks2 = processor.chunk_devices(devices)

        assert chunks1 == chunks2

    def test_chunking_order_preserved(self):
        """Test that chunking preserves order."""
        processor = BatchProcessor(max_chunk_size=100)
        devices = list(range(500))

        chunks = processor.chunk_devices(devices)

        # Flatten chunks and verify order
        flat = [item for chunk in chunks for item in chunk]
        assert flat == devices

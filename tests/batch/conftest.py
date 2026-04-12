"""Pytest fixtures for batch testing.

This module provides pytest fixtures for testing the batch processing system.
"""

import pytest

from netbox_dio import BatchProcessor, BatchResult, DeviceError


@pytest.fixture
def batch_processor():
    """Create a batch processor for testing.

    Returns:
        BatchProcessor instance
    """
    return BatchProcessor(max_chunk_size=100)


@pytest.fixture
def progress_manager():
    """Create a mock progress manager for testing.

    Returns:
        MockProgressManager instance
    """
    from netbox_dio.progress import MockProgressManager
    return MockProgressManager(total=1000, description="Test")


@pytest.fixture
def sample_devices():
    """Create a list of sample devices for testing.

    Returns:
        List of DiodeDevice instances
    """
    from netbox_dio.models import DiodeDevice
    return [
        DiodeDevice(name="device-01", site="site-a", device_type="type-1", role="role-1"),
        DiodeDevice(name="device-02", site="site-b", device_type="type-2", role="role-2"),
        DiodeDevice(name="device-03", site="site-c", device_type="type-3", role="role-3"),
    ]

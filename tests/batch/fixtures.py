"""Shared test fixtures for batch operations.

This module provides common test data structures for testing the batch
processing system.
"""

from netbox_dio.models import DiodeDevice


def large_device_list(n: int = 100):
    """Generate a list of n devices for testing.

    Args:
        n: Number of devices to generate

    Returns:
        List of DiodeDevice instances
    """
    devices = []
    for i in range(n):
        devices.append(
            DiodeDevice(
                name=f"device-{i}",
                site=f"site-{i % 5}",
                device_type=f"type-{i % 3}",
                role=f"role-{i % 2}",
            )
        )
    return devices


def progress_manager_mock():
    """Create a mock progress manager for testing.

    Returns:
        MockProgressManager instance
    """
    from netbox_dio.progress import MockProgressManager
    return MockProgressManager(total=1000, description="Test")


def batch_processor_mock():
    """Create a batch processor for testing.

    Returns:
        BatchProcessor instance
    """
    from netbox_dio import BatchProcessor
    return BatchProcessor(max_chunk_size=100)


def create_test_device(i: int) -> DiodeDevice:
    """Create a single test device.

    Args:
        i: Device index

    Returns:
        DiodeDevice instance
    """
    return DiodeDevice(
        name=f"device-{i}",
        site=f"site-{i % 5}",
        device_type=f"type-{i % 3}",
        role=f"role-{i % 2}",
        serial=f"SN-{i:05d}",
        asset_tag=f"AT-{i:05d}",
        platform="Cisco IOS XE",
        status="active",
    )


def create_test_device_list(n: int) -> list:
    """Create a list of test devices.

    Args:
        n: Number of devices

    Returns:
        List of DiodeDevice instances
    """
    return [create_test_device(i) for i in range(n)]


def create_device_with_errors(i: int) -> DiodeDevice:
    """Create a test device with potential issues.

    Args:
        i: Device index

    Returns:
        DiodeDevice instance
    """
    # Every 10th device has an issue
    if i % 10 == 0:
        return DiodeDevice(
            name=f"device-{i}",
            site=f"site-{i % 5}",
            device_type=None,  # Invalid: missing device_type
            role=f"role-{i % 2}",
        )
    return DiodeDevice(
        name=f"device-{i}",
        site=f"site-{i % 5}",
        device_type=f"type-{i % 3}",
        role=f"role-{i % 2}",
    )

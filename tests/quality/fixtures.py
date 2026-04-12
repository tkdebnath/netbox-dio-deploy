"""Shared test fixtures for quality metrics scenarios.

This module provides common test data structures for testing the quality
metrics system.
"""

import pytest

from netbox_dio.models import DiodeDevice


def complete_device_data():
    """Create a device with all fields populated.

    Returns:
        DiodeDevice instance with complete data
    """
    return DiodeDevice(
        name="router-01",
        site="site-a",
        device_type="cisco-9300",
        role="core-router",
        serial="SN123456789",
        asset_tag="AT-001",
        platform="Cisco IOS XE",
        status="active",
        custom_fields={"location": "rack-a1", "owner": "network-team"},
    )


def incomplete_device_data():
    """Create a device with some fields missing.

    Returns:
        DiodeDevice instance with missing fields
    """
    return DiodeDevice(
        name="router-02",
        site="site-b",
        device_type="arista-7280",
        role="spine-router",
    )


def invalid_device_data():
    """Create a device with validation errors.

    Returns:
        DiodeDevice instance with invalid data
    """
    return DiodeDevice(
        name="router-03",
        site="site-c",
        device_type="cisco-9300",
        role="core-router",
        status="invalid_status",
    )


def mixed_quality_device():
    """Create a device with mixed quality.

    Returns:
        DiodeDevice instance with some good and some bad fields
    """
    return DiodeDevice(
        name="router-04",
        site="site-d",
        device_type="paloalto-firewall",
        role="edge-firewall",
        serial="SN987654321",
        asset_tag=None,  # Missing
        platform=None,  # Missing
        status="active",
    )


def high_value_device():
    """Create a high-value device for testing.

    Returns:
        DiodeDevice instance with premium configuration
    """
    return DiodeDevice(
        name="premium-router",
        site="dc-primary",
        device_type="cisco-nexus-9000",
        role="spine-router",
        serial="PREM-SN-001",
        asset_tag="PREM-AT-001",
        platform="Nexus OS",
        status="active",
        custom_fields={
            "rack": "A1",
            "u_position": 1,
            "power_cycle": True,
            "warranty_end": "2027-01-15",
        },
    )


def low_value_device():
    """Create a low-value device for testing.

    Returns:
        DiodeDevice instance with minimal configuration
    """
    return DiodeDevice(
        name="budget-switch",
        site="branch-office",
        device_type="arista-leaves",
        role="access-switch",
    )


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

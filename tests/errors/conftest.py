# Pytest fixtures for error handling tests
# This file provides shared test data for all error handling tests

import pytest


@pytest.fixture
def sample_device_dict():
    """Returns a valid sample device dictionary for error testing."""
    return {
        "name": "test-device",
        "site": "test-site",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "SN12345",
        "asset_tag": "AT-001",
        "platform": "Cisco IOS XE",
        "status": "active",
    }


@pytest.fixture
def invalid_device_dict():
    """Returns a device dictionary with missing required fields."""
    return {
        "name": "incomplete-device",
    }


@pytest.fixture
def device_with_bad_status():
    """Returns a device dictionary with invalid status."""
    return {
        "name": "bad-status-device",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "status": "invalid_status",
    }


@pytest.fixture
def batch_of_devices():
    """Returns 1500 devices for batch error testing."""
    devices = []

    # 1000 basic devices
    for i in range(1000):
        devices.append({
            "name": f"device-{i:04d}",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        })

    # 500 devices with interfaces
    for i in range(1000, 1500):
        devices.append({
            "name": f"device-interface-{i:04d}",
            "site": "site-b",
            "device_type": "cisco-9200",
            "role": "access-switch",
            "interfaces": [
                {
                    "name": f"eth0-{i}",
                    "device": f"device-interface-{i:04d}",
                    "type": "physical",
                }
            ],
        })

    return devices


@pytest.fixture
def error_fixture_data():
    """Returns data for various error scenarios."""
    return {
        "validation_errors": [
            {"name": "missing_required", "data": {"name": "test"}},
            {"name": "invalid_status", "data": {"name": "test", "status": "bad"}},
            {"name": "empty_name", "data": {"name": "", "site": "s"}},
        ],
        "conversion_errors": [
            {"name": "device_conversion", "device_name": "router-01"},
            {"name": "interface_conversion", "interface_name": "eth0"},
        ],
        "io_errors": [
            {"name": "connection_refused", "endpoint": "diode.example.com:443"},
            {"name": "timeout", "endpoint": "diode.example.com:443"},
        ],
    }

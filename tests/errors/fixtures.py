"""Test fixtures for error handling scenarios.

This module provides test fixtures for various error scenarios including
invalid device data, conversion failures, and batch processing errors.
"""

import pytest


@pytest.fixture
def invalid_device_dicts():
    """Returns a list of dicts with various invalid data for testing.

    Each dict has a 'name' describing the error type and 'data' containing
    the invalid device data.
    """
    return [
        {
            "name": "missing_required_field",
            "data": {"name": "test-device"},
            "error_field": "site",
        },
        {
            "name": "invalid_status",
            "data": {
                "name": "test-device",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "invalid_status",
            },
            "error_field": "status",
        },
        {
            "name": "empty_name",
            "data": {
                "name": "",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
            },
            "error_field": "name",
        },
        {
            "name": "name_too_long",
            "data": {
                "name": "a" * 100,
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
            },
            "error_field": "name",
        },
        {
            "name": "name_too_short",
            "data": {
                "name": "a",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
            },
            "error_field": "name",
        },
        {
            "name": "invalid_serial",
            "data": {
                "name": "test-device",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "serial": "SN" * 100,
            },
            "error_field": "serial",
        },
    ]


@pytest.fixture
def error_scenarios():
    """Returns test scenarios for each exception type.

    Each scenario includes:
    - name: Description of the scenario
    - exception: The exception class to test
    - error_data: Data needed to trigger the exception
    - expected_fields: Fields expected in the exception context
    """
    return [
        {
            "name": "validation_missing_required",
            "exception": "DiodeValidationError",
            "error_data": {"name": "test"},
            "expected_fields": ["field_name", "device_name"],
        },
        {
            "name": "validation_invalid_status",
            "exception": "DiodeValidationError",
            "error_data": {
                "name": "router-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "bad_value",
            },
            "expected_fields": ["field_name", "value", "device_name"],
        },
        {
            "name": "conversion_device_failure",
            "exception": "DiodeConversionError",
            "error_data": {"device_name": "router-01", "conversion_type": "device"},
            "expected_fields": ["device_name", "conversion_type"],
        },
        {
            "name": "conversion_interface_failure",
            "exception": "DiodeConversionError",
            "error_data": {"device_name": "router-01", "conversion_type": "interface"},
            "expected_fields": ["device_name", "conversion_type"],
        },
        {
            "name": "client_connection_refused",
            "exception": "DiodeConnectionRefusedError",
            "error_data": {"endpoint": "diode.example.com:443"},
            "expected_fields": ["endpoint"],
        },
        {
            "name": "client_timeout",
            "exception": "DiodeTimeoutError",
            "error_data": {"endpoint": "diode.example.com:443", "timeout": 30.0},
            "expected_fields": ["endpoint"],
        },
        {
            "name": "client_auth_failure",
            "exception": "DiodeAuthenticationError",
            "error_data": {
                "message": "Invalid credentials",
                "endpoint": "diode.example.com:443",
            },
            "expected_fields": ["endpoint"],
        },
        {
            "name": "server_response_error",
            "exception": "DiodeServerResponseError",
            "error_data": {
                "message": "Resource not found",
                "request_id": "req-12345",
                "device_name": "router-01",
            },
            "expected_fields": ["request_id", "device_name", "status_code"],
        },
        {
            "name": "batch_aggregated_errors",
            "exception": "DiodeBatchError",
            "error_data": {
                "total": 100,
                "failed": 5,
                "summary": {"DiodeValidationError": 3, "DiodeClientError": 2},
            },
            "expected_fields": ["total", "failed", "summary"],
        },
    ]


@pytest.fixture
def batch_error_fixtures():
    """Returns fixtures for batch error testing.

    Includes:
    - single_error: One failed device
    - partial_success: Mix of success and failure
    - all_failures: All devices fail
    - multiple_error_types: Different error types
    """
    return {
        "single_error": {
            "devices": 50,
            "successful": 49,
            "failed": 1,
            "error_type": "DiodeClientError",
        },
        "partial_success": {
            "devices": 100,
            "successful": 75,
            "failed": 25,
            "error_type": "DiodeValidationError",
        },
        "all_failures": {
            "devices": 500,
            "successful": 0,
            "failed": 500,
            "error_type": "DiodeClientError",
        },
        "multiple_error_types": {
            "devices": 100,
            "error_types": {
                "DiodeValidationError": 30,
                "DiodeConversionError": 20,
                "DiodeClientError": 50,
            },
        },
    }


@pytest.fixture
def sample_device_dict():
    """Returns a valid sample device dictionary."""
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
def device_with_interfaces():
    """Returns a device dictionary with interfaces."""
    return {
        "name": "network-device",
        "site": "main-datacenter",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "SN67890",
        "interfaces": [
            {
                "name": "eth0",
                "device": "network-device",
                "type": "physical",
                "label": "Main Interface",
                "enabled": True,
                "speed": 10000,
                "duplex": "full",
            },
            {
                "name": "eth1",
                "device": "network-device",
                "type": "physical",
                "label": "Backup Interface",
                "enabled": False,
            },
        ],
    }


@pytest.fixture
def device_with_vlans():
    """Returns a device dictionary with VLANs."""
    return {
        "name": "vlan-device",
        "site": "main-datacenter",
        "device_type": "cisco-9300",
        "role": "core-router",
        "vlans": [
            {
                "name": "management",
                "vid": 100,
                "site": "main-datacenter",
                "status": "active",
                "role": "access",
            },
            {
                "name": "data",
                "vid": 200,
                "site": "main-datacenter",
                "status": "active",
                "role": "distribution",
            },
        ],
    }


@pytest.fixture
def large_batch_devices():
    """Returns a list of 1500 device dictionaries for batch testing."""
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
            "name": f"device-with-interface-{i:04d}",
            "site": "site-b",
            "device_type": "cisco-9200",
            "role": "access-switch",
            "interfaces": [
                {
                    "name": f"eth0-{i}",
                    "device": f"device-with-interface-{i:04d}",
                    "type": "physical",
                }
            ],
        })

    return devices

"""Shared test fixtures for validation scenarios.

This module provides common test data structures for testing the validation
framework and built-in rules.
"""

import pytest

from netbox_dio.models import DiodeDevice


def device_with_all_fields():
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
    )


def device_with_all_fields_dict():
    """Create a device dict with all fields populated.

    Returns:
        Dictionary with complete device data
    """
    return {
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "SN123456789",
        "asset_tag": "AT-001",
        "platform": "Cisco IOS XE",
        "status": "active",
        "custom_fields": {"location": "rack-a1", "owner": "network-team"},
    }


def device_missing_required():
    """Create a device missing required fields.

    Returns:
        Dictionary missing required fields
    """
    return {
        "name": "router-02",
        "device_type": "cisco-9300",
        "role": "core-router",
    }


def device_with_invalid_status():
    """Create a device with an invalid status value.

    Returns:
        Dictionary with invalid status
    """
    return {
        "name": "router-03",
        "site": "site-b",
        "device_type": "cisco-9300",
        "role": "distribution-router",
        "status": "maintenance",
    }


def device_with_long_name():
    """Create a device with a name exceeding 64 characters.

    Returns:
        Dictionary with long name
    """
    return {
        "name": "this-is-a-very-long-device-name-that-exceeds-the-maximum-length-of-64-characters",
        "site": "site-c",
        "device_type": "cisco-9300",
        "role": "access-switch",
    }


def device_with_custom_fields():
    """Create a device with custom fields.

    Returns:
        Dictionary with custom fields
    """
    return {
        "name": "router-04",
        "site": "site-d",
        "device_type": "arista-7280",
        "role": "spine-router",
        "custom_fields": {
            "datacenter": "dc1",
            "rack": "a1",
            "u_position": 1,
            "power_cycle": True,
        },
    }


def device_with_short_serial():
    """Create a device with an empty serial number.

    Returns:
        Dictionary with empty serial
    """
    return {
        "name": "router-05",
        "site": "site-e",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "",
    }


def device_with_long_serial():
    """Create a device with a serial exceeding 64 characters.

    Returns:
        Dictionary with long serial
    """
    return {
        "name": "router-06",
        "site": "site-f",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "this-is-a-very-long-serial-number-that-exceeds-sixty-four-characters-xyz",
    }


def device_with_long_asset_tag():
    """Create a device with an asset tag exceeding 64 characters.

    Returns:
        Dictionary with long asset tag
    """
    return {
        "name": "router-07",
        "site": "site-g",
        "device_type": "cisco-9300",
        "role": "core-router",
        "asset_tag": "this-is-a-very-long-asset-tag-that-exceeds-sixty-four-characters-abc",
    }


def device_with_null_values():
    """Create a device with null optional fields.

    Returns:
        Dictionary with null optional fields
    """
    return {
        "name": "router-08",
        "site": "site-h",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": None,
        "asset_tag": None,
        "platform": None,
    }


def valid_devices_list():
    """Create a list of valid device dictionaries.

    Returns:
        List of valid device dictionaries
    """
    return [
        {
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        },
        {
            "name": "switch-01",
            "site": "site-b",
            "device_type": "arista-7280",
            "role": "spine-router",
        },
        {
            "name": "firewall-01",
            "site": "site-c",
            "device_type": "paloalto-firewall",
            "role": "edge-firewall",
        },
    ]


def devices_with_various_issues():
    """Create a list of devices with various validation issues.

    Returns:
        List of device dictionaries with issues
    """
    return [
        {
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "status": "invalid_status",
        },
        {
            "name": "router-02",
            "site": "site-b",
            "device_type": "arista-7280",
            "role": "spine-router",
        },
        {
            "name": "this-is-a-very-long-device-name-that-exceeds-maximum-length",
            "site": "site-c",
            "device_type": "cisco-9300",
            "role": "core-router",
        },
    ]


def custom_rule_device():
    """Create a device for testing custom rules.

    Returns:
        Dictionary with data for custom rule testing
    """
    return {
        "name": "router-09",
        "site": "site-i",
        "device_type": "custom-model-x",
        "role": "custom-role-y",
        "custom_fields": {
            "manufacturer": "custom-vendor",
            "build_date": "2024-01-15",
            "warranty_end": "2027-01-15",
        },
    }

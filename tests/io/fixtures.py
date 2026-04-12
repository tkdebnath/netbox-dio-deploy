# I/O layer test fixtures
# Provides test data for batch processing and client testing

import pytest


@pytest.fixture
def sample_device_dicts():
    """Returns a list of 1500+ device dictionaries for chunking tests.

    The list includes:
    - 500 basic devices
    - 500 devices with subcomponents (interfaces, VLANs)
    - 500 devices with full data
    - 10 extra devices for edge case testing
    """
    devices = []

    # Basic devices (500)
    for i in range(500):
        devices.append({
            "name": f"router-{i:04d}",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "serial": f"SN{i:08d}",
            "asset_tag": f"AT-{i:04d}",
            "platform": "Cisco IOS XE",
            "status": "active",
        })

    # Devices with interfaces (500)
    for i in range(500, 1000):
        devices.append({
            "name": f"switch-{i:04d}",
            "site": "site-b",
            "device_type": "cisco-9200",
            "role": "access-switch",
            "serial": f"SN{i:08d}",
            "asset_tag": f"AT-{i:04d}",
            "platform": "Cisco IOS XE",
            "status": "active",
            "interfaces": [
                {
                    "name": f"eth0-{i}",
                    "device": f"switch-{i:04d}",
                    "type": "physical",
                    "label": f"Interface {i}",
                    "enabled": True,
                    "speed": 1000,
                    "duplex": "full",
                    "mtu": 1500,
                },
                {
                    "name": f"eth1-{i}",
                    "device": f"switch-{i:04d}",
                    "type": "physical",
                    "label": f"Interface {i} secondary",
                    "enabled": False,
                },
            ],
        })

    # Devices with full data including VLANs (500)
    for i in range(1000, 1500):
        devices.append({
            "name": f"firewall-{i:04d}",
            "site": "site-c",
            "device_type": "fortinet-1000",
            "role": "firewall",
            "serial": f"SN{i:08d}",
            "asset_tag": f"AT-{i:04d}",
            "platform": "FortiOS",
            "status": "active",
            "interfaces": [
                {
                    "name": f"wan0-{i}",
                    "device": f"firewall-{i:04d}",
                    "type": "physical",
                    "enabled": True,
                },
                {
                    "name": f"lan0-{i}",
                    "device": f"firewall-{i:04d}",
                    "type": "physical",
                    "enabled": True,
                    "mode": "access",
                    "untagged_vlan": f"vlan-{i % 100}",
                },
            ],
            "vlans": [
                {
                    "name": f"vlan-{i % 100}",
                    "vid": i % 100,
                    "site": f"site-c",
                    "status": "active",
                    "role": "access",
                },
            ],
        })

    # Extra devices for edge case testing (10)
    for i in range(1500, 1510):
        devices.append({
            "name": f"edge-case-{i:04d}",
            "site": "site-d",
            "device_type": "test-device",
            "role": "test-role",
            "status": "planned",
        })

    return devices


@pytest.fixture
def batch_payload():
    """Returns a simulated batch payload structure.

    This represents what a batch of device dictionaries would look like
    when prepared for batch processing.
    """
    return {
        "devices": [
            {
                "name": "device-001",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "serial": "SN001",
            },
            {
                "name": "device-002",
                "site": "site-a",
                "device_type": "cisco-9200",
                "role": "access-switch",
                "serial": "SN002",
            },
            {
                "name": "device-003",
                "site": "site-b",
                "device_type": "arista-7050",
                "role": "spine-switch",
                "serial": "SN003",
            },
        ],
        "options": {
            "dry_run": False,
            "validate_only": False,
            "continue_on_error": True,
        },
    }


@pytest.fixture
def chunked_payloads():
    """Returns pre-chunked payloads for testing.

    Each chunk contains 1000 devices max.
    """
    chunk1 = [
        {"name": f"device-{i:04d}", "site": "site-a", "device_type": "cisco-9300", "role": "core-router"}
        for i in range(1000)
    ]
    chunk2 = [
        {"name": f"device-{i:04d}", "site": "site-b", "device_type": "cisco-9200", "role": "access-switch"}
        for i in range(1000, 1500)
    ]

    return [chunk1, chunk2]


@pytest.fixture
def single_device_dict():
    """Returns a basic single device dictionary."""
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
def device_with_subcomponents():
    """Returns a device dictionary with interfaces and VLANs."""
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
def device_with_errors():
    """Returns a device dictionary with missing required fields for error testing."""
    return {
        "name": "incomplete-device",
        # Missing site, device_type, role - will fail validation
    }

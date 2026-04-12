"""Shared fixtures for CLI tests.

This file provides reusable test data structures for testing CLI commands
including single devices, batches of devices, and edge cases for validation.
"""

import pytest
import json
import yaml


# Device fixtures from main conftest.py
@pytest.fixture
def device_data():
    """Returns a dict with all required and optional fields."""
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
        "business_unit": "enterprise",
    }


@pytest.fixture
def required_only_data():
    """Returns a dict with only required fields."""
    return {
        "name": "switch-01",
        "site": "site-b",
        "device_type": "cisco-9200",
        "role": "access-switch",
    }


@pytest.fixture
def device_list():
    """Returns a list of 3 devices for batch testing."""
    return [
        {
            "name": "device-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "serial": "SN-001",
        },
        {
            "name": "device-02",
            "site": "site-b",
            "device_type": "cisco-9200",
            "role": "access-switch",
            "serial": "SN-002",
        },
        {
            "name": "device-03",
            "site": "site-c",
            "device_type": "juniper-mx",
            "role": "edge-router",
            "serial": "SN-003",
        },
    ]


# File content fixtures
@pytest.fixture
def file_json(device_data):
    """Returns JSON file content as string."""
    return json.dumps([device_data], indent=2)


@pytest.fixture
def file_yaml(device_data):
    """Returns YAML file content as string."""
    return yaml.dump([device_data], default_flow_style=False)


@pytest.fixture
def batch_payload(device_list):
    """Returns a structure for batch processing with chunk info."""
    return {
        "devices": device_list,
        "chunk_size": 100,
        "total_count": len(device_list),
    }


# Edge case fixtures
@pytest.fixture
def edge_case_missing_required():
    """Returns a dict missing a required field (site)."""
    return {
        "name": "router-03",
        "device_type": "cisco-9300",
        "role": "core-router",
    }


@pytest.fixture
def edge_case_invalid_status():
    """Returns a dict with an invalid status value."""
    return {
        "name": "router-02",
        "site": "site-c",
        "device_type": "cisco-9300",
        "role": "distribution-router",
        "status": "invalid_status",
    }


@pytest.fixture
def edge_case_oversized_name():
    """Returns a dict with an oversized name field (>64 chars)."""
    return {
        "name": "a" * 70,
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
    }


@pytest.fixture
def edge_case_empty_name():
    """Returns a dict with an empty name field."""
    return {
        "name": "",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
    }


@pytest.fixture
def edge_case_special_chars():
    """Returns a dict with special characters in name."""
    return {
        "name": "router-01 / test (primary)",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
    }


@pytest.fixture
def edge_case_null_values():
    """Returns a dict with None/null values for optional fields."""
    return {
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": None,
        "asset_tag": None,
        "platform": None,
        "status": None,
        "custom_fields": None,
    }


# Batch fixtures
@pytest.fixture
def many_device_dicts():
    """Returns a list of 10+ device dictionaries for batch testing."""
    devices = []
    for i in range(15):
        devices.append({
            "name": f"device-{i:02d}",
            "site": f"site-{chr(97 + (i % 3))}",
            "device_type": f"model-{i % 3}",
            "role": "core-router" if i % 2 == 0 else "access-switch",
            "serial": f"SN-{i:05d}",
        })
    return devices


@pytest.fixture
def large_dataset():
    """Returns a list of 1500+ devices for batch size testing."""
    devices = []
    for i in range(1500):
        devices.append({
            "name": f"device-{i:04d}",
            "site": f"site-{i % 10}",
            "device_type": f"model-{i % 5}",
            "role": "core-router" if i % 2 == 0 else "access-switch",
            "serial": f"SN-{i:08d}",
        })
    return devices


# YAML content fixtures
@pytest.fixture
def yaml_content_single():
    """Returns YAML content for a single device."""
    return """- name: test-device-01
  site: site-a
  device_type: cisco-9300
  role: core-router
  serial: SN-001
  asset_tag: AT-001
"""


@pytest.fixture
def yaml_content_list():
    """Returns YAML content for multiple devices."""
    return """- name: device-01
  site: site-a
  device_type: cisco-9300
  role: core-router
- name: device-02
  site: site-b
  device_type: cisco-9200
  role: access-switch
- name: device-03
  site: site-c
  device_type: juniper-mx
  role: edge-router
"""


@pytest.fixture
def json_content_list():
    """Returns JSON content for multiple devices."""
    return """[
  {
    "name": "device-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router",
    "serial": "SN-001"
  },
  {
    "name": "device-02",
    "site": "site-b",
    "device_type": "cisco-9200",
    "role": "access-switch",
    "serial": "SN-002"
  },
  {
    "name": "device-03",
    "site": "site-c",
    "device_type": "juniper-mx",
    "role": "edge-router",
    "serial": "SN-003"
  }
]"""


# Invalid content fixtures
@pytest.fixture
def invalid_json_content():
    """Returns invalid JSON content."""
    return '{"name": "device", "site": "site-a", "device_type": "cisco-9300", "role": "core-router",}'


@pytest.fixture
def invalid_yaml_content():
    """Returns invalid YAML content."""
    return """name: device
site: site-a
  - device_type: invalid indentation
role: core-router"""


@pytest.fixture
def malformed_yaml_multidoc():
    """Returns multi-document YAML with malformed content."""
    return """---
name: device-01
site: site-a
device_type: cisco-9300
role: core-router
---
name: device-02
site: site-b
device_type: cisco-9200
role: access-switch
---
invalid yaml content here
"""


# Rack/PDU/Circuit/PowerFeed fixtures
@pytest.fixture
def rack_data():
    """Returns a dict for DiodeRack device."""
    return {
        "name": "rack-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "rack_type": "42U",
        "rack_width": 19,
        "rack_height": 42,
        "rack_depth": 1200,
        "rack_unit": "U",
        "serial": "RACK-001",
        "asset_tag": "AT-RACK-001",
        "location": "A1",
    }


@pytest.fixture
def pdu_data():
    """Returns a dict for DiodePDU device."""
    return {
        "name": "pdu-01",
        "site": "site-a",
    }


@pytest.fixture
def circuit_data():
    """Returns a dict for DiodeCircuit device."""
    return {
        "cid": "CIR-001",
        "name": "circuit-01",
        "site": "site-a",
    }


@pytest.fixture
def power_feed_data():
    """Returns a dict for DiodePowerFeed device."""
    return {
        "name": "power-feed-01",
        "power_panel": "power-panel-01",
        "site": "site-a",
    }

"""Pytest fixtures for export functionality tests."""

import pytest

from netbox_dio.models import (
    DiodeDevice,
    DiodeRack,
    DiodePDU,
    DiodeCircuit,
    DiodePowerFeed,
    DiodeInterface,
    DiodeVLAN,
)


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
    }


@pytest.fixture
def rack_data():
    """Returns a dict with all required and optional fields for rack."""
    return {
        "name": "rack-01",
        "site": "site-a",
        "rack_type": "42u",
        "serial": "RACK-001",
        "role": "core-rack",
        "u_height": 42,
        "starting_unit": 1,
        "description": "Core rack for router-01",
        "status": "active",
        "location": "A-1",
        "airflow": "front-to-rear",
    }


@pytest.fixture
def pdu_data():
    """Returns a dict with all required and optional fields for PDU."""
    return {
        "name": "pdu-01",
        "site": "site-a",
        "description": "Main PDU for rack-01",
        "status": "active",
        "amperage": 30,
        "phase": "3-phase",
        "voltage": 208,
        "outlets": [
            {
                "name": "outlet-1",
                "device": "pdu-01",
                "type": "iec-309",
            }
        ],
    }


@pytest.fixture
def circuit_data():
    """Returns a dict with all required and optional fields for circuit."""
    return {
        "cid": "CIR-001",
        "name": "primary-circuit",
        "type": "primary",
        "provider": "telco-1",
        "status": "active",
        "commit_rate": 1000000000,
    }


@pytest.fixture
def power_feed_data():
    """Returns a dict with all required and optional fields for power feed."""
    return {
        "name": "power-feed-01",
        "power_panel": "power-panel-01",
        "phase": "3-phase",
        "supply": "ac",
        "voltage": 208,
        "amperage": 100,
        "status": "active",
        "rack": "rack-01",
    }


@pytest.fixture
def device_list(device_data):
    """Returns a list of 3 test devices."""
    return [
        DiodeDevice.from_dict({**device_data, "name": "device-01"}),
        DiodeDevice.from_dict({**device_data, "name": "device-02"}),
        DiodeDevice.from_dict({**device_data, "name": "device-03"}),
    ]


@pytest.fixture
def interface_data():
    """Returns a dict with interface data."""
    return {
        "name": "eth0",
        "device": "router-01",
        "type": "physical",
        "speed": 10000,
        "duplex": "full",
        "enabled": True,
        "description": "Upstream connection",
    }


@pytest.fixture
def vlan_data():
    """Returns a dict with VLAN data."""
    return {
        "name": "vlan-100",
        "site": "site-a",
        "vid": 100,
        "role": "management",
        "status": "active",
    }


@pytest.fixture
def file_device_data():
    """Returns a dict with data suitable for file import."""
    return {
        "name": "file-device-01",
        "site": "site-b",
        "device_type": " Juniper MX",
        "role": "edge-router",
        "serial": "JX-12345",
        "asset_tag": "AT-FILE-01",
        "status": "planned",
    }

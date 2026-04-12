# Pytest fixtures for DiodeDevice tests
# This file provides shared test data for all model tests

import pytest


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
def invalid_status_data():
    """Returns a dict with an invalid status value."""
    return {
        "name": "router-02",
        "site": "site-c",
        "device_type": "cisco-9300",
        "role": "distribution-router",
        "status": "invalid_status",
    }


@pytest.fixture
def missing_required_data():
    """Returns a dict missing a required field (site)."""
    return {
        "name": "router-03",
        "device_type": "cisco-9300",
        "role": "core-router",
    }

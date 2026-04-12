"""Pytest fixtures for validator testing.

This module provides pytest fixtures for testing the validation framework.
"""

import pytest

from netbox_dio.validators.framework import RuleRegistry, ValidatorPipeline


@pytest.fixture
def rule_registry():
    """Create a fresh rule registry for each test.

    Returns:
        RuleRegistry instance
    """
    return RuleRegistry.get_instance()


@pytest.fixture
def validator_pipeline():
    """Create a fresh validator pipeline for each test.

    Returns:
        ValidatorPipeline instance
    """
    return ValidatorPipeline()


@pytest.fixture
def sample_devices():
    """Create a list of sample devices for testing.

    Returns:
        List of DiodeDevice instances
    """
    from netbox_dio.models import DiodeDevice

    return [
        DiodeDevice(
            name="device-01",
            site="site-a",
            device_type="cisco-9300",
            role="core-router",
        ),
        DiodeDevice(
            name="device-02",
            site="site-b",
            device_type="arista-7280",
            role="spine-router",
        ),
        DiodeDevice(
            name="device-03",
            site="site-c",
            device_type="paloalto-firewall",
            role="edge-firewall",
        ),
    ]

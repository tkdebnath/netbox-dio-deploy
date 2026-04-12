"""Test suite for the converter module."""

import pytest

from netbox_dio.converter import (
    convert_device,
    convert_device_to_entities,
    convert_interface,
    convert_vlan,
)
from netbox_dio.models import DiodeDevice
from netboxlabs.diode.sdk.ingester import Entity


class TestConvertDevice:
    """Tests for the convert_device() function."""

    def test_convert_device_basic(self, required_only_data: dict) -> None:
        """Test basic conversion with required fields only."""
        device = DiodeDevice.model_validate(required_only_data)
        entity = convert_device(device)

        assert entity is not None
        assert entity.device.name == device.name
        assert entity.device.site.name == device.site
        assert entity.device.device_type.model == device.device_type
        assert entity.device.role.name == device.role

    def test_convert_device_with_optional_fields(self, device_data: dict) -> None:
        """Test conversion with all optional fields."""
        device = DiodeDevice.model_validate(device_data)
        entity = convert_device(device)

        assert entity.device.serial == device.serial
        assert entity.device.asset_tag == device.asset_tag
        assert entity.device.platform.name == device.platform
        assert entity.device.status == device.status

    def test_convert_device_protobuf_compatibility(self, required_only_data: dict) -> None:
        """Test that output is a valid protobuf message."""
        device = DiodeDevice.model_validate(required_only_data)
        entity = convert_device(device)

        # Verify it's a protobuf message with SerializeToString method
        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0

    def test_convert_device_with_custom_fields(self, device_data: dict) -> None:
        """Test conversion with custom fields."""
        device = DiodeDevice.model_validate(device_data)
        entity = convert_device(device)

        # Custom fields should be None (converted in to_protobuf)
        assert entity.device.custom_fields is None or entity.device.custom_fields == {}

    def test_convert_device_to_entities_returns_list(self, required_only_data: dict) -> None:
        """Test that convert_device_to_entities returns a list of Entities."""
        device = DiodeDevice.model_validate(required_only_data)
        entities = convert_device_to_entities(device)

        assert isinstance(entities, list)
        assert len(entities) == 1
        # Check protobuf Entity type
        assert type(entities[0]).__name__ == 'Entity'
        assert entities[0].device.name == device.name


class TestStubFunctions:
    """Tests for stub conversion functions (Phase 3)."""

    def test_convert_interface_raises_not_implemented(self) -> None:
        """Test that convert_interface raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            convert_interface(None)

    def test_convert_vlan_raises_not_implemented(self) -> None:
        """Test that convert_vlan raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            convert_vlan(None)

"""Test suite for subcomponent conversion functions."""

import pytest

from netbox_dio.converter import (
    convert_interface,
    convert_vlan,
    convert_module,
    convert_module_bay,
    convert_cable,
    convert_prefix,
    convert_ip_address,
)
from netbox_dio.models import (
    DiodeInterface,
    DiodeVLAN,
    DiodeModule,
    DiodeModuleBay,
    DiodeCable,
    CableTerminationPoint,
    DiodePrefix,
    DiodeIPAddress,
)


class TestConvertInterface:
    """Tests for convert_interface function."""

    def test_convert_interface_basic(self) -> None:
        """Test basic interface conversion."""
        interface = DiodeInterface(name="eth0", device="router-01", type="physical")
        entity = convert_interface(interface)

        assert entity is not None
        assert entity.interface.name == "eth0"
        assert entity.interface.type == "physical"

    def test_convert_interface_with_optional_fields(self) -> None:
        """Test interface conversion with optional fields."""
        interface = DiodeInterface(
            name="eth0",
            device="router-01",
            type="physical",
            label="primary-interface",
            enabled=True,
            mtu=1500,
            description="uplink to core",
            mode="access",
            speed=1000,
            duplex="full",
            untagged_vlan="vlan100",
        )
        entity = convert_interface(interface)

        assert entity is not None
        assert entity.interface.name == "eth0"
        assert entity.interface.label == "primary-interface"
        assert entity.interface.mtu == 1500
        assert entity.interface.mode == "access"

    def test_convert_interface_to_protobuf(self) -> None:
        """Test converting interface to protobuf is valid."""
        interface = DiodeInterface(name="eth0", device="router-01", type="physical")
        entity = convert_interface(interface)

        # Verify it's a valid protobuf message
        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertVLAN:
    """Tests for convert_vlan function."""

    def test_convert_vlan_basic(self) -> None:
        """Test basic VLAN conversion."""
        vlan = DiodeVLAN(name="vlan100", vid=100, site="site-a")
        entity = convert_vlan(vlan)

        assert entity is not None
        assert entity.vlan.name == "vlan100"
        assert entity.vlan.vid == 100

    def test_convert_vlan_with_optional_fields(self) -> None:
        """Test VLAN conversion with optional fields."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
            description="production-vlan",
            status="active",
            role="access",
            tenant="enterprise",
        )
        entity = convert_vlan(vlan)

        assert entity is not None
        assert entity.vlan.name == "vlan100"
        assert entity.vlan.description == "production-vlan"

    def test_convert_vlan_to_protobuf(self) -> None:
        """Test converting VLAN to protobuf is valid."""
        vlan = DiodeVLAN(name="vlan100", vid=100, site="site-a")
        entity = convert_vlan(vlan)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertModule:
    """Tests for convert_module function."""

    def test_convert_module_basic(self) -> None:
        """Test basic module conversion."""
        module = DiodeModule(module_type="cisco-9300", device="router-01")
        entity = convert_module(module)

        assert entity is not None
        assert entity.module.module_type.model == "cisco-9300"

    def test_convert_module_with_optional_fields(self) -> None:
        """Test module conversion with optional fields."""
        module = DiodeModule(
            module_type="cisco-9300",
            device="router-01",
            serial="SN123456",
            asset_tag="AT-001",
            status="active",
            description="supervisor-engine",
        )
        entity = convert_module(module)

        assert entity is not None
        assert entity.module.serial == "SN123456"
        assert entity.module.status == "active"

    def test_convert_module_to_protobuf(self) -> None:
        """Test converting module to protobuf is valid."""
        module = DiodeModule(module_type="cisco-9300", device="router-01")
        entity = convert_module(module)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertModuleBay:
    """Tests for convert_module_bay function."""

    def test_convert_module_bay_basic(self) -> None:
        """Test basic module bay conversion."""
        bay = DiodeModuleBay(device="router-01", module="module-1", position=1)
        entity = convert_module_bay(bay)

        assert entity is not None
        assert entity.module_bay.position == "1"

    def test_convert_module_bay_with_optional_fields(self) -> None:
        """Test module bay conversion with optional fields."""
        bay = DiodeModuleBay(
            device="router-01",
            module="module-1",
            position=1,
            name="supervisor-bay",
            label="Slot 1",
            description="Primary supervisor module",
        )
        entity = convert_module_bay(bay)

        assert entity is not None
        assert entity.module_bay.name == "supervisor-bay"
        assert entity.module_bay.label == "Slot 1"

    def test_convert_module_bay_to_protobuf(self) -> None:
        """Test converting module bay to protobuf is valid."""
        bay = DiodeModuleBay(device="router-01", module="module-1", position=1)
        entity = convert_module_bay(bay)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertCable:
    """Tests for convert_cable function."""

    def test_convert_cable_basic(self) -> None:
        """Test basic cable conversion."""
        a_term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        b_term = CableTerminationPoint(termination_type="device", termination_id="switch-01", cable_end="B")
        cable = DiodeCable(a_terminations=[a_term], b_terminations=[b_term], type="cat6")
        entity = convert_cable(cable)

        assert entity is not None
        assert entity.cable.type == "cat6"

    def test_convert_cable_with_optional_fields(self) -> None:
        """Test cable conversion with optional fields."""
        a_term = CableTerminationPoint(termination_type="interface", termination_id="eth0", cable_end="A")
        b_term = CableTerminationPoint(termination_type="interface", termination_id="eth1", cable_end="B")
        cable = DiodeCable(
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6",
            status="active",
            label="uplink-cable",
            color="blue",
        )
        entity = convert_cable(cable)

        assert entity is not None
        assert entity.cable.type == "cat6"
        assert entity.cable.status == "active"

    def test_convert_cable_to_protobuf(self) -> None:
        """Test converting cable to protobuf is valid."""
        a_term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        b_term = CableTerminationPoint(termination_type="device", termination_id="switch-01", cable_end="B")
        cable = DiodeCable(a_terminations=[a_term], b_terminations=[b_term], type="cat6")
        entity = convert_cable(cable)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertPrefix:
    """Tests for convert_prefix function."""

    def test_convert_prefix_basic(self) -> None:
        """Test basic prefix conversion."""
        prefix = DiodePrefix(prefix="192.168.1.0/24")
        entity = convert_prefix(prefix)

        assert entity is not None
        assert entity.prefix.prefix == "192.168.1.0/24"

    def test_convert_prefix_with_optional_fields(self) -> None:
        """Test prefix conversion with optional fields."""
        prefix = DiodePrefix(
            prefix="192.168.1.0/24",
            vrf="vrf-internal",
            status="active",
            role="network",
            is_pool=True,
            tenant="enterprise",
        )
        entity = convert_prefix(prefix)

        assert entity is not None
        assert entity.prefix.prefix == "192.168.1.0/24"
        assert entity.prefix.status == "active"

    def test_convert_prefix_to_protobuf(self) -> None:
        """Test converting prefix to protobuf is valid."""
        prefix = DiodePrefix(prefix="192.168.1.0/24")
        entity = convert_prefix(prefix)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0


class TestConvertIPAddress:
    """Tests for convert_ip_address function."""

    def test_convert_ip_address_basic(self) -> None:
        """Test basic IP address conversion."""
        ip = DiodeIPAddress(address="192.168.1.1/24")
        entity = convert_ip_address(ip)

        assert entity is not None
        assert entity.ip_address.address == "192.168.1.1/24"

    def test_convert_ip_address_with_optional_fields(self) -> None:
        """Test IP address conversion with optional fields."""
        ip = DiodeIPAddress(
            address="192.168.1.1/24",
            vrf="vrf-internal",
            tenant="enterprise",
            status="active",
            role="secondary",
            dns_name="router-01.example.com",
        )
        entity = convert_ip_address(ip)

        assert entity is not None
        assert entity.ip_address.address == "192.168.1.1/24"
        assert entity.ip_address.status == "active"

    def test_convert_ip_address_to_protobuf(self) -> None:
        """Test converting IP address to protobuf is valid."""
        ip = DiodeIPAddress(address="192.168.1.1/24")
        entity = convert_ip_address(ip)

        assert hasattr(entity, 'SerializeToString')
        protobuf_bytes = entity.SerializeToString()
        assert len(protobuf_bytes) > 0

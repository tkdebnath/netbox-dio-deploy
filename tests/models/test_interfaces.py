"""Test suite for DiodeInterface model."""
import pytest
from netbox_dio.models.interface import DiodeInterface, InterfaceType, InterfaceMode, InterfaceDuplex


class TestInterfaceCreation:
    """Tests for DiodeInterface creation."""

    def test_interface_creation(self) -> None:
        """Test basic interface creation with required fields."""
        interface = DiodeInterface(name="eth0", device="router-01", type="physical")
        assert interface.name == "eth0"
        assert interface.device == "router-01"
        assert interface.type == InterfaceType.physical

    def test_interface_with_optional_fields(self) -> None:
        """Test interface creation with all optional fields."""
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
            mgmt_only=False,
            untagged_vlan="vlan100",
        )
        assert interface.name == "eth0"
        assert interface.label == "primary-interface"
        assert interface.mtu == 1500
        assert interface.description == "uplink to core"
        assert interface.mode == InterfaceMode.access

    def test_interface_type_validation(self) -> None:
        """Test interface type enum validation."""
        interface = DiodeInterface(name="eth0", device="router-01", type="virtual")
        assert interface.type == InterfaceType.virtual

        interface = DiodeInterface(name="lag0", device="router-01", type="lag")
        assert interface.type == InterfaceType.lag

        interface = DiodeInterface(name="wlan0", device="ap-01", type="wireless")
        assert interface.type == InterfaceType.wireless

    def test_interface_mode_validation(self) -> None:
        """Test interface mode enum validation."""
        interface = DiodeInterface(name="eth0", device="switch-01", type="physical", mode="access")
        assert interface.mode == InterfaceMode.access

        interface = DiodeInterface(name="trunk0", device="switch-01", type="physical", mode="trunk")
        assert interface.mode == InterfaceMode.trunk

    def test_interface_from_dict(self) -> None:
        """Test creating interface from dictionary."""
        data = {
            "name": "eth0",
            "device": "router-01",
            "type": "physical",
            "label": "uplink",
            "enabled": True,
            "mtu": 1500,
            "speed": 1000,
            "duplex": "full",
            "mode": "trunk",
            "untagged_vlan": "vlan100",
        }
        interface = DiodeInterface.from_dict(data)
        assert interface.name == "eth0"
        assert interface.label == "uplink"
        assert interface.mtu == 1500
        assert interface.mode == InterfaceMode.trunk


class TestInterfaceToProtobuf:
    """Tests for DiodeInterface to protobuf conversion."""

    def test_interface_to_protobuf(self) -> None:
        """Test converting interface to protobuf."""
        interface = DiodeInterface(name="eth0", device="router-01", type="physical")
        protobuf = interface.to_protobuf()
        assert protobuf is not None
        assert protobuf.name == "eth0"

    def test_interface_to_protobuf_with_all_fields(self) -> None:
        """Test converting interface with all fields to protobuf."""
        interface = DiodeInterface(
            name="eth0",
            device="router-01",
            type="physical",
            label="primary-interface",
            enabled=True,
            mtu=1500,
            speed=1000,
            duplex="full",
            mode="access",
            untagged_vlan="vlan100",
        )
        protobuf = interface.to_protobuf()
        assert protobuf.name == "eth0"
        assert protobuf.mtu == 1500
        assert protobuf.speed == 1000
        assert protobuf.duplex == "full"
        assert protobuf.mode == "access"
        # untagged_vlan is converted to a VLAN object by the SDK
        assert protobuf.untagged_vlan.name == "vlan100"

    def test_interface_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        interface = DiodeInterface(name="eth0", device="router-01", type="physical")
        protobuf = interface.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

"""Test suite for DiodeVLAN model."""
import pytest
from netbox_dio.models.vlan import DiodeVLAN, VLANStatus, VLANRole, VLANGroup


class TestVLANCreation:
    """Tests for DiodeVLAN creation."""

    def test_vlan_creation(self) -> None:
        """Test basic VLAN creation with required fields."""
        vlan = DiodeVLAN(name="vlan100", vid=100, site="site-a")
        assert vlan.name == "vlan100"
        assert vlan.vid == 100
        assert vlan.site == "site-a"

    def test_vlan_with_optional_fields(self) -> None:
        """Test VLAN creation with all optional fields."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
            description="production-vlan",
            status="active",
            role="access",
            tenant="enterprise",
            qinq_svlan=200,
        )
        assert vlan.name == "vlan100"
        assert vlan.description == "production-vlan"
        assert vlan.status == VLANStatus.active
        assert vlan.role == VLANRole.access

    def test_vlan_from_dict(self) -> None:
        """Test creating VLAN from dictionary."""
        data = {
            "name": "vlan200",
            "vid": 200,
            "site": "site-b",
            "description": "dmz-vlan",
            "status": "reserved",
            "role": "distribution",
        }
        vlan = DiodeVLAN.from_dict(data)
        assert vlan.name == "vlan200"
        assert vlan.vid == 200
        assert vlan.description == "dmz-vlan"
        assert vlan.status == VLANStatus.reserved

    def test_vlan_validation(self) -> None:
        """Test VLAN status and role validation."""
        vlan = DiodeVLAN(name="vlan300", vid=300, site="site-c", status="deprecated")
        assert vlan.status == VLANStatus.deprecated

        vlan = DiodeVLAN(name="vlan400", vid=400, site="site-c", role="core")
        assert vlan.role == VLANRole.core


class TestVLANToProtobuf:
    """Tests for DiodeVLAN to protobuf conversion."""

    def test_vlan_to_protobuf(self) -> None:
        """Test converting VLAN to protobuf."""
        vlan = DiodeVLAN(name="vlan100", vid=100, site="site-a")
        protobuf = vlan.to_protobuf()
        assert protobuf is not None
        assert protobuf.name == "vlan100"
        assert protobuf.vid == 100

    def test_vlan_to_protobuf_with_all_fields(self) -> None:
        """Test converting VLAN with all fields to protobuf."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
            description="production-vlan",
            status="active",
            role="access",
            tenant="enterprise",
        )
        protobuf = vlan.to_protobuf()
        assert protobuf.name == "vlan100"
        assert protobuf.description == "production-vlan"
        assert protobuf.status == "active"

    def test_vlan_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        vlan = DiodeVLAN(name="vlan100", vid=100, site="site-a")
        protobuf = vlan.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

"""Test suite for DiodeIPAddress model."""
import pytest
from netbox_dio.models.ip_address import DiodeIPAddress, IPAddressStatus, IPAddressRole


class TestIPCreation:
    """Tests for DiodeIPAddress creation."""

    def test_ip_creation(self) -> None:
        """Test basic IP address creation with required fields."""
        ip = DiodeIPAddress(address="192.168.1.1/24")
        assert ip.address == "192.168.1.1/24"

    def test_ip_with_optional_fields(self) -> None:
        """Test IP address creation with all optional fields."""
        ip = DiodeIPAddress(
            address="192.168.1.1/24",
            vrf="vrf-internal",
            tenant="enterprise",
            status="active",
            role="loopback",
            dns_name="router-01.example.com",
            description="management-ip",
        )
        assert ip.address == "192.168.1.1/24"
        assert ip.vrf == "vrf-internal"
        assert ip.status == IPAddressStatus.active
        assert ip.role == IPAddressRole.loopback
        assert ip.dns_name == "router-01.example.com"

    def test_ip_from_dict(self) -> None:
        """Test creating IP address from dictionary."""
        data = {
            "address": "10.0.0.1/8",
            "vrf": "vrf-public",
            "status": "reserved",
            "role": "anycast",
        }
        ip = DiodeIPAddress.from_dict(data)
        assert ip.address == "10.0.0.1/8"
        assert ip.vrf == "vrf-public"
        assert ip.status == IPAddressStatus.reserved

    def test_ip_validation(self) -> None:
        """Test IP status and role validation."""
        ip = DiodeIPAddress(address="172.16.0.1/12", status="deprecated")
        assert ip.status == IPAddressStatus.deprecated

        ip = DiodeIPAddress(address="192.168.0.1/24", role="vip")
        assert ip.role == IPAddressRole.vip

    def test_ipv6_address(self) -> None:
        """Test IPv6 address creation."""
        ip = DiodeIPAddress(address="2001:db8::1/64")
        assert ip.address == "2001:db8::1/64"


class TestIPToProtobuf:
    """Tests for DiodeIPAddress to protobuf conversion."""

    def test_ip_to_protobuf(self) -> None:
        """Test converting IP address to protobuf."""
        ip = DiodeIPAddress(address="192.168.1.1/24")
        protobuf = ip.to_protobuf()
        assert protobuf is not None
        assert protobuf.address == "192.168.1.1/24"

    def test_ip_to_protobuf_with_all_fields(self) -> None:
        """Test converting IP address with all fields to protobuf."""
        ip = DiodeIPAddress(
            address="192.168.1.1/24",
            vrf="vrf-internal",
            tenant="enterprise",
            status="active",
            role="secondary",
            dns_name="router-01.example.com",
        )
        protobuf = ip.to_protobuf()
        assert protobuf.address == "192.168.1.1/24"
        assert protobuf.vrf.name == "vrf-internal"
        assert protobuf.status == "active"
        assert protobuf.role == "secondary"

    def test_ip_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        ip = DiodeIPAddress(address="192.168.1.1/24")
        protobuf = ip.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

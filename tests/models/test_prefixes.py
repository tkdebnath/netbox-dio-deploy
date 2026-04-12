"""Test suite for DiodePrefix model."""
import pytest
from netbox_dio.models.prefix import DiodePrefix, PrefixStatus, PrefixRole


class TestPrefixCreation:
    """Tests for DiodePrefix creation."""

    def test_prefix_creation(self) -> None:
        """Test basic prefix creation with required fields."""
        prefix = DiodePrefix(prefix="192.168.1.0/24")
        assert prefix.prefix == "192.168.1.0/24"

    def test_prefix_with_optional_fields(self) -> None:
        """Test prefix creation with all optional fields."""
        prefix = DiodePrefix(
            prefix="192.168.1.0/24",
            vrf="vrf-internal",
            status="active",
            role="network",
            is_pool=True,
            mark_utilized=50,
            description="management-network",
            tenant="enterprise",
        )
        assert prefix.prefix == "192.168.1.0/24"
        assert prefix.vrf == "vrf-internal"
        assert prefix.status == PrefixStatus.active
        assert prefix.role == PrefixRole.network

    def test_prefix_from_dict(self) -> None:
        """Test creating prefix from dictionary."""
        data = {
            "prefix": "10.0.0.0/8",
            "vrf": "vrf-public",
            "status": "reserved",
            "role": "loopback",
        }
        prefix = DiodePrefix.from_dict(data)
        assert prefix.prefix == "10.0.0.0/8"
        assert prefix.vrf == "vrf-public"
        assert prefix.status == PrefixStatus.reserved

    def test_prefix_validation(self) -> None:
        """Test prefix status and role validation."""
        prefix = DiodePrefix(prefix="172.16.0.0/12", status="deprecated")
        assert prefix.status == PrefixStatus.deprecated

        prefix = DiodePrefix(prefix="10.10.0.0/16", role="relay")
        assert prefix.role == PrefixRole.relay

    def test_ipv6_prefix(self) -> None:
        """Test IPv6 prefix creation."""
        prefix = DiodePrefix(prefix="2001:db8::/32")
        assert prefix.prefix == "2001:db8::/32"


class TestPrefixToProtobuf:
    """Tests for DiodePrefix to protobuf conversion."""

    def test_prefix_to_protobuf(self) -> None:
        """Test converting prefix to protobuf."""
        prefix = DiodePrefix(prefix="192.168.1.0/24")
        protobuf = prefix.to_protobuf()
        assert protobuf is not None
        assert protobuf.prefix == "192.168.1.0/24"

    def test_prefix_to_protobuf_with_all_fields(self) -> None:
        """Test converting prefix with all fields to protobuf."""
        prefix = DiodePrefix(
            prefix="192.168.1.0/24",
            vrf="vrf-internal",
            status="active",
            role="network",
            is_pool=True,
            tenant="enterprise",
        )
        protobuf = prefix.to_protobuf()
        assert protobuf.prefix == "192.168.1.0/24"
        assert protobuf.vrf.name == "vrf-internal"
        assert protobuf.status == "active"

    def test_prefix_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        prefix = DiodePrefix(prefix="192.168.1.0/24")
        protobuf = prefix.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

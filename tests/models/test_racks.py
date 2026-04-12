"""Test suite for DiodeRack model."""

import pytest
from netbox_dio.models.rack import DiodeRack


class TestRackCreation:
    """Tests for DiodeRack creation."""

    def test_rack_creation(self) -> None:
        """Test basic rack creation with required fields."""
        rack = DiodeRack(name="R1", site="site-a", rack_type="42u")
        assert rack.name == "R1"
        assert rack.site == "site-a"
        assert rack.rack_type == "42u"

    def test_rack_with_optional_fields(self) -> None:
        """Test rack creation with all optional fields."""
        rack = DiodeRack(
            name="R1",
            site="site-a",
            rack_type="42u",
            serial="SN123456",
            asset_tag="AT-001",
            role="main-rack",
            u_height=48,
            starting_unit=1,
            description="Main server rack",
            status="active",
        )
        assert rack.name == "R1"
        assert rack.serial == "SN123456"
        assert rack.u_height == 48
        assert rack.starting_unit == 1
        assert rack.status == "active"

    def test_rack_from_dict(self) -> None:
        """Test creating rack from dictionary."""
        data = {
            "name": "R2",
            "site": "site-b",
            "rack_type": "45u",
            "u_height": 42,
            "status": "planned",
        }
        rack = DiodeRack.from_dict(data)
        assert rack.name == "R2"
        assert rack.rack_type == "45u"
        assert rack.u_height == 42

    def test_rack_to_protobuf(self) -> None:
        """Test converting rack to protobuf."""
        rack = DiodeRack(name="R1", site="site-a", rack_type="42u")
        protobuf = rack.to_protobuf()
        assert protobuf is not None
        assert protobuf.name == "R1"
        assert protobuf.site.name == "site-a"
        assert protobuf.rack_type.model == "42u"


class TestRackValidation:
    """Tests for DiodeRack field validation."""

    def test_name_too_short(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodeRack(name="", site="site-a", rack_type="42u")

    def test_name_too_long(self) -> None:
        """Test that name over 64 chars raises ValueError."""
        long_name = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeRack(name=long_name, site="site-a", rack_type="42u")

    def test_rack_type_too_long(self) -> None:
        """Test that rack type over 64 chars raises ValueError."""
        long_type = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeRack(name="R1", site="site-a", rack_type=long_type)

    def test_serial_too_long(self) -> None:
        """Test that serial over 64 chars raises ValueError."""
        long_serial = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeRack(name="R1", site="site-a", rack_type="42u", serial=long_serial)

    def test_asset_tag_too_long(self) -> None:
        """Test that asset tag over 64 chars raises ValueError."""
        long_tag = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeRack(name="R1", site="site-a", rack_type="42u", asset_tag=long_tag)

    def test_u_height_invalid(self) -> None:
        """Test that u_height must be positive."""
        with pytest.raises(ValueError, match="must be positive"):
            DiodeRack(name="R1", site="site-a", rack_type="42u", u_height=0)

    def test_u_height_too_high(self) -> None:
        """Test that u_height cannot exceed 100."""
        with pytest.raises(ValueError, match="exceeds maximum of 100"):
            DiodeRack(name="R1", site="site-a", rack_type="42u", u_height=101)

    def test_starting_unit_invalid(self) -> None:
        """Test that starting_unit must be 1 or 48."""
        with pytest.raises(ValueError, match="must be 1 or 48"):
            DiodeRack(name="R1", site="site-a", rack_type="42u", starting_unit=5)

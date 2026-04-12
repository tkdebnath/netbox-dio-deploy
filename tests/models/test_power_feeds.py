"""Test suite for DiodePowerFeed model."""

import pytest
from netbox_dio.models.power_feed import DiodePowerFeed


class TestPowerFeedCreation:
    """Tests for DiodePowerFeed creation."""

    def test_power_feed_creation(self) -> None:
        """Test basic power feed creation with required fields."""
        power_feed = DiodePowerFeed(name="PF1", power_panel="PP1")
        assert power_feed.name == "PF1"
        assert power_feed.power_panel == "PP1"

    def test_power_feed_with_optional_fields(self) -> None:
        """Test power feed creation with optional fields."""
        power_feed = DiodePowerFeed(
            name="PF1",
            power_panel="PP1",
            phase="3-phase",
            voltage=208,
            amperage=30,
            capacity=400,
            status="active",
            description="Main power feed",
        )
        assert power_feed.name == "PF1"
        assert power_feed.phase == "3-phase"
        assert power_feed.voltage == 208
        assert power_feed.amperage == 30

    def test_power_feed_from_dict(self) -> None:
        """Test creating power feed from dictionary."""
        data = {
            "name": "PF2",
            "power_panel": "PP2",
            "voltage": 240,
            "amperage": 20,
        }
        power_feed = DiodePowerFeed.from_dict(data)
        assert power_feed.name == "PF2"
        assert power_feed.voltage == 240

    def test_power_feed_to_protobuf(self) -> None:
        """Test converting power feed to protobuf."""
        power_feed = DiodePowerFeed(name="PF1", power_panel="PP1", phase="3-phase")
        protobuf = power_feed.to_protobuf()
        assert protobuf is not None
        assert protobuf.name == "PF1"
        # power_panel is stored as a string reference in the protobuf
        # We just verify the conversion works


class TestPowerFeedValidation:
    """Tests for DiodePowerFeed field validation."""

    def test_name_too_short(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodePowerFeed(name="", power_panel="PP1")

    def test_name_too_long(self) -> None:
        """Test that name over 64 chars raises ValueError."""
        long_name = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodePowerFeed(name=long_name, power_panel="PP1")

    def test_power_panel_too_short(self) -> None:
        """Test that empty power_panel raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodePowerFeed(name="PF1", power_panel="")

    def test_power_panel_too_long(self) -> None:
        """Test that power_panel over 64 chars raises ValueError."""
        long_pp = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodePowerFeed(name="PF1", power_panel=long_pp)

    def test_voltage_invalid_low(self) -> None:
        """Test that voltage must be at least 100."""
        with pytest.raises(ValueError, match="must be at least 100"):
            DiodePowerFeed(name="PF1", power_panel="PP1", voltage=50)

    def test_voltage_too_high(self) -> None:
        """Test that voltage cannot exceed 600."""
        with pytest.raises(ValueError, match="exceeds maximum of 600"):
            DiodePowerFeed(name="PF1", power_panel="PP1", voltage=601)

    def test_amperage_invalid(self) -> None:
        """Test that amperage must be positive."""
        with pytest.raises(ValueError, match="must be positive"):
            DiodePowerFeed(name="PF1", power_panel="PP1", amperage=0)

    def test_amperage_too_high(self) -> None:
        """Test that amperage cannot exceed 500."""
        with pytest.raises(ValueError, match="exceeds maximum of 500"):
            DiodePowerFeed(name="PF1", power_panel="PP1", amperage=501)

    def test_phase_invalid(self) -> None:
        """Test that phase must be valid."""
        with pytest.raises(ValueError, match="must be one of"):
            DiodePowerFeed(name="PF1", power_panel="PP1", phase="invalid-phase")

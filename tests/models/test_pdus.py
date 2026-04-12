"""Test suite for DiodePDU model."""

import pytest
from netbox_dio.models.pdu import DiodePDU, DiodePowerOutlet


class TestPDUCreation:
    """Tests for DiodePDU creation."""

    def test_pdu_creation(self) -> None:
        """Test basic PDU creation with required fields."""
        pdu = DiodePDU(name="PDU1", site="site-a", amperage=30, voltage=208, phase="3-phase")
        assert pdu.name == "PDU1"
        assert pdu.site == "site-a"
        assert pdu.amperage == 30
        assert pdu.phase == "3-phase"

    def test_pdu_with_optional_fields(self) -> None:
        """Test PDU creation with optional fields."""
        pdu = DiodePDU(
            name="PDU1",
            site="site-a",
            description="Main PDU for rack A",
            status="active",
            location="Rack A",
            owner="network-team",
        )
        assert pdu.name == "PDU1"
        assert pdu.description == "Main PDU for rack A"

    def test_pdu_from_dict(self) -> None:
        """Test creating PDU from dictionary."""
        data = {
            "name": "PDU2",
            "site": "site-b",
            "amperage": 15,
            "voltage": 120,
        }
        pdu = DiodePDU.from_dict(data)
        assert pdu.name == "PDU2"
        assert pdu.amperage == 15
        assert pdu.voltage == 120

    def test_pdu_to_protobuf(self) -> None:
        """Test converting PDU to protobuf."""
        pdu = DiodePDU(name="PDU1", site="site-a", amperage=30)
        protobuf = pdu.to_protobuf()
        assert protobuf is not None
        assert protobuf.name == "PDU1"
        assert protobuf.site.name == "site-a"


class TestPowerOutlet:
    """Tests for DiodePowerOutlet."""

    def test_outlet_creation(self) -> None:
        """Test power outlet creation."""
        outlet = DiodePowerOutlet(name="outlet-1", device="PDU1", type="iec-309")
        assert outlet.name == "outlet-1"
        assert outlet.device == "PDU1"
        assert outlet.type == "iec-309"

    def test_outlet_from_dict(self) -> None:
        """Test creating power outlet from dictionary."""
        data = {
            "name": "outlet-2",
            "device": "PDU2",
            "type": "l14-30",
        }
        outlet = DiodePowerOutlet.from_dict(data)
        assert outlet.name == "outlet-2"
        assert outlet.type == "l14-30"

    def test_outlet_type_validation(self) -> None:
        """Test that outlet type is validated."""
        with pytest.raises(ValueError, match="must be a valid outlet type"):
            DiodePowerOutlet(name="outlet-1", device="PDU1", type="invalid-type")


class TestPDUValidation:
    """Tests for DiodePDU field validation."""

    def test_name_too_short(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodePDU(name="", site="site-a", amperage=30)

    def test_name_too_long(self) -> None:
        """Test that name over 64 chars raises ValueError."""
        long_name = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodePDU(name=long_name, site="site-a", amperage=30)

    def test_amperage_invalid(self) -> None:
        """Test that amperage must be in range 1-500."""
        with pytest.raises(ValueError, match="must be positive"):
            DiodePDU(name="PDU1", site="site-a", amperage=0)

    def test_amperage_too_high(self) -> None:
        """Test that amperage cannot exceed 500."""
        with pytest.raises(ValueError, match="exceeds maximum of 500"):
            DiodePDU(name="PDU1", site="site-a", amperage=501)

    def test_voltage_invalid_low(self) -> None:
        """Test that voltage must be at least 100."""
        with pytest.raises(ValueError, match="must be at least 100"):
            DiodePDU(name="PDU1", site="site-a", voltage=50, amperage=30)

    def test_voltage_too_high(self) -> None:
        """Test that voltage cannot exceed 600."""
        with pytest.raises(ValueError, match="exceeds maximum of 600"):
            DiodePDU(name="PDU1", site="site-a", voltage=601, amperage=30)

    def test_phase_invalid(self) -> None:
        """Test that phase must be valid."""
        with pytest.raises(ValueError, match="must be one of"):
            DiodePDU(name="PDU1", site="site-a", amperage=30, phase="invalid-phase")

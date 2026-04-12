"""Test suite for DiodeCircuit model."""

import pytest
from netbox_dio.models.power_circuit import DiodeCircuit


class TestCircuitCreation:
    """Tests for DiodeCircuit creation."""

    def test_circuit_creation(self) -> None:
        """Test basic circuit creation with required fields."""
        circuit = DiodeCircuit(cid="CIR-001", name="main-circuit")
        assert circuit.cid == "CIR-001"
        assert circuit.name == "main-circuit"

    def test_circuit_with_optional_fields(self) -> None:
        """Test circuit creation with optional fields."""
        circuit = DiodeCircuit(
            cid="CIR-001",
            name="main-circuit",
            type="utility",
            provider="PowerCorp",
            provider_account="PA-123",
            commit_rate=100000000,
            description="Primary power circuit",
            status="active",
        )
        assert circuit.cid == "CIR-001"
        assert circuit.type == "utility"
        assert circuit.commit_rate == 100000000

    def test_circuit_from_dict(self) -> None:
        """Test creating circuit from dictionary."""
        data = {
            "cid": "CIR-002",
            "name": "backup-circuit",
            "commit_rate": 50000000,
        }
        circuit = DiodeCircuit.from_dict(data)
        assert circuit.cid == "CIR-002"
        assert circuit.commit_rate == 50000000

    def test_circuit_to_protobuf(self) -> None:
        """Test converting circuit to protobuf."""
        circuit = DiodeCircuit(cid="CIR-001", name="main-circuit")
        protobuf = circuit.to_protobuf()
        assert protobuf is not None
        assert protobuf.cid == "CIR-001"


class TestCircuitValidation:
    """Tests for DiodeCircuit field validation."""

    def test_cid_too_short(self) -> None:
        """Test that empty CID raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodeCircuit(cid="", name="main-circuit")

    def test_cid_too_long(self) -> None:
        """Test that CID over 64 chars raises ValueError."""
        long_cid = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeCircuit(cid=long_cid, name="main-circuit")

    def test_name_too_short(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            DiodeCircuit(cid="CIR-001", name="")

    def test_name_too_long(self) -> None:
        """Test that name over 64 chars raises ValueError."""
        long_name = "x" * 65
        with pytest.raises(ValueError, match="exceeds maximum length"):
            DiodeCircuit(cid="CIR-001", name=long_name)

    def test_commit_rate_negative(self) -> None:
        """Test that commit_rate cannot be negative."""
        with pytest.raises(ValueError, match="must be non-negative"):
            DiodeCircuit(cid="CIR-001", name="main", commit_rate=-1)

    def test_commit_rate_too_high(self) -> None:
        """Test that commit_rate cannot exceed 100Gbps."""
        with pytest.raises(ValueError, match="exceeds maximum"):
            DiodeCircuit(cid="CIR-001", name="main", commit_rate=100000000001)

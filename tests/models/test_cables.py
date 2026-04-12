"""Test suite for DiodeCable model."""
import pytest
from netbox_dio.models.cable import DiodeCable, CableTerminationPoint, CableType, CableStatus, CableTerminationPointType


class TestCableCreation:
    """Tests for DiodeCable creation."""

    def test_cable_creation(self) -> None:
        """Test basic cable creation with required fields."""
        a_term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        b_term = CableTerminationPoint(termination_type="device", termination_id="switch-01", cable_end="B")
        cable = DiodeCable(a_terminations=[a_term], b_terminations=[b_term], type="cat6")
        assert cable.a_terminations[0].termination_type == "device"
        assert cable.b_terminations[0].termination_id == "switch-01"
        assert cable.type == CableType.cat6

    def test_cable_with_optional_fields(self) -> None:
        """Test cable creation with all optional fields."""
        a_term = CableTerminationPoint(termination_type="interface", termination_id="eth0", cable_end="A")
        b_term = CableTerminationPoint(termination_type="interface", termination_id="eth1", cable_end="B")
        cable = DiodeCable(
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6a",
            status="active",
            label="uplink-cable",
            color="blue",
            length=5,
            length_unit="m",
            description="primary uplink",
        )
        assert cable.a_terminations[0].termination_type == "interface"
        assert cable.status == CableStatus.active
        assert cable.color == "blue"
        assert cable.length == 5

    def test_cable_from_dict(self) -> None:
        """Test creating cable from dictionary."""
        data = {
            "a_terminations": [
                {
                    "termination_type": "device",
                    "termination_id": "router-01",
                    "cable_end": "A",
                }
            ],
            "b_terminations": [
                {
                    "termination_type": "device",
                    "termination_id": "switch-01",
                    "cable_end": "B",
                }
            ],
            "type": "fiber",
            "status": "planned",
        }
        cable = DiodeCable.from_dict(data)
        assert cable.type == CableType.fiber
        assert cable.status == CableStatus.planned

    def test_termination_point_validation(self) -> None:
        """Test cable termination point validation."""
        # Valid termination types
        term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        assert term.termination_type == "device"

        term = CableTerminationPoint(termination_type="interface", termination_id="eth0", cable_end="B")
        assert term.termination_type == "interface"

        # Valid cable ends
        assert term.cable_end == "B"


class TestCableToProtobuf:
    """Tests for DiodeCable to protobuf conversion."""

    def test_cable_to_protobuf(self) -> None:
        """Test converting cable to protobuf."""
        a_term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        b_term = CableTerminationPoint(termination_type="device", termination_id="switch-01", cable_end="B")
        cable = DiodeCable(a_terminations=[a_term], b_terminations=[b_term], type="cat6")
        protobuf = cable.to_protobuf()
        assert protobuf is not None
        assert protobuf.type == "cat6"

    def test_cable_to_protobuf_with_all_fields(self) -> None:
        """Test converting cable with all fields to protobuf."""
        a_term = CableTerminationPoint(termination_type="interface", termination_id="eth0", cable_end="A")
        b_term = CableTerminationPoint(termination_type="interface", termination_id="eth1", cable_end="B")
        cable = DiodeCable(
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6",
            status="active",
            label="primary-uplink",
            color="green",
        )
        protobuf = cable.to_protobuf()
        assert protobuf.type == "cat6"
        assert protobuf.status == "active"
        assert protobuf.label == "primary-uplink"

    def test_cable_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        a_term = CableTerminationPoint(termination_type="device", termination_id="router-01", cable_end="A")
        b_term = CableTerminationPoint(termination_type="device", termination_id="switch-01", cable_end="B")
        cable = DiodeCable(a_terminations=[a_term], b_terminations=[b_term], type="cat6")
        protobuf = cable.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

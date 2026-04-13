"""Test suite for DiodeCable model."""
import pytest
from netbox_dio.models.cable import DiodeCable, TerminationPoint, CableType, CableStatus


class TestCableCreation:
    """Tests for DiodeCable creation."""

    def test_cable_creation(self) -> None:
        """Test basic cable creation with required fields."""
        a_term = TerminationPoint(type="device", id="router-01", cable_end="A")
        b_term = TerminationPoint(type="device", id="switch-01", cable_end="B")
        cable = DiodeCable(
            label="test-cable",
            device_a="router-01",
            device_b="switch-01",
            type="cat6"
        )
        assert cable.device_a == "router-01"
        assert cable.device_b == "switch-01"
        assert cable.type == CableType.cat6

    def test_cable_with_optional_fields(self) -> None:
        """Test cable creation with all optional fields."""
        a_term = TerminationPoint(type="interface", id="eth0", cable_end="A")
        b_term = TerminationPoint(type="interface", id="eth1", cable_end="B")
        cable = DiodeCable(
            label="uplink-cable",
            device_a="eth0-device",
            device_b="eth1-device",
            type="cat6a",
            status="active",
            color="blue",
            length=5,
            length_unit="m",
            description="primary uplink",
        )
        assert cable.status == CableStatus.active
        assert cable.color == "blue"
        assert cable.length == 5

    def test_cable_from_dict(self) -> None:
        """Test creating cable from dictionary."""
        data = {
            "label": "test-cable",
            "device_a": "router-01",
            "device_b": "switch-01",
            "type": "fiber",
            "status": "planned",
        }
        cable = DiodeCable.from_dict(data)
        assert cable.type == CableType.fiber
        assert cable.status == CableStatus.planned

    def test_termination_point_validation(self) -> None:
        """Test cable termination point validation."""
        # Valid termination types
        term = TerminationPoint(type="device", id="router-01", cable_end="A")
        assert term.type == "device"

        term = TerminationPoint(type="interface", id="eth0", cable_end="B")
        assert term.type == "interface"

        # Valid cable ends
        assert term.cable_end == "B"


class TestCableToProtobuf:
    """Tests for DiodeCable to protobuf conversion."""

    def test_cable_to_protobuf(self) -> None:
        """Test converting cable to protobuf."""
        a_term = TerminationPoint(type="device", id="router-01", cable_end="A")
        b_term = TerminationPoint(type="device", id="switch-01", cable_end="B")
        cable = DiodeCable(
            label="test-cable",
            device_a="router-01",
            device_b="switch-01",
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6"
        )
        protobuf = cable.to_protobuf()
        assert protobuf is not None
        assert protobuf.type == "cat6"

    def test_cable_to_protobuf_with_all_fields(self) -> None:
        """Test converting cable with all fields to protobuf."""
        a_term = TerminationPoint(type="interface", id="eth0", cable_end="A")
        b_term = TerminationPoint(type="interface", id="eth1", cable_end="B")
        cable = DiodeCable(
            label="primary-uplink",
            device_a="eth0-device",
            device_b="eth1-device",
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6",
            status="active",
            color="green",
        )
        protobuf = cable.to_protobuf()
        assert protobuf.type == "cat6"
        assert protobuf.status == "active"
        assert protobuf.label == "primary-uplink"

    def test_cable_protobuf_serialization(self) -> None:
        """Test that protobuf output is serializable."""
        a_term = TerminationPoint(type="device", id="router-01", cable_end="A")
        b_term = TerminationPoint(type="device", id="switch-01", cable_end="B")
        cable = DiodeCable(
            label="test-cable",
            device_a="router-01",
            device_b="switch-01",
            a_terminations=[a_term],
            b_terminations=[b_term],
            type="cat6"
        )
        protobuf = cable.to_protobuf()
        serialized = protobuf.SerializeToString()
        assert len(serialized) > 0

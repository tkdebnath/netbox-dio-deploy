"""JSON export tests for NetBox Diode Device Wrapper."""

import json
import pytest

from netbox_dio import DiodeDevice, DiodeRack, DiodePDU, DiodeCircuit, DiodePowerFeed
from netbox_dio.export import to_json, to_yaml, export_devices
from netbox_dio.importer import import_from_json


class TestJSONExportBasic:
    """Test basic JSON export functionality."""

    def test_to_json_basic(self, device_data):
        """Test basic JSON export with required fields only."""
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)
        data = json.loads(json_str)

        assert data["name"] == "router-01"
        assert data["site"] == "site-a"
        assert data["device_type"] == "cisco-9300"
        assert data["role"] == "core-router"

    def test_to_json_with_optional_fields(self, device_data):
        """Test JSON export with all fields."""
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)
        data = json.loads(json_str)

        assert data["serial"] == "SN123456789"
        assert data["asset_tag"] == "AT-001"
        assert data["platform"] == "Cisco IOS XE"
        assert data["status"] == "active"
        assert data["custom_fields"] == {"location": "rack-a1", "owner": "network-team"}

    def test_to_json_pretty(self, device_data):
        """Test pretty-printed JSON with indentation."""
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device, pretty=True)

        # Check for indentation
        assert '  "' in json_str
        assert '\n' in json_str

        # Parse to verify it's valid
        data = json.loads(json_str)
        assert data["name"] == "router-01"

    def test_to_json_device_list(self, device_list):
        """Test batch export of multiple devices."""
        json_str = export_devices(device_list, format="json")
        data = json.loads(json_str)

        assert len(data) == 3
        assert data[0]["name"] == "device-01"
        assert data[1]["name"] == "device-02"
        assert data[2]["name"] == "device-03"

    def test_to_json_rack(self, rack_data):
        """Test JSON export for DiodeRack."""
        rack = DiodeRack.from_dict(rack_data)
        json_str = to_json(rack)
        data = json.loads(json_str)

        assert data["name"] == "rack-01"
        assert data["site"] == "site-a"
        assert data["rack_type"] == "42u"
        assert data["u_height"] == 42

    def test_to_json_pdu(self, pdu_data):
        """Test JSON export for DiodePDU."""
        pdu = DiodePDU.from_dict(pdu_data)
        json_str = to_json(pdu)
        data = json.loads(json_str)

        assert data["name"] == "pdu-01"
        assert data["site"] == "site-a"
        assert data["amperage"] == 30
        assert data["phase"] == "3-phase"
        assert data["voltage"] == 208

    def test_to_json_circuit(self, circuit_data):
        """Test JSON export for DiodeCircuit."""
        circuit = DiodeCircuit.from_dict(circuit_data)
        json_str = to_json(circuit)
        data = json.loads(json_str)

        assert data["cid"] == "CIR-001"
        assert data["name"] == "primary-circuit"
        assert data["provider"] == "telco-1"

    def test_to_json_power_feed(self, power_feed_data):
        """Test JSON export for DiodePowerFeed."""
        power_feed = DiodePowerFeed.from_dict(power_feed_data)
        json_str = to_json(power_feed)
        data = json.loads(json_str)

        assert data["name"] == "power-feed-01"
        assert data["power_panel"] == "power-panel-01"
        assert data["voltage"] == 208
        assert data["amperage"] == 100


class TestJSONValidation:
    """Test JSON output validation."""

    def test_json_valid_parseable(self, device_data):
        """Verify JSON is valid and parseable."""
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

        # Verify round-trip
        device2 = DiodeDevice.from_dict(parsed)
        assert device2.name == device.name

    def test_json_roundtrip(self, device_data):
        """Test export and re-import should work."""
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        # Parse back
        data = json.loads(json_str)
        device2 = DiodeDevice.from_dict(data)

        assert device2.name == device.name
        assert device2.site == device.site
        assert device2.device_type == device.device_type
        assert device2.role == device.role

    def test_json_special_characters(self):
        """Test handling of special characters in device name."""
        device_data = {
            "name": "router-01 / test",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        }
        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)
        data = json.loads(json_str)

        assert data["name"] == "router-01 / test"


class TestExportDevices:
    """Test the export_devices function."""

    def test_export_devices_yaml(self, device_list):
        """Test export_devices with YAML format."""
        yaml_str = export_devices(device_list, format="yaml")
        import yaml
        data = yaml.safe_load(yaml_str)
        assert len(data) == 3

    def test_export_devices_netbox_yaml(self, device_list):
        """Test export_devices with netbox-yaml format."""
        yaml_str = export_devices(device_list, format="netbox-yaml")
        import yaml
        data = yaml.safe_load(yaml_str)

        assert "device_type" in data
        assert "device" in data
        assert len(data["device"]) == 3

    def test_export_devices_invalid_format(self, device_list):
        """Test export_devices raises error for invalid format."""
        with pytest.raises(Exception):
            export_devices(device_list, format="invalid")
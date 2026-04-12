"""YAML export tests for NetBox Diode Device Wrapper."""

import pytest

import yaml

from netbox_dio import DiodeDevice, DiodeRack, DiodePDU
from netbox_dio.export import to_yaml, to_netbox_yaml, export_devices


class TestYAMLExportBasic:
    """Test basic YAML export functionality."""

    def test_to_yaml_basic(self, device_data):
        """Test basic YAML export."""
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        assert "name: router-01" in yaml_str
        assert "site: site-a" in yaml_str
        assert "device_type: cisco-9300" in yaml_str
        assert "role: core-router" in yaml_str

    def test_to_yaml_multiline(self):
        """Test YAML with proper multiline strings."""
        device_data = {
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "platform": "Cisco IOS XE\nVersion 17.3.3",
        }
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        # YAML should handle multiline properly
        parsed = yaml.safe_load(yaml_str)
        assert parsed["platform"] == "Cisco IOS XE\nVersion 17.3.3"

    def test_to_yaml_netbox_compatible(self, device_data):
        """Test that YAML is NetBox-compatible."""
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        # Should be parseable as YAML
        parsed = yaml.safe_load(yaml_str)
        assert isinstance(parsed, dict)
        assert parsed["name"] == "router-01"

    def test_to_yaml_special_chars(self):
        """Test handling of special characters in YAML."""
        device_data = {
            "name": "router-01 @ dc1",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        }
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        parsed = yaml.safe_load(yaml_str)
        assert parsed["name"] == "router-01 @ dc1"

    def test_yaml_to_json(self, device_data):
        """Test YAML to JSON conversion works."""
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        # Convert YAML to dict
        yaml_dict = yaml.safe_load(yaml_str)

        # Convert to JSON and back
        import json
        json_str = json.dumps(yaml_dict)
        parsed = json.loads(json_str)

        assert parsed["name"] == "router-01"

    def test_yaml_roundtrip(self, device_data):
        """Test export to YAML and back works."""
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_yaml(device)

        # Parse back
        parsed = yaml.safe_load(yaml_str)
        device2 = DiodeDevice.from_dict(parsed)

        assert device2.name == device.name
        assert device2.site == device.site


class TestYAMLExportNetbox:
    """Test NetBox YAML export."""

    def test_to_netbox_yaml_structure(self, device_data):
        """Test the structure of NetBox YAML output."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        assert "device_type" in result
        assert "device" in result
        assert isinstance(result["device_type"], list)
        assert isinstance(result["device"], list)

    def test_netbox_yaml_device_type_reference(self, device_data):
        """Test that device_type is a reference in NetBox YAML."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        device_entry = result["device"][0]
        assert "device_type" in device_entry
        assert isinstance(device_entry["device_type"], dict)
        assert "name" in device_entry["device_type"]


class TestExportDevicesYAML:
    """Test export_devices with YAML format."""

    def test_export_devices_yaml_basic(self, device_list):
        """Test batch export to YAML."""
        yaml_str = export_devices(device_list, format="yaml")
        data = yaml.safe_load(yaml_str)
        assert len(data) == 3

    def test_export_devices_netbox_yaml(self, device_list):
        """Test batch export to NetBox YAML."""
        yaml_str = export_devices(device_list, format="netbox-yaml")
        result = yaml.safe_load(yaml_str)

        assert "device_type" in result
        assert "device" in result
        assert len(result["device"]) == 3

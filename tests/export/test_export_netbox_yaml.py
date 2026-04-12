"""NetBox YAML export tests for NetBox Diode Device Wrapper."""

import pytest

import yaml

from netbox_dio import DiodeDevice, DiodeRack
from netbox_dio.export import to_netbox_yaml, export_devices


class TestNetBoxYAMLExport:
    """Test NetBox YAML export functionality."""

    def test_to_netbox_yaml_device(self, device_data):
        """Test export device with device_type template."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        assert "device_type" in result
        assert "device" in result

        # Check device_type structure
        device_type = result["device_type"][0]
        assert device_type["name"] == "cisco-9300"
        assert "manufacturer" in device_type
        assert "model_name" in device_type

        # Check device structure
        device_entry = result["device"][0]
        assert device_entry["name"] == "router-01"
        assert device_entry["device_type"]["name"] == "cisco-9300"
        assert device_entry["role"]["name"] == "core-router"
        assert device_entry["site"]["name"] == "site-a"

    def test_netbox_yaml_with_custom_data(self, device_data):
        """Test export with custom data in device."""
        device_data["custom_fields"] = {"rack_location": "A-1"}
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        dev = result["device"][0]
        assert dev["custom_fields"]["rack_location"] == "A-1"

    def test_to_netbox_yaml_structure(self, device_data):
        """Test the structure of NetBox YAML output."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        # Verify required fields
        assert "device_type" in result
        assert "device" in result
        assert isinstance(result["device_type"], list)
        assert isinstance(result["device"], list)

        # Verify device_type has required fields
        dt = result["device_type"][0]
        assert "name" in dt
        assert "manufacturer" in dt

        # Verify device has required fields
        dev = result["device"][0]
        assert "name" in dev
        assert "device_type" in dev
        assert "role" in dev
        assert "site" in dev

    def test_netbox_yaml_device_type_reference(self, device_data):
        """Test that device_type is a reference (not full object)."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        device_entry = result["device"][0]
        assert isinstance(device_entry["device_type"], dict)
        assert "name" in device_entry["device_type"]
        # Should NOT have full device type object, just reference
        assert "serial" not in device_entry["device_type"]

    def test_to_netbox_yaml_with_interfaces(self):
        """Test export with interfaces in custom_fields."""
        device_data = {
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "custom_fields": {
                "interfaces": [
                    {"name": "eth0", "type": "physical"},
                    {"name": "eth1", "type": "physical"},
                ]
            },
        }
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        dev = result["device"][0]
        assert dev["custom_fields"]["interfaces"][0]["name"] == "eth0"

    def test_netbox_yaml_multidoc(self, device_list):
        """Test multiple devices in single file."""
        result = export_devices(device_list, format="netbox-yaml")

        parsed = yaml.safe_load(result)
        assert len(parsed["device"]) == 3

        # All devices should reference the same device type (de-duplicated)
        device_type_names = set()
        for dt in parsed["device_type"]:
            device_type_names.add(dt["name"])
        assert len(device_type_names) == 1  # All same type


class TestNetBoxYAMLValidation:
    """Test NetBox YAML output validation."""

    def test_netbox_yaml_valid_parseable(self, device_data):
        """Verify NetBox YAML is valid and parseable."""
        device = DiodeDevice.from_dict(device_data)
        yaml_str = to_netbox_yaml(device)
        result_str = yaml.dump(yaml_str, default_flow_style=False)

        parsed = yaml.safe_load(result_str)
        assert isinstance(parsed, dict)

    def test_netbox_yaml_serializable(self, device_data):
        """Test that NetBox YAML can be serialized and parsed."""
        device = DiodeDevice.from_dict(device_data)
        result = to_netbox_yaml(device)

        # Serialize to YAML string
        yaml_str = yaml.dump(result)

        # Parse back
        parsed = yaml.safe_load(yaml_str)
        assert parsed["device"][0]["name"] == "router-01"
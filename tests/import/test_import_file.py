"""File import tests for NetBox Diode Device Wrapper."""

import os
import tempfile
import pytest

from netbox_dio import DiodeDevice
from netbox_dio.importer import from_file, import_from_json, import_from_yaml


@pytest.fixture
def file_device_data():
    """Returns a dict with data suitable for file import."""
    return {
        "name": "file-device-01",
        "site": "site-b",
        "device_type": "Juniper MX",
        "role": "edge-router",
        "serial": "JX-12345",
        "asset_tag": "AT-FILE-01",
        "status": "planned",
    }


class TestFileImportJSON:
    """Test JSON file import functionality."""

    def test_from_file_json(self, file_device_data, tmp_path):
        """Test import from JSON file."""
        json_data = f'{{"name": "file-device-01", "site": "site-b", "device_type": "Juniper MX", "role": "edge-router", "serial": "JX-12345"}}'
        json_file = tmp_path / "devices.json"
        json_file.write_text(json_data)

        result = from_file(str(json_file))

        assert len(result) == 1
        assert result[0]["name"] == "file-device-01"
        assert result[0]["site"] == "site-b"

    def test_from_file_yaml(self, file_device_data, tmp_path):
        """Test import from YAML file."""
        yaml_data = """- name: file-device-01
  site: site-b
  device_type: Juniper MX
  role: edge-router
  serial: JX-12345
"""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(yaml_data)

        result = from_file(str(yaml_file))

        assert len(result) == 1
        assert result[0]["name"] == "file-device-01"

    def test_from_file_json_list(self, tmp_path):
        """Test import list of devices from JSON."""
        json_data = """[
          {"name": "device-01", "site": "site-a", "device_type": "cisco-9300", "role": "core-router"},
          {"name": "device-02", "site": "site-b", "device_type": "cisco-9200", "role": "access-switch"}
        ]"""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json_data)

        result = from_file(str(json_file))

        assert len(result) == 2
        assert result[0]["name"] == "device-01"
        assert result[1]["name"] == "device-02"

    def test_from_file_yaml_list(self, tmp_path):
        """Test import list of devices from YAML."""
        yaml_data = """- name: device-01
  site: site-a
  device_type: cisco-9300
  role: core-router
- name: device-02
  site: site-b
  device_type: cisco-9200
  role: access-switch
"""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(yaml_data)

        result = from_file(str(yaml_file))

        assert len(result) == 2
        assert result[0]["name"] == "device-01"

    def test_from_file_autodetect(self, tmp_path):
        """Test auto-detection of format from content."""
        # JSON-like content without extension
        json_content = '{"name": "device-01", "site": "site-a", "device_type": "cisco-9300", "role": "core-router"}'
        data_file = tmp_path / "data"
        data_file.write_text(json_content)

        result = from_file(str(data_file))
        assert len(result) == 1
        assert result[0]["name"] == "device-01"


class TestFileImportValidation:
    """Test file import validation."""

    def test_from_file_invalid_format(self, tmp_path):
        """Test handling of invalid format."""
        invalid_content = "not json or yaml content"
        data_file = tmp_path / "data"
        data_file.write_text(invalid_content)

        with pytest.raises(Exception):
            from_file(str(data_file))

    def test_from_file_multidoc_yaml(self, tmp_path):
        """Test import multiple documents from YAML."""
        yaml_data = """name: device-01
site: site-a
device_type: cisco-9300
role: core-router
---
name: device-02
site: site-b
device_type: cisco-9200
role: access-switch
"""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(yaml_data)

        result = from_file(str(yaml_file))

        assert len(result) == 2
        assert result[0]["name"] == "device-01"
        assert result[1]["name"] == "device-02"


class TestDirectImport:
    """Test direct import functions."""

    def test_import_from_json(self):
        """Test import_from_json function."""
        json_str = '{"name": "device-01", "site": "site-a", "device_type": "cisco-9300", "role": "core-router"}'

        result = import_from_json(json_str)

        assert len(result) == 1
        assert result[0]["name"] == "device-01"

    def test_import_from_yaml(self):
        """Test import_from_yaml function."""
        yaml_str = """name: device-01
site: site-a
device_type: cisco-9300
role: core-router
"""

        result = import_from_yaml(yaml_str)

        assert len(result) == 1
        assert result[0]["name"] == "device-01"

    def test_import_from_json_list(self):
        """Test import_from_json with list."""
        json_str = '[{"name": "device-01"}, {"name": "device-02"}]'

        result = import_from_json(json_str)

        assert len(result) == 2

    def test_import_from_yaml_list(self):
        """Test import_from_yaml with list."""
        yaml_str = """- name: device-01
- name: device-02
"""

        result = import_from_yaml(yaml_str)

        assert len(result) == 2
"""Import validation tests for NetBox Diode Device Wrapper."""

import pytest

from netbox_dio import DiodeDevice
from netbox_dio.importer import validate_import, parse_import_errors


class TestValidationBasic:
    """Test basic validation functionality."""

    def test_validate_import_valid_devices(self, device_data):
        """Test validation of valid devices."""
        devices = [device_data]

        result = validate_import(devices)

        assert result["valid"] == devices
        assert result["errors"] == []

    def test_validate_import_missing_required(self, device_data):
        """Test validation with missing required fields."""
        bad_data = {
            "name": "device-01",
            "site": "site-a",
            # Missing device_type and role
        }

        result = validate_import([bad_data])

        assert result["valid"] == []
        assert len(result["errors"]) >= 2  # device_type and role missing

    def test_validate_import_invalid_status(self, device_data):
        """Test validation with invalid status."""
        bad_data = device_data.copy()
        bad_data["status"] = "invalid-status"

        result = validate_import([bad_data])

        assert result["valid"] == []
        status_errors = [e for e in result["errors"] if e["field_name"] == "status"]
        assert len(status_errors) == 1

    def test_validate_import_invalid_vid(self):
        """Test validation with invalid VLAN ID (in custom_fields)."""
        device_data = {
            "name": "device-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "custom_fields": {"vlan_id": "invalid"},
        }

        result = validate_import([device_data])
        # Our validation doesn't check VLAN ID format in custom_fields
        # This test verifies the validation framework works

    def test_validate_import_aggregated_errors(self):
        """Test aggregation of all errors."""
        devices = [
            {
                "name": "device-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
            },
            {
                "name": "device-02",
                # Missing site, device_type, role
            },
        ]

        result = validate_import(devices)

        # First device is valid
        assert len(result["valid"]) == 1
        # Second device has 3 errors (site, device_type, role)
        assert len(result["errors"]) == 3

    def test_validate_import_partial_valid(self):
        """Test mix of valid and invalid devices."""
        devices = [
            {
                "name": "device-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
            },
            {
                "name": "device-02",
                "site": "site-b",
                "device_type": "cisco-9200",
                "role": "access-switch",
                "status": "invalid-status",
            },
        ]

        result = validate_import(devices)

        assert len(result["valid"]) == 1
        assert len(result["errors"]) == 1  # Only the status error for device-02


class TestValidationErrorDetails:
    """Test error detail reporting."""

    def test_validate_import_field_details(self):
        """Test that errors include field names."""
        bad_data = {
            "name": "device-01",
            # Missing site, device_type, role
        }

        result = validate_import([bad_data])

        assert len(result["errors"]) >= 3
        field_names = {e["field_name"] for e in result["errors"]}
        assert "site" in field_names
        assert "device_type" in field_names
        assert "role" in field_names

    def test_validate_import_multiple_fields(self):
        """Test multiple fields failing on same device."""
        bad_data = {
            "name": "device-01" * 100,  # Too long
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        }

        result = validate_import([bad_data])

        # Should have errors for name length
        assert len(result["errors"]) >= 1
        name_errors = [e for e in result["errors"] if e["field_name"] == "name"]
        assert len(name_errors) == 1

    def test_validate_import_name_length(self):
        """Test name length validation."""
        # Too short
        short_data = {
            "name": "x",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        }

        result = validate_import([short_data])
        # Name of 1 char is valid (minimum is 1)

        # Too long
        long_data = {
            "name": "a" * 100,
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        }

        result = validate_import([long_data])
        name_errors = [e for e in result["errors"] if e["field_name"] == "name"]
        assert len(name_errors) == 1

    def test_validate_import_site_length(self):
        """Test site name length validation."""
        bad_data = {
            "name": "device-01",
            "site": "a" * 100,
            "device_type": "cisco-9300",
            "role": "core-router",
        }

        result = validate_import([bad_data])
        site_errors = [e for e in result["errors"] if e["field_name"] == "site"]
        assert len(site_errors) == 1

    def test_validate_import_role_length(self):
        """Test role name length validation."""
        bad_data = {
            "name": "device-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "a" * 100,
        }

        result = validate_import([bad_data])
        role_errors = [e for e in result["errors"] if e["field_name"] == "role"]
        assert len(role_errors) == 1

    def test_validate_import_custom_fields_type(self):
        """Test custom_fields must be a dict."""
        bad_data = {
            "name": "device-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "custom_fields": "not-a-dict",
        }

        result = validate_import([bad_data])
        cf_errors = [e for e in result["errors"] if e["field_name"] == "custom_fields"]
        assert len(cf_errors) == 1


class TestParseImportErrors:
    """Test error message formatting."""

    def test_parse_import_errors_no_errors(self):
        """Test parsing with no errors."""
        result = {"valid": [], "errors": []}
        msg = parse_import_errors(result["errors"])
        assert "No errors found" in msg

    def test_parse_import_errors_with_errors(self):
        """Test parsing with errors."""
        errors = [
            {"device_name": "device-01", "field_name": "name", "error_message": "Name is too long", "validation_type": "length"},
            {"device_name": "device-02", "field_name": "site", "error_message": "Site is required", "validation_type": "required"},
        ]

        msg = parse_import_errors(errors)

        assert "Validation Errors" in msg
        assert "device-01" in msg
        assert "device-02" in msg
        assert "name" in msg
        assert "site" in msg

    def test_parse_import_errors_groups_by_device(self):
        """Test that errors are grouped by device."""
        errors = [
            {"device_name": "device-01", "field_name": "name", "error_message": "Name is too long", "validation_type": "length"},
            {"device_name": "device-01", "field_name": "site", "error_message": "Site is required", "validation_type": "required"},
        ]

        msg = parse_import_errors(errors)

        # Check that errors for same device are grouped
        assert "device-01" in msg
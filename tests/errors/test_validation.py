"""Tests for validation error handling.

Tests cover:
- Missing required fields
- Invalid status values
- Name length validation
- Serial format validation
- Asset tag format validation
- from_dict() error wrapping
"""

import pytest
from netbox_dio import DiodeValidationError
from netbox_dio.models import DiodeDevice


class TestDeviceValidationMissingRequiredField:
    """Tests for missing required field validation."""

    def test_device_validation_missing_required_field(self):
        """Test that missing required fields raise DiodeValidationError."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({"name": "test-device"})
        assert "site" in str(exc_info.value)

    def test_device_validation_missing_multiple_required_fields(self):
        """Test that multiple missing required fields are detected."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({"name": "test-device", "serial": "SN123"})
        # Both site and device_type and role should be mentioned
        assert "site" in str(exc_info.value)

    def test_device_validation_missing_role(self):
        """Test that missing role field is detected."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({
                "name": "test-device",
                "site": "site-a",
                "device_type": "cisco-9300",
            })
        assert "role" in str(exc_info.value)

    def test_device_validation_with_context(self):
        """Test that validation errors include context."""
        data = {"name": "test-device"}
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict(data, device_name="router-01")
        assert "router-01" in str(exc_info.value)


class TestDeviceValidationInvalidStatus:
    """Tests for invalid status validation."""

    def test_device_validation_invalid_status(self):
        """Test that invalid status values raise error."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({
                "name": "router-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "invalid_status",
            })
        # Verify error message includes device name and invalid value
        error_msg = str(exc_info.value)
        assert "router-01" in error_msg
        assert "invalid_status" in error_msg

    def test_device_validation_status_active(self):
        """Test that 'active' status is valid."""
        device = DiodeDevice.from_dict({
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "status": "active",
        })
        assert device.status == "active"

    def test_device_validation_status_offline(self):
        """Test that 'offline' status is valid."""
        device = DiodeDevice.from_dict({
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "status": "offline",
        })
        assert device.status == "offline"

    def test_device_validation_status_planned(self):
        """Test that 'planned' status is valid."""
        device = DiodeDevice.from_dict({
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "status": "planned",
        })
        assert device.status == "planned"

    def test_device_validation_status_none(self):
        """Test that None status is valid (optional field)."""
        device = DiodeDevice.from_dict({
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
        })
        assert device.status is None


class TestDeviceValidationNameLength:
    """Tests for name length validation."""

    def test_device_validation_name_too_short(self):
        """Test that too short names are rejected."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.validate_name_length("")
        assert "cannot be empty" in str(exc_info.value)

    def test_device_validation_name_too_long(self):
        """Test that too long names are rejected."""
        long_name = "a" * 100
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.validate_name_length(long_name)
        assert "exceeds maximum length of 64" in str(exc_info.value)

    def test_device_validation_name_valid_length(self):
        """Test that valid length names are accepted."""
        name = "router-01"
        result = DiodeDevice.validate_name_length(name)
        assert result == name

    def test_device_validation_name_minimum(self):
        """Test that minimum length name (1 char) is accepted."""
        name = "a"
        result = DiodeDevice.validate_name_length(name)
        assert result == name


class TestDeviceValidationFromDictWithInvalidData:
    """Tests for from_dict() with various invalid data."""

    def test_device_validation_from_dict_with_invalid_data(self):
        """Test from_dict with completely invalid data structure."""
        with pytest.raises(DiodeValidationError):
            DiodeDevice.from_dict({"name": 123})

    def test_device_validation_from_dict_empty_dict(self):
        """Test from_dict with empty dictionary."""
        with pytest.raises(DiodeValidationError):
            DiodeDevice.from_dict({})

    def test_device_validation_from_dict_with_custom_fields(self):
        """Test from_dict with valid custom fields."""
        device = DiodeDevice.from_dict({
            "name": "router-01",
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "custom_fields": {"location": "rack-a1"},
        })
        assert device.custom_fields == {"location": "rack-a1"}


class TestDeviceValidationSerialFormat:
    """Tests for serial number format validation."""

    def test_device_validation_serial_format_valid(self):
        """Test that valid serial format is accepted."""
        serial = "SN123456789"
        result = DiodeDevice.validate_serial_format(serial)
        assert result == serial

    def test_device_validation_serial_format_too_long(self):
        """Test that too long serial numbers are rejected."""
        long_serial = "SN" + "a" * 100
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.validate_serial_format(long_serial)
        assert "exceeds maximum length of 64" in str(exc_info.value)

    def test_device_validation_serial_format_none(self):
        """Test that None serial is accepted (optional field)."""
        result = DiodeDevice.validate_serial_format(None)
        assert result is None


class TestDeviceValidationAssetTagFormat:
    """Tests for asset tag format validation."""

    def test_device_validation_asset_tag_format_valid(self):
        """Test that valid asset tag format is accepted."""
        asset_tag = "AT-001"
        result = DiodeDevice.validate_asset_tag_format(asset_tag)
        assert result == asset_tag

    def test_device_validation_asset_tag_format_too_long(self):
        """Test that too long asset tags are rejected."""
        long_tag = "AT" + "a" * 100
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.validate_asset_tag_format(long_tag)
        assert "exceeds maximum length of 64" in str(exc_info.value)

    def test_device_validation_asset_tag_format_none(self):
        """Test that None asset tag is accepted (optional field)."""
        result = DiodeDevice.validate_asset_tag_format(None)
        assert result is None


class TestValidationErrorContext:
    """Tests for validation error context information."""

    def test_validation_error_field_name(self):
        """Test that validation errors include field name."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({
                "name": "router-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "invalid_status",
            })
        assert exc_info.value.context.get("field_name") == "status"

    def test_validation_error_value(self):
        """Test that validation errors include invalid value."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({
                "name": "router-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "invalid_status",
            })
        assert exc_info.value.context.get("value") == "invalid_status"

    def test_validation_error_device_name(self):
        """Test that validation errors include device name."""
        with pytest.raises(DiodeValidationError) as exc_info:
            DiodeDevice.from_dict({
                "name": "router-01",
                "site": "site-a",
                "device_type": "cisco-9300",
                "role": "core-router",
                "status": "invalid_status",
            }, device_name="production-router")
        assert exc_info.value.context.get("device_name") == "production-router"

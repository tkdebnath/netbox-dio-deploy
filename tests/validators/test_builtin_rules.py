"""Tests for built-in validation rules.

This module tests the built-in validation rules provided by the framework.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.validators import Severity, ValidatorPipeline
from netbox_dio.validators import ValidationRule
from netbox_dio.validators.framework import (
    RequiredFieldsRule,
    ValidStatusRule,
    NameLengthRule,
    SerialLengthRule,
    AssetTagLengthRule,
    RoleMatchDeviceTypeRule,
)


class TestRequiredFieldsRule:
    """Tests for the RequiredFieldsRule."""

    def test_passes_with_all_fields(self):
        """Test that a device with all required fields passes."""
        rule = RequiredFieldsRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True
        assert result.severity == Severity.ERROR

    def test_fails_with_missing_name(self):
        """Test that a device missing the name field fails."""
        rule = RequiredFieldsRule()
        device_dict = {"site": "site", "device_type": "type", "role": "role"}
        result = rule.apply(device_dict)
        assert result.passed is False
        assert "required fields missing" in result.error_message.lower()

    def test_fails_with_missing_site(self):
        """Test that a device missing the site field fails."""
        rule = RequiredFieldsRule()
        device_dict = {"name": "dev", "device_type": "type", "role": "role"}
        result = rule.apply(device_dict)
        assert result.passed is False
        assert "site" in result.error_message.lower()

    def test_fails_with_missing_device_type(self):
        """Test that a device missing the device_type field fails."""
        rule = RequiredFieldsRule()
        device_dict = {"name": "dev", "site": "site", "role": "role"}
        result = rule.apply(device_dict)
        assert result.passed is False
        assert "device_type" in result.error_message.lower()

    def test_fails_with_missing_role(self):
        """Test that a device missing the role field fails."""
        rule = RequiredFieldsRule()
        device_dict = {"name": "dev", "site": "site", "device_type": "type"}
        result = rule.apply(device_dict)
        assert result.passed is False
        assert "role" in result.error_message.lower()



class TestValidStatusRule:
    """Tests for the ValidStatusRule."""

    def test_passes_with_active(self):
        """Test that active status passes."""
        rule = ValidStatusRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="active")
        result = rule.apply(device)
        assert result.passed is True

    def test_passes_with_offline(self):
        """Test that offline status passes."""
        rule = ValidStatusRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="offline")
        result = rule.apply(device)
        assert result.passed is True

    def test_passes_with_planned(self):
        """Test that planned status passes."""
        rule = ValidStatusRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="planned")
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_with_invalid_status(self):
        """Test that an invalid status fails."""
        rule = ValidStatusRule()
        device_dict = {"name": "dev", "site": "site", "device_type": "type", "role": "role", "status": "maintenance"}
        result = rule.apply(device_dict)
        assert result.passed is False
        assert "status" in result.field_name.lower()
        assert "maintenance" in result.value.lower()

    def test_passes_with_none_status(self):
        """Test that None status passes (optional field)."""
        rule = ValidStatusRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status=None)
        result = rule.apply(device)
        assert result.passed is True


class TestNameLengthRule:
    """Tests for the NameLengthRule."""

    def test_passes_with_valid_length(self):
        """Test that a valid length name passes."""
        rule = NameLengthRule()
        device = DiodeDevice(name="valid-name-123", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_with_empty_name(self):
        """Test that an empty name fails."""
        rule = NameLengthRule()
        device = DiodeDevice(name="", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is False
        assert "too short" in result.error_message.lower()

    def test_fails_with_too_long_name(self):
        """Test that a name exceeding 64 characters fails."""
        rule = NameLengthRule()
        long_name = "x" * 65
        device = DiodeDevice(name=long_name, site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is False
        assert "exceeds maximum length" in result.error_message.lower()
        assert "65" in result.error_message or "64" in result.error_message

    def test_name_at_exact_boundary(self):
        """Test that a name at exactly 64 characters passes."""
        rule = NameLengthRule()
        name_64 = "x" * 64
        device = DiodeDevice(name=name_64, site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True


class TestSerialLengthRule:
    """Tests for the SerialLengthRule."""

    def test_passes_with_valid_serial(self):
        """Test that a valid length serial passes."""
        rule = SerialLengthRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial="ABC123")
        result = rule.apply(device)
        assert result.passed is True

    def test_passes_with_none_serial(self):
        """Test that None serial passes (optional field)."""
        rule = SerialLengthRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial=None)
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_with_too_long_serial(self):
        """Test that a serial exceeding 64 characters fails."""
        rule = SerialLengthRule()
        long_serial = "x" * 65
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial=long_serial)
        result = rule.apply(device)
        assert result.passed is False
        assert "serial" in result.field_name.lower()
        assert "exceeds maximum length" in result.error_message.lower()

    def test_serial_at_boundary(self):
        """Test that a serial at exactly 64 characters passes."""
        rule = SerialLengthRule()
        serial_64 = "x" * 64
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial=serial_64)
        result = rule.apply(device)
        assert result.passed is True


class TestAssetTagLengthRule:
    """Tests for the AssetTagLengthRule."""

    def test_passes_with_valid_asset_tag(self):
        """Test that a valid length asset tag passes."""
        rule = AssetTagLengthRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag="TAG123")
        result = rule.apply(device)
        assert result.passed is True

    def test_passes_with_none_asset_tag(self):
        """Test that None asset tag passes (optional field)."""
        rule = AssetTagLengthRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag=None)
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_with_too_long_asset_tag(self):
        """Test that an asset tag exceeding 64 characters fails."""
        rule = AssetTagLengthRule()
        long_tag = "x" * 65
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag=long_tag)
        result = rule.apply(device)
        assert result.passed is False
        assert "asset_tag" in result.field_name.lower()
        assert "exceeds maximum length" in result.error_message.lower()

    def test_asset_tag_at_boundary(self):
        """Test that an asset tag at exactly 64 characters passes."""
        rule = AssetTagLengthRule()
        tag_64 = "x" * 64
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag=tag_64)
        result = rule.apply(device)
        assert result.passed is True


class TestRoleMatchDeviceTypeRule:
    """Tests for the RoleMatchDeviceTypeRule."""

    def test_passes_with_valid_combination(self):
        """Test that a valid role/device-type combination passes."""
        rule = RoleMatchDeviceTypeRule()
        device = DiodeDevice(name="dev", site="site", device_type="cisco-9300", role="core-router")
        result = rule.apply(device)
        assert result.passed is True

    def test_passes_with_none_role(self):
        """Test that None role passes (optional validation)."""
        rule = RoleMatchDeviceTypeRule()
        device_dict = {"name": "dev", "site": "site", "device_type": "type", "role": None}
        result = rule.apply(device_dict)
        assert result.passed is True

    def test_passes_with_none_device_type(self):
        """Test that None device_type passes (optional validation)."""
        rule = RoleMatchDeviceTypeRule()
        device_dict = {"name": "dev", "site": "site", "device_type": None, "role": "role"}
        result = rule.apply(device_dict)
        assert result.passed is True


class TestRuleRegistryIntegration:
    """Integration tests for the rule registry."""

    def test_builtin_rules_register(self):
        """Test that built-in rules can be registered."""
        from netbox_dio.validators.framework import register_builtin_rules, RuleRegistry

        registry = RuleRegistry.get_instance()
        register_builtin_rules(registry)

        assert registry.has_rule("required_fields")
        assert registry.has_rule("valid_status")
        assert registry.has_rule("name_length")
        assert registry.has_rule("serial_length")
        assert registry.has_rule("asset_tag_length")
        assert registry.has_rule("role_match_device_type")

    def test_pipeline_with_builtin_rules(self):
        """Test using the pipeline with built-in rules."""
        from netbox_dio.validators.framework import get_builtin_rules

        pipeline = ValidatorPipeline()
        for rule in get_builtin_rules():
            pipeline.add_rule(rule)

        # Test with valid device
        device = DiodeDevice(name="valid-dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert all(r.passed for r in results)

        # Test with invalid device
        device = DiodeDevice(name="", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert any(not r.passed for r in results)


class TestPipelineSeverities:
    """Tests for severity configuration in pipelines."""

    def test_error_severity_default(self):
        """Test that errors have ERROR severity by default."""
        pipeline = ValidatorPipeline()

        class FailRule(ValidationRule):
            def apply(self, device):
                return self.fail_result("Error")

        pipeline.add_rule(FailRule("fail", "Fail"))
        results = pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert results[0].severity == Severity.ERROR

    def test_warning_severity_configurable(self):
        """Test that rules with WARNING severity produce warning results."""
        from netbox_dio.validators.framework import SerialLengthRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(SerialLengthRule())

        device_dict = {"name": "dev", "site": "site", "device_type": "type", "role": "role", "serial": "x" * 100}
        results = pipeline.run(device_dict)
        assert results[0].severity == Severity.WARNING

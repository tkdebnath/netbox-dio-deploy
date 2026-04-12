"""Tests for cross-field validation rules.

This module tests validation rules that depend on multiple fields.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.validators import Severity, ValidatorPipeline, ValidationResult
from netbox_dio.validators.framework import ValidationRule


class CrossFieldRule(ValidationRule):
    """A rule that validates across multiple fields."""

    def __init__(self) -> None:
        super().__init__(
            name="cross_field_check",
            description="Cross-field validation",
        )

    def apply(self, device: DiodeDevice) -> ValidationResult:
        """Validate device with multiple field dependencies."""
        # If device has platform, it should have a valid status
        if device.platform and device.status == "offline":
            return self.fail_result(
                message="Platform device cannot be offline",
                field_name="platform",
                value=device.platform,
            )
        return self.pass_result()


class TestCrossFieldValidation:
    """Tests for cross-field validation rules."""

    def test_passes_when_platform_and_active(self):
        """Test passing when platform and active status."""
        rule = CrossFieldRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", platform="Cisco", status="active")
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_when_platform_and_offline(self):
        """Test failing when platform and offline status."""
        rule = CrossFieldRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", platform="Cisco", status="offline")
        result = rule.apply(device)
        assert result.passed is False
        assert "platform" in result.field_name.lower()

    def test_passes_without_platform(self):
        """Test passing when no platform is set."""
        rule = CrossFieldRule()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="offline")
        result = rule.apply(device)
        assert result.passed is True


class TestConditionalValidation:
    """Tests for conditionally-applied validation."""

    def test_required_when_field_present(self):
        """Test that a field is required when another field is present."""

        class ConditionalRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="conditional_check",
                    description="Conditional field check",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.serial is not None:
                    # If serial is present (even if empty), it should not be empty
                    if device.serial == "":
                        return self.fail_result(
                            message="Serial cannot be empty when provided",
                            field_name="serial",
                            value="",
                        )
                return self.pass_result()

        rule = ConditionalRule()

        # With serial should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial="ABC123")
        result = rule.apply(device)
        assert result.passed is True

        # With empty serial should fail
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial="")
        result = rule.apply(device)
        assert result.passed is False

        # Without serial should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True


class TestDeviceTypeRoleValidation:
    """Tests for device-type-role validation."""

    def test_valid_device_type_role_combination(self):
        """Test that valid type/role combinations pass."""
        from netbox_dio.validators.framework import RoleMatchDeviceTypeRule

        rule = RoleMatchDeviceTypeRule()
        device = DiodeDevice(name="dev", site="site", device_type="cisco-9300", role="core-router")
        result = rule.apply(device)
        assert result.passed is True

    def test_warns_on_missing_type_or_role(self):
        """Test that missing type or role is handled gracefully."""
        from netbox_dio.validators.framework import RoleMatchDeviceTypeRule

        rule = RoleMatchDeviceTypeRule()

        # Missing device type
        device_dict = {"name": "dev", "site": "site", "device_type": None, "role": "role"}
        result = rule.apply(device_dict)
        assert result.passed is True

        # Missing role
        device_dict = {"name": "dev", "site": "site", "device_type": "type", "role": None}
        result = rule.apply(device_dict)
        assert result.passed is True


class TestValidationWithCustomFields:
    """Tests for validation involving custom fields."""

    def test_custom_field_validation(self):
        """Test validation logic based on custom fields."""

        class CustomFieldRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="custom_field_check",
                    description="Custom field validation",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.custom_fields:
                    # Check for specific custom field values
                    if device.custom_fields.get("warranty_expired", False):
                        return self.fail_result(
                            message="Warranty has expired",
                            field_name="custom_fields.warranty_expired",
                            value=True,
                        )
                return self.pass_result()

        rule = CustomFieldRule()

        # Without custom fields should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True

        # With valid custom fields should pass
        device = DiodeDevice(
            name="dev", site="site", device_type="type", role="role",
            custom_fields={"warranty_expired": False}
        )
        result = rule.apply(device)
        assert result.passed is True

        # With expired warranty should fail
        device = DiodeDevice(
            name="dev", site="site", device_type="type", role="role",
            custom_fields={"warranty_expired": True}
        )
        result = rule.apply(device)
        assert result.passed is False


class TestPipelineCrossField:
    """Tests for cross-field validation in pipelines."""

    def test_pipeline_with_multiple_cross_field_rules(self):
        """Test pipeline with multiple cross-field rules."""
        from netbox_dio.validators.framework import RequiredFieldsRule

        class StatusPlatformRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="status_platform",
                    description="Status-platform validation",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.status == "active" and not device.platform:
                    return self.fail_result(
                        message="Active devices should have a platform",
                        field_name="status",
                        value="active",
                    )
                return self.pass_result()

        pipeline = ValidatorPipeline()
        pipeline.add_rule(RequiredFieldsRule())
        pipeline.add_rule(StatusPlatformRule())

        # Device missing platform should fail
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="active")
        results = pipeline.run(device)
        # Should have at least one failure
        assert any(not r.passed for r in results)

    def test_aggregated_results(self):
        """Test getting aggregated results from cross-field validation."""
        pipeline = ValidatorPipeline()

        class Rule1(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="rule1",
                    description="Rule 1",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.name and len(device.name) < 3:
                    return self.fail_result("Name too short", field_name="name", value=device.name)
                return self.pass_result()

        class Rule2(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="rule2",
                    description="Rule 2",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.site and "invalid" in device.site.lower():
                    return self.fail_result("Invalid site", field_name="site", value=device.site)
                return self.pass_result()

        pipeline.add_rule(Rule1())
        pipeline.add_rule(Rule2())

        device = DiodeDevice(name="ab", site="invalid-site", device_type="type", role="role")
        results = pipeline.run(device)

        assert len(results) == 2
        failed_results = [r for r in results if not r.passed]
        assert len(failed_results) == 2
        assert failed_results[0].field_name == "name"
        assert failed_results[1].field_name == "site"


class TestValidationWithPipelineFilters:
    """Tests for filtering cross-field validation results."""

    def test_filter_cross_field_results(self):
        """Test filtering cross-field validation results."""
        pipeline = ValidatorPipeline(severity_filter=Severity.WARNING)

        class WarningRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="warn",
                    description="Warning",
                    severity=Severity.WARNING,
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                return self.fail_result(
                    "Warning",
                    field_name="test",
                    value="test",
                )

        pipeline.add_rule(WarningRule())
        results = pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert len(results) == 1
        assert results[0].severity == Severity.WARNING

    def test_empty_results_with_strict_filter(self):
        """Test that strict filtering produces empty results."""
        pipeline = ValidatorPipeline(severity_filter=Severity.ERROR)

        class WarningRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="warn",
                    description="Warning",
                    severity=Severity.WARNING,
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                return self.fail_result("Warning", field_name="test", value="test")

        pipeline.add_rule(WarningRule())
        results = pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert len(results) == 0

"""Tests for custom validation rules.

This module tests the ability to create and register custom validation rules.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.validators import Severity, ValidatorPipeline, ValidationResult, ValidationRule
from netbox_dio.validators.framework import RuleRegistry


class CustomRule(ValidationRule):
    """A custom validation rule for testing."""

    def __init__(self) -> None:
        super().__init__(
            name="custom_check",
            description="Custom check rule",
            severity=Severity.WARNING,
        )

    def apply(self, device: DiodeDevice) -> ValidationResult:
        """Apply custom validation logic."""
        # Check if device name contains specific pattern
        if device.name and "invalid" in device.name.lower():
            return self.fail_result(
                message="Device name contains 'invalid'",
                field_name="name",
                value=device.name,
            )
        return self.pass_result()


class TestCustomRuleRegistration:
    """Tests for registering custom rules."""

    def test_register_custom_rule(self):
        """Test registering a custom rule."""
        registry = RuleRegistry.get_instance()
        rule = CustomRule()
        registry.register(rule)
        assert registry.get("custom_check") == rule

    def test_register_non_rule_raises(self):
        """Test that registering a non-rule object raises an error."""
        registry = RuleRegistry.get_instance()
        with pytest.raises(ValueError, match="must be a ValidationRule"):
            registry.register("not a rule")

    def test_custom_rule_severity(self):
        """Test that custom rules can set their own severity."""
        rule = CustomRule()
        assert rule.severity == Severity.WARNING


class TestCustomRuleExecution:
    """Tests for executing custom rules."""

    def test_passes_valid_device(self):
        """Test that a valid device passes the custom rule."""
        rule = CustomRule()
        device = DiodeDevice(name="valid-device", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is True

    def test_fails_invalid_device(self):
        """Test that an invalid device fails the custom rule."""
        rule = CustomRule()
        device = DiodeDevice(name="invalid-device", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.passed is False
        assert "invalid" in result.error_message.lower()
        assert "name" == result.field_name

    def test_custom_metadata(self):
        """Test that custom rules can add metadata."""
        class CustomRuleWithMetadata(ValidationRule):
            def __init__(self) -> None:
                super().__init__(
                    name="custom_metadata",
                    description="Rule with metadata",
                )

            def apply(self, device: DiodeDevice) -> ValidationResult:
                result = self.fail_result(
                    message="Custom error",
                    field_name="custom",
                    value="test",
                )
                result.metadata = {"custom_field": "value", "count": 42}
                return result

        rule = CustomRuleWithMetadata()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        result = rule.apply(device)
        assert result.metadata["custom_field"] == "value"
        assert result.metadata["count"] == 42


class TestPipelineWithCustomRules:
    """Tests for pipelines with custom rules."""

    def test_pipeline_with_custom_rule(self):
        """Test using a custom rule in a pipeline."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="test_rule",
                    description="Test rule",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                if device.name and "bad" in device.name.lower():
                    return self.fail_result("Bad name", field_name="name", value=device.name)
                return self.pass_result()

        pipeline.add_rule(TestRule())
        device = DiodeDevice(name="dev-bad-name", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert len(results) == 1
        assert results[0].passed is False

    def test_multiple_custom_rules(self):
        """Test running multiple custom rules."""
        pipeline = ValidatorPipeline()

        class Rule1(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="rule1",
                    description="Rule 1",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                return self.fail_result("Rule 1 failed", field_name="name", value=device.name) if device.name == "fail1" else self.pass_result()

        class Rule2(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="rule2",
                    description="Rule 2",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                return self.fail_result("Rule 2 failed", field_name="name", value=device.name) if device.name == "fail2" else self.pass_result()

        pipeline.add_rule(Rule1())
        pipeline.add_rule(Rule2())

        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_custom_rule_in_pipeline_with_builtin(self):
        """Test mixing custom and built-in rules."""
        from netbox_dio.validators.framework import RequiredFieldsRule

        pipeline = ValidatorPipeline()

        class CustomRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="custom",
                    description="Custom rule",
                )
            def apply(self, device: DiodeDevice) -> ValidationResult:
                return self.pass_result()

        pipeline.add_rule(RequiredFieldsRule())
        pipeline.add_rule(CustomRule())

        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert len(results) == 2
        assert all(r.passed for r in results)


class TestRuleOrdering:
    """Tests for rule ordering in pipelines."""

    def test_rules_run_in_order(self):
        """Test that rules run in the order they were added."""
        pipeline = ValidatorPipeline()

        run_order = []

        class OrderedRule(ValidationRule):
            def __init__(self, name: str) -> None:
                super().__init__(name=name, description=f"Rule {name}")
                self.order_name = name

            def apply(self, device: DiodeDevice) -> ValidationResult:
                run_order.append(self.order_name)
                return self.pass_result()

        pipeline.add_rule(OrderedRule("first"))
        pipeline.add_rule(OrderedRule("second"))
        pipeline.add_rule(OrderedRule("third"))

        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        pipeline.run(device)

        assert run_order == ["first", "second", "third"]


class TestRuleFiltering:
    """Tests for filtering rules by severity."""

    def test_filter_by_warning(self):
        """Test filtering to include only WARNING and ERROR severity."""
        from netbox_dio.validators.framework import ValidStatusRule, NameLengthRule

        pipeline = ValidatorPipeline(severity_filter=Severity.WARNING)
        pipeline.add_rule(ValidStatusRule())
        pipeline.add_rule(NameLengthRule())

        device_dict = {"name": "x" * 100, "site": "site", "device_type": "type", "role": "role", "status": "invalid"}
        results = pipeline.run(device_dict)

        # Should include WARNING (NameLength) and ERROR (ValidStatus), but not INFO-level
        # (though there are no INFO rules in this test)
        assert len(results) >= 1
        for result in results:
            assert result.severity in (Severity.WARNING, Severity.ERROR)

    def test_filter_by_error(self):
        """Test filtering to include only ERROR severity."""
        from netbox_dio.validators.framework import NameLengthRule, SerialLengthRule

        pipeline = ValidatorPipeline(severity_filter=Severity.ERROR)
        # NameLengthRule is ERROR, SerialLengthRule is WARNING
        pipeline.add_rule(NameLengthRule())  # ERROR
        pipeline.add_rule(SerialLengthRule())  # WARNING

        device_dict = {"name": "x" * 100, "site": "site", "device_type": "type", "role": "role"}
        results = pipeline.run(device_dict)
        # Only NameLengthRule (ERROR) should pass, SerialLengthRule (WARNING) should be filtered out
        assert len(results) == 1
        assert results[0].severity == Severity.ERROR


# Import for class definitions
from netbox_dio.validators import ValidationResult
from netbox_dio.validators.framework import ValidationRule

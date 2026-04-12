"""Tests for the validation framework core classes.

This module tests the ValidationRule base class, RuleRegistry,
and ValidatorPipeline orchestration.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.validators import (
    ValidationResult,
    ValidationRule,
    RuleRegistry,
    ValidatorPipeline,
    Severity,
)


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            rule_name="test_rule",
            rule_description="Test rule description",
            severity=Severity.ERROR,
            passed=True,
        )
        assert result.rule_name == "test_rule"
        assert result.rule_description == "Test rule description"
        assert result.severity == Severity.ERROR
        assert result.passed is True

    def test_with_optional_fields(self):
        """Test creating a result with optional fields."""
        result = ValidationResult(
            rule_name="test_rule",
            rule_description="Test rule",
            severity=Severity.WARNING,
            passed=False,
            field_name="name",
            value="invalid-name",
            error_message="Name is invalid",
        )
        assert result.field_name == "name"
        assert result.value == "invalid-name"
        assert result.error_message == "Name is invalid"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult(
            rule_name="test_rule",
            rule_description="Test rule",
            severity=Severity.INFO,
            passed=True,
            metadata={"key": "value"},
        )
        result_dict = result.to_dict()
        assert result_dict["rule_name"] == "test_rule"
        assert result_dict["severity"] == "info"
        assert result_dict["passed"] is True
        assert result_dict["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """Test creating result from dictionary."""
        data = {
            "rule_name": "test_rule",
            "rule_description": "Test rule",
            "severity": "warning",
            "passed": False,
            "field_name": "name",
            "value": "test",
            "error_message": "Test error",
            "metadata": {"extra": "data"},
        }
        result = ValidationResult.from_dict(data)
        assert result.rule_name == "test_rule"
        assert result.severity == Severity.WARNING
        assert result.passed is False
        assert result.field_name == "name"
        assert result.metadata == {"extra": "data"}


class TestValidationRule:
    """Tests for the ValidationRule base class."""

    def test_abstract_class(self):
        """Test that ValidationRule is an abstract class."""
        with pytest.raises(TypeError):
            ValidationRule("name", "description")

    def test_pass_result(self):
        """Test the pass_result helper method."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("test", "Test rule")
        result = rule.apply(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert result.passed is True
        assert result.severity == Severity.ERROR

    def test_fail_result(self):
        """Test the fail_result helper method."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.fail_result("Error message", "field", "value")

        rule = TestRule("test", "Test rule", severity=Severity.WARNING)
        result = rule.apply(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert result.passed is False
        assert result.severity == Severity.WARNING
        assert result.error_message == "Error message"
        assert result.field_name == "field"
        assert result.value == "value"

    def test_name_validation_lowercase(self):
        """Test that rule names must be lowercase."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()
        with pytest.raises(ValueError, match="snake_case"):
            TestRule("UPPERCASE", "description")

    def test_name_validation_starts_with_letter(self):
        """Test that rule names must start with a letter."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()
        with pytest.raises(ValueError, match="snake_case"):
            TestRule("_invalid", "description")

    def test_name_validation_no_special_chars(self):
        """Test that rule names can only contain alphanumeric and underscore."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()
        with pytest.raises(ValueError, match="snake_case"):
            TestRule("invalid-name", "description")

    def test_repr(self):
        """Test the repr method."""
        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("test_rule", "Test rule", severity=Severity.INFO)
        assert "TestRule" in repr(rule)
        assert "test_rule" in repr(rule)
        assert "info" in repr(rule)


class TestRuleRegistry:
    """Tests for the RuleRegistry singleton."""

    def test_singleton_instance(self):
        """Test that RuleRegistry is a singleton."""
        registry1 = RuleRegistry.get_instance()
        registry2 = RuleRegistry.get_instance()
        assert registry1 is registry2

    def test_register_rule(self):
        """Test registering a rule."""
        registry = RuleRegistry.get_instance()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("test_rule", "Test rule")
        registry.register(rule)
        assert registry.get("test_rule") == rule

    def test_register_duplicate_raises(self):
        """Test that registering a duplicate rule raises an error."""
        registry = RuleRegistry.get_instance()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("duplicate", "Test rule")
        registry.register(rule)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(rule)

    def test_get_rule(self):
        """Test getting a rule by name."""
        registry = RuleRegistry.get_instance()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("get_test", "Get test rule")
        registry.register(rule)

        retrieved = registry.get("get_test")
        assert retrieved == rule

    def test_get_nonexistent_rule(self):
        """Test getting a non-existent rule returns None."""
        registry = RuleRegistry.get_instance()
        assert registry.get("nonexistent") is None

    def test_get_all_rules(self):
        """Test getting all registered rules."""
        registry = RuleRegistry.get_instance()
        registry.clear()  # Clear any existing rules

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        registry.register(TestRule("rule1", "Rule 1"))
        registry.register(TestRule("rule2", "Rule 2"))

        all_rules = registry.get_all()
        assert len(all_rules) == 2
        assert "rule1" in all_rules
        assert "rule2" in all_rules

    def test_unregister_rule(self):
        """Test unregistering a rule."""
        registry = RuleRegistry.get_instance()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rule = TestRule("unregister_test", "Unregister test rule")
        registry.register(rule)
        assert registry.has_rule("unregister_test")

        removed = registry.unregister("unregister_test")
        assert removed is True
        assert registry.get("unregister_test") is None

    def test_unregister_nonexistent(self):
        """Test unregistering a non-existent rule returns False."""
        registry = RuleRegistry.get_instance()
        assert registry.unregister("nonexistent") is False

    def test_has_rule(self):
        """Test checking if a rule is registered."""
        registry = RuleRegistry.get_instance()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        registry.register(TestRule("has_test", "Has test rule"))
        assert registry.has_rule("has_test")
        assert not registry.has_rule("not_registered")


class TestValidatorPipeline:
    """Tests for the ValidatorPipeline class."""

    def test_add_rule(self):
        """Test adding a rule to the pipeline."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule("pipeline_test", "Pipeline test rule"))
        assert len(pipeline.rules) == 1

    def test_add_rules(self):
        """Test adding multiple rules."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        rules = [
            TestRule("rule1", "Rule 1"),
            TestRule("rule2", "Rule 2"),
            TestRule("rule3", "Rule 3"),
        ]
        pipeline.add_rules(rules)
        assert len(pipeline.rules) == 3

    def test_method_chaining(self):
        """Test method chaining for pipeline operations."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule("test1", "Test 1")).add_rule(TestRule("test2", "Test 2"))
        assert len(pipeline.rules) == 2

    def test_run_rules(self):
        """Test running the pipeline on a device."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="test_rule",
                    description="Test rule",
                )
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule())
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert len(results) == 1
        assert results[0].passed is True

    def test_timing_metadata(self):
        """Test that timing metadata is recorded."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="test_rule",
                    description="Test rule",
                )
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule())
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert "timing_ms" in results[0].metadata
        assert results[0].metadata["timing_ms"] > 0

    def test_get_results(self):
        """Test getting results from the pipeline."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule("test", "Test"))
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        results = pipeline.get_results()
        assert len(results) == 1

    def test_get_timing(self):
        """Test getting timing information."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule("timing_test", "Timing test"))
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        timing = pipeline.get_timing()
        assert "timing_test" in timing
        assert timing["timing_test"] > 0

    def test_get_passed_count(self):
        """Test getting passed rule count."""
        pipeline = ValidatorPipeline()

        class PassRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        class FailRule(ValidationRule):
            def apply(self, device):
                return self.fail_result("Failed")

        pipeline.add_rule(PassRule("pass1", "Pass 1"))
        pipeline.add_rule(PassRule("pass2", "Pass 2"))
        pipeline.add_rule(FailRule("fail1", "Fail 1"))
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert pipeline.get_passed_count() == 2
        assert pipeline.get_failed_count() == 1

    def test_get_severity_counts(self):
        """Test getting severity counts."""
        pipeline = ValidatorPipeline()

        class ErrorRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="err",
                    description="Error",
                    severity=Severity.ERROR,
                )
            def apply(self, device):
                return self.fail_result("Error")

        class WarningRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="warn",
                    description="Warning",
                    severity=Severity.WARNING,
                )
            def apply(self, device):
                return self.fail_result("Warning")

        class InfoRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="info",
                    description="Info",
                    severity=Severity.INFO,
                )
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(ErrorRule())
        pipeline.add_rule(WarningRule())
        pipeline.add_rule(InfoRule())
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        assert pipeline.get_error_count() == 1
        assert pipeline.get_warning_count() == 1
        assert pipeline.get_info_count() == 1

    def test_clear(self):
        """Test clearing the pipeline."""
        pipeline = ValidatorPipeline()

        class TestRule(ValidationRule):
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(TestRule("test", "Test"))
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        pipeline.clear()
        assert len(pipeline.rules) == 0
        assert len(pipeline.results) == 0

    def test_severity_filter(self):
        """Test filtering results by severity."""
        pipeline = ValidatorPipeline(severity_filter=Severity.WARNING)

        class ErrorRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="err",
                    description="Error",
                    severity=Severity.ERROR,
                )
            def apply(self, device):
                return self.fail_result("Error")

        class WarningRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="warn",
                    description="Warning",
                    severity=Severity.WARNING,
                )
            def apply(self, device):
                return self.fail_result("Warning")

        class InfoRule(ValidationRule):
            def __init__(self):
                super().__init__(
                    name="info",
                    description="Info",
                    severity=Severity.INFO,
                )
            def apply(self, device):
                return self.pass_result()

        pipeline.add_rule(ErrorRule())
        pipeline.add_rule(WarningRule())
        pipeline.add_rule(InfoRule())
        pipeline.run(DiodeDevice(name="dev", site="site", device_type="type", role="role"))
        # Should only include WARNING and ERROR (excluding INFO)
        results = pipeline.get_results()
        assert len(results) == 2
        assert all(r.severity in (Severity.ERROR, Severity.WARNING) for r in results)

    def test_rule_exception_handling(self):
        """Test handling of rule execution exceptions."""
        pipeline = ValidatorPipeline()

        class FailingRule(ValidationRule):
            def apply(self, device):
                raise ValueError("Rule execution failed")

        pipeline.add_rule(FailingRule("fail", "Failing rule"))
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert len(results) == 1
        assert results[0].passed is False
        assert "Rule execution error" in results[0].error_message


class TestBuiltInRules:
    """Tests for built-in validation rules."""

    def test_required_fields_rule(self):
        """Test the required fields rule."""
        from netbox_dio.validators.framework import RequiredFieldsRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(RequiredFieldsRule())

        # Device with all required fields should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert results[0].passed is True

        # Device missing required field should fail
        device_dict = {"name": "dev", "site": "site", "device_type": "type"}  # missing role
        results = pipeline.run(device_dict)
        assert results[0].passed is False
        assert "required fields missing" in results[0].error_message.lower()

    def test_valid_status_rule(self):
        """Test the valid status rule."""
        from netbox_dio.validators.framework import ValidStatusRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(ValidStatusRule())

        # Valid status should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", status="active")
        results = pipeline.run(device)
        assert results[0].passed is True

        # Invalid status should fail
        device_dict = {"name": "dev", "site": "site", "device_type": "type", "role": "role", "status": "invalid"}
        results = pipeline.run(device_dict)
        assert results[0].passed is False
        assert "invalid status" in results[0].error_message.lower()

    def test_name_length_rule(self):
        """Test the name length rule."""
        from netbox_dio.validators.framework import NameLengthRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(NameLengthRule())

        # Valid name should pass
        device = DiodeDevice(name="valid-name", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert results[0].passed is True

        # Too short name should fail
        device = DiodeDevice(name="", site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert results[0].passed is False

        # Too long name should fail
        device = DiodeDevice(name="x" * 100, site="site", device_type="type", role="role")
        results = pipeline.run(device)
        assert results[0].passed is False

    def test_serial_length_rule(self):
        """Test the serial length rule."""
        from netbox_dio.validators.framework import SerialLengthRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(SerialLengthRule())

        # Valid serial should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial="ABC123")
        results = pipeline.run(device)
        assert results[0].passed is True

        # Too long serial should fail
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", serial="x" * 100)
        results = pipeline.run(device)
        assert results[0].passed is False

    def test_asset_tag_length_rule(self):
        """Test the asset tag length rule."""
        from netbox_dio.validators.framework import AssetTagLengthRule

        pipeline = ValidatorPipeline()
        pipeline.add_rule(AssetTagLengthRule())

        # Valid asset tag should pass
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag="TAG123")
        results = pipeline.run(device)
        assert results[0].passed is True

        # Too long asset tag should fail
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role", asset_tag="x" * 100)
        results = pipeline.run(device)
        assert results[0].passed is False

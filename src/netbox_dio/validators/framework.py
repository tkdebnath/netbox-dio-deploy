"""Validation framework base classes and registry.

This module provides the core classes for the validation framework:
ValidationRule (base class), RuleRegistry (storage), and ValidatorPipeline (orchestration).
"""

from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Callable, Optional, Type, TypeVar

from ..exceptions import DiodeValidationError
from ..models import DiodeDevice
from . import Severity


@dataclass
class ValidationResult:
    """Result of a single validation rule execution.

    Captures the outcome of running a validation rule against a device,
    including whether it passed, any error messages, and metadata.

    Attributes:
        rule_name: Unique identifier for the rule
        rule_description: Human-readable description of the rule
        severity: How severe the result is (error, warning, info)
        passed: Whether the rule passed (True) or failed (False)
        field: The field that was validated (if applicable)
        value: The value that was validated (if applicable)
        error_message: Error message if the rule failed
        metadata: Additional metadata (timing, rule-specific data)
    """

    rule_name: str
    rule_description: str
    severity: Severity
    passed: bool
    field_name: Optional[str] = None
    value: Any = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def severity_value(self) -> str:
        """Get severity as a string."""
        return self.severity.value

    def to_dict(self) -> dict:
        """Convert result to a dictionary."""
        return {
            "rule_name": self.rule_name,
            "rule_description": self.rule_description,
            "severity": self.severity_value,
            "passed": self.passed,
            "field": self.field_name,
            "value": self.value,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ValidationResult:
        """Create a ValidationResult from a dictionary."""
        severity_str = data.get("severity", "info")
        severity = Severity(severity_str)
        return cls(
            rule_name=data.get("rule_name", "unknown"),
            rule_description=data.get("rule_description", ""),
            severity=severity,
            passed=data.get("passed", False),
            field_name=data.get("field_name", data.get("field")),
            value=data.get("value"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )


class ValidationRule(ABC):
    """Abstract base class for all validation rules.

    Subclasses must implement the apply() method to perform validation
    logic on a DiodeDevice.

    Attributes:
        name: Unique identifier for the rule (snake_case)
        description: Human-readable description of what the rule checks
        severity: Severity level for this rule (default: error)
    """

    def __init__(
        self, name: str, description: str, severity: Severity = Severity.ERROR
    ) -> None:
        """Initialize a validation rule.

        Args:
            name: Unique identifier for the rule (should be snake_case)
            description: Human-readable description
            severity: Severity level (error, warning, info)
        """
        if not name:
            raise ValueError("Rule name cannot be empty")
        if not re.match(r"^[a-z][a-z0-9_]*$", name):
            raise ValueError(
                f"Rule name must be snake_case starting with letter: {name}"
            )

        self.name = name
        self.description = description
        self.severity = severity

    @abstractmethod
    def apply(self, device: DiodeDevice) -> ValidationResult:
        """Apply the validation rule to a device.

        Args:
            device: The DiodeDevice to validate

        Returns:
            ValidationResult with the outcome of the validation
        """
        pass

    def pass_result(self, message: Optional[str] = None) -> ValidationResult:
        """Create a passing result.

        Args:
            message: Optional success message

        Returns:
            ValidationResult with passed=True
        """
        return ValidationResult(
            rule_name=self.name,
            rule_description=self.description,
            severity=self.severity,
            passed=True,
            error_message=message,
        )

    def fail_result(self, message: str, field_name: Optional[str] = None, value: Any = None) -> ValidationResult:
        """Create a failing result.

        Args:
            message: Error message explaining the failure
            field_name: The field that failed (optional)
            value: The value that failed (optional)

        Returns:
            ValidationResult with passed=False
        """
        return ValidationResult(
            rule_name=self.name,
            rule_description=self.description,
            severity=self.severity,
            passed=False,
            field_name=field_name,
            value=value,
            error_message=message,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', severity={self.severity.value})"


class RuleRegistry:
    """Global registry for validation rules.

    Stores registered rules and provides lookup by name.
    Uses a singleton pattern to ensure a single registry instance.

    Attributes:
        rules: Dictionary mapping rule names to rule instances
    """

    _instance: Optional[RuleRegistry] = None
    _lock: Lock = Lock()

    def __new__(cls) -> RuleRegistry:
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the rule registry."""
        if self._initialized:
            return

        self._initialized = True
        self.rules: dict[str, ValidationRule] = {}
        self._built_in_names: set[str] = set()
        self._lock = Lock()

    @classmethod
    def get_instance(cls) -> RuleRegistry:
        """Get the singleton RuleRegistry instance.

        Returns:
            The singleton RuleRegistry
        """
        return cls()

    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule.

        Args:
            rule: The rule to register

        Raises:
            ValueError: If rule name is already registered or invalid
        """
        if not isinstance(rule, ValidationRule):
            raise ValueError(
                f"Rule must be a ValidationRule, got {type(rule).__name__}"
            )

        with self._lock:
            if rule.name in self.rules:
                raise ValueError(f"Rule '{rule.name}' is already registered")
            if not re.match(r"^[a-z][a-z0-9_]*$", rule.name):
                raise ValueError(
                    f"Rule name must be snake_case starting with letter: {rule.name}"
                )
            self.rules[rule.name] = rule

    def get(self, rule_name: str) -> Optional[ValidationRule]:
        """Get a registered rule by name.

        Args:
            rule_name: The name of the rule to retrieve

        Returns:
            The rule instance, or None if not found
        """
        return self.rules.get(rule_name)

    def get_all(self) -> dict[str, ValidationRule]:
        """Get all registered rules.

        Returns:
            Dictionary mapping rule names to rule instances
        """
        return dict(self.rules)

    def unregister(self, rule_name: str) -> bool:
        """Remove a rule from the registry.

        Args:
            rule_name: The name of the rule to remove

        Returns:
            True if the rule was removed, False if not found
        """
        with self._lock:
            if rule_name in self.rules:
                del self.rules[rule_name]
                return True
            return False

    def has_rule(self, rule_name: str) -> bool:
        """Check if a rule is registered.

        Args:
            rule_name: The name of the rule

        Returns:
            True if the rule is registered, False otherwise
        """
        return rule_name in self.rules

    def clear(self) -> None:
        """Clear all registered rules."""
        with self._lock:
            self.rules = {}
            self._built_in_names = set()

    def register_built_in(self, rule: ValidationRule) -> None:
        """Register a built-in rule.

        Built-in rules can be overridden by user rules.

        Args:
            rule: The built-in rule to register
        """
        self._built_in_names.add(rule.name)
        self.register(rule)


class ValidatorPipeline:
    """Orchestrates validation rule execution.

    Manages a collection of validation rules and executes them
    against a device, collecting results and supporting severity filtering.

    Attributes:
        rules: List of rule instances to execute
        severity_filter: Optional filter for result severity
        results: List of collected validation results
    """

    def __init__(self, severity_filter: Optional[Severity] = None) -> None:
        """Initialize the validator pipeline.

        Args:
            severity_filter: Optional severity filter (only include this severity or higher)
        """
        self.rules: list[ValidationRule] = []
        self.severity_filter = severity_filter
        self.results: list[ValidationResult] = []
        self._timing: dict[str, float] = {}

    def add_rule(self, rule: ValidationRule) -> "ValidatorPipeline":
        """Add a rule to the pipeline.

        Args:
            rule: The rule to add

        Returns:
            Self for method chaining
        """
        self.rules.append(rule)
        return self

    def add_rules(self, rules: list[ValidationRule]) -> "ValidatorPipeline":
        """Add multiple rules to the pipeline.

        Args:
            rules: List of rules to add

        Returns:
            Self for method chaining
        """
        self.rules.extend(rules)
        return self

    def set_severity_filter(self, severity: Severity) -> "ValidatorPipeline":
        """Set severity filter for results.

        Only results with this severity or higher will be included.

        Args:
            severity: Minimum severity level

        Returns:
            Self for method chaining
        """
        self.severity_filter = severity
        return self

    def _should_include(self, result: ValidationResult) -> bool:
        """Check if a result should be included based on severity filter.

        Args:
            result: The validation result

        Returns:
            True if the result should be included
        """
        if self.severity_filter is None:
            return True

        severity_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
        return severity_order.get(result.severity, 2) <= severity_order.get(self.severity_filter, 2)

    def run(self, device: DiodeDevice) -> list[ValidationResult]:
        """Execute all rules against a device.

        Args:
            device: The DiodeDevice to validate

        Returns:
            List of validation results
        """
        self.results = []
        self._timing = {}

        for rule in self.rules:
            start_time = time.time()
            try:
                result = rule.apply(device)
                result.metadata["timing_ms"] = (time.time() - start_time) * 1000
                self._timing[rule.name] = result.metadata["timing_ms"]
            except Exception as e:
                # Rule execution failed - create an error result
                result = ValidationResult(
                    rule_name=rule.name,
                    rule_description=rule.description,
                    severity=Severity.ERROR,
                    passed=False,
                    error_message=f"Rule execution error: {str(e)}",
                    metadata={"timing_ms": (time.time() - start_time) * 1000},
                )
            self.results.append(result)

        # Filter results based on severity
        if self.severity_filter:
            self.results = [r for r in self.results if self._should_include(r)]

        return self.results

    def get_results(self) -> list[ValidationResult]:
        """Get the collected results from the last run.

        Returns:
            List of validation results
        """
        return self.results

    def get_timing(self) -> dict[str, float]:
        """Get timing information for rule execution.

        Returns:
            Dictionary mapping rule names to execution time in milliseconds
        """
        return dict(self._timing)

    def get_passed_count(self) -> int:
        """Get the count of passed rules.

        Returns:
            Number of rules that passed
        """
        return sum(1 for r in self.results if r.passed)

    def get_failed_count(self) -> int:
        """Get the count of failed rules.

        Returns:
            Number of rules that failed
        """
        return sum(1 for r in self.results if not r.passed)

    def get_error_count(self) -> int:
        """Get the count of error-level results.

        Returns:
            Number of error-level results
        """
        return sum(1 for r in self.results if r.severity == Severity.ERROR)

    def get_warning_count(self) -> int:
        """Get the count of warning-level results.

        Returns:
            Number of warning-level results
        """
        return sum(1 for r in self.results if r.severity == Severity.WARNING)

    def get_info_count(self) -> int:
        """Get the count of info-level results.

        Returns:
            Number of info-level results
        """
        return sum(1 for r in self.results if r.severity == Severity.INFO)

    def clear(self) -> None:
        """Clear all rules and results."""
        self.rules = []
        self.results = []
        self._timing = {}


# Built-in validation rules


class RequiredFieldsRule(ValidationRule):
    """Validate that required fields are present on a device."""

    def __init__(self) -> None:
        super().__init__(
            name="required_fields",
            description="Check that all required fields (name, site, device_type, role) are present",
            severity=Severity.ERROR,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the required fields check.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        # Handle both DiodeDevice and dict
        if isinstance(device, dict):
            name = device.get("name")
            site = device.get("site")
            device_type = device.get("device_type")
            role = device.get("role")
        else:
            name = getattr(device, "name", None)
            site = getattr(device, "site", None)
            device_type = getattr(device, "device_type", None)
            role = getattr(device, "role", None)

        missing = []
        if not name:
            missing.append("name")
        if not site:
            missing.append("site")
        if not device_type:
            missing.append("device_type")
        if not role:
            missing.append("role")

        if missing:
            return self.fail_result(
                message=f"Required fields missing: {', '.join(missing)}",
                field_name="required_fields",
                value=missing,
            )

        return self.pass_result()


class ValidStatusRule(ValidationRule):
    """Validate that device status is one of the allowed values."""

    ALLOWED_STATUSES = {"active", "offline", "planned"}

    def __init__(self) -> None:
        super().__init__(
            name="valid_status",
            description="Validate that device status is one of: active, offline, planned",
            severity=Severity.ERROR,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the status validation.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        # Handle both dict and DiodeDevice
        if isinstance(device, dict):
            status = device.get("status")
        else:
            status = getattr(device, "status", None)

        if status is None:
            return self.pass_result()

        if status not in self.ALLOWED_STATUSES:
            return self.fail_result(
                message=f"Invalid status '{status}'. Must be one of: {', '.join(sorted(self.ALLOWED_STATUSES))}",
                field_name="status",
                value=status,
            )

        return self.pass_result()


class NameLengthRule(ValidationRule):
    """Validate that device name is within the allowed length."""

    MIN_LENGTH = 1
    MAX_LENGTH = 64

    def __init__(self) -> None:
        super().__init__(
            name="name_length",
            description="Validate that device name is between 1 and 64 characters",
            severity=Severity.ERROR,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the name length validation.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        name = getattr(device, "name", None) or ""
        length = len(name)

        if length < self.MIN_LENGTH:
            return self.fail_result(
                message=f"Device name is too short (minimum {self.MIN_LENGTH} character(s))",
                field_name="name",
                value=name,
            )

        if length > self.MAX_LENGTH:
            return self.fail_result(
                message=f"Device name exceeds maximum length of {self.MAX_LENGTH} characters (got {length})",
                field_name="name",
                value=name,
            )

        return self.pass_result()


class SerialLengthRule(ValidationRule):
    """Validate that serial number is within the allowed length."""

    MAX_LENGTH = 64

    def __init__(self) -> None:
        super().__init__(
            name="serial_length",
            description="Validate that serial number is at most 64 characters",
            severity=Severity.WARNING,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the serial length validation.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        serial = getattr(device, "serial", None)
        if serial is None:
            return self.pass_result()

        if len(serial) > self.MAX_LENGTH:
            return self.fail_result(
                message=f"Serial number exceeds maximum length of {self.MAX_LENGTH} characters (got {len(serial)})",
                field_name="serial",
                value=serial,
            )

        return self.pass_result()


class AssetTagLengthRule(ValidationRule):
    """Validate that asset tag is within the allowed length."""

    MAX_LENGTH = 64

    def __init__(self) -> None:
        super().__init__(
            name="asset_tag_length",
            description="Validate that asset tag is at most 64 characters",
            severity=Severity.WARNING,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the asset tag length validation.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        asset_tag = getattr(device, "asset_tag", None)
        if asset_tag is None:
            return self.pass_result()

        if len(asset_tag) > self.MAX_LENGTH:
            return self.fail_result(
                message=f"Asset tag exceeds maximum length of {self.MAX_LENGTH} characters (got {len(asset_tag)})",
                field_name="asset_tag",
                value=asset_tag,
            )

        return self.pass_result()


class RoleMatchDeviceTypeRule(ValidationRule):
    """Validate that device role is appropriate for the device type.

    This is a placeholder for more sophisticated role validation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="role_match_device_type",
            description="Validate that device role is appropriate for the device type",
            severity=Severity.WARNING,
        )

    def apply(self, device: DiodeDevice | dict) -> ValidationResult:
        """Apply the role/device type matching check.

        Args:
            device: The DiodeDevice or dict to validate

        Returns:
            ValidationResult with the outcome
        """
        role = getattr(device, "role", None)
        device_type = getattr(device, "device_type", None)
        # This is a basic placeholder - in production, you might check
        # against a database of valid role-type combinations
        if not role or not device_type:
            return self.pass_result()

        # Basic check: ensure both have values
        return self.pass_result()


def get_builtin_rules() -> list[ValidationRule]:
    """Get all built-in validation rules.

    Returns:
        List of built-in rule instances
    """
    return [
        RequiredFieldsRule(),
        ValidStatusRule(),
        NameLengthRule(),
        SerialLengthRule(),
        AssetTagLengthRule(),
        RoleMatchDeviceTypeRule(),
    ]


def register_builtin_rules(registry: RuleRegistry) -> None:
    """Register all built-in rules with a registry.

    Args:
        registry: The RuleRegistry to register rules with
    """
    for rule in get_builtin_rules():
        registry.register_built_in(rule)

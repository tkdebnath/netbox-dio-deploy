"""Validation framework for Diode devices.

This module provides a custom validation rule framework that allows
users to register and execute domain-specific validation rules on Diode devices.

Usage:
    from netbox_dio import DiodeDevice
    from netbox_dio.validators import ValidationRule, RuleRegistry, ValidatorPipeline

    # Define a custom rule
    class CustomValidationRule(ValidationRule):
        def apply(self, device: DiodeDevice) -> ValidationResult:
            # Custom validation logic
            if device.name.startswith("invalid"):
                return self.fail("Device name must not start with 'invalid'")
            return self.pass()

    # Register and run
    registry = RuleRegistry.get_instance()
    registry.register(CustomValidationRule("custom_check", "Custom check rule"))

    pipeline = ValidatorPipeline()
    pipeline.add_rule(CustomValidationRule("custom_check", "Custom check rule"))
    results = pipeline.run(device)

    for result in results:
        if not result.passed:
            print(f"Validation failed: {result.error_message}")
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

# Import Severity first to avoid circular dependency
from .enums import Severity

# Import framework after Severity is defined
from .framework import (
    ValidationResult,
    ValidationRule,
    RuleRegistry,
    ValidatorPipeline,
)

__all__ = [
    "ValidationResult",
    "ValidationRule",
    "RuleRegistry",
    "ValidatorPipeline",
    "Severity",
]

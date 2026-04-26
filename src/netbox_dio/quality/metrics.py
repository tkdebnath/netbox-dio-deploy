"""Quality metrics calculations for Diode devices.

This module provides classes for calculating data completeness and validity
scores for network infrastructure devices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional



from ..exceptions import DiodeValidationError
from ..models import DiodeDevice
from ..validators import ValidationResult, Severity, ValidatorPipeline


@dataclass
class FieldQuality:
    """Quality metrics for a single field.

    Captures the quality of an individual field including whether it's
    present, valid, and a calculated score.

    Attributes:
        field_name: The name of the field
        present: Whether the field is present on the device
        valid: Whether the field value is valid
        value: The actual field value
        score: Quality score from 0.0 to 1.0
        issues: List of issues found with this field
    """

    field_name: str
    present: bool
    valid: bool
    value: Any
    score: float = 1.0
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to a dictionary."""
        return {
            "field_name": self.field_name,
            "present": self.present,
            "valid": self.valid,
            "value": self.value,
            "score": self.score,
            "issues": self.issues,
        }

    @classmethod
    def from_dict(cls, data: dict) -> FieldQuality:
        """Create a FieldQuality from a dictionary."""
        return cls(
            field_name=data["field_name"],
            present=data["present"],
            valid=data["valid"],
            value=data.get("value"),
            score=data.get("score", 1.0),
            issues=data.get("issues", []),
        )


@dataclass
class QualityMetrics:
    """Overall quality metrics for a device or batch.

    Captures the overall quality assessment including completeness,
    validity, and overall scores.

    Attributes:
        device_name: The name of the device
        completeness_score: Score for how complete the data is (0.0-1.0)
        validity_score: Score for how valid the data is (0.0-1.0)
        overall_score: Weighted average (70% validity, 30% completeness)
        timestamp: When the metrics were calculated
        field_breakdown: Per-field quality breakdown
        error_count: Number of errors found
        warning_count: Number of warnings found
        info_count: Number of info messages
    """

    device_name: str
    completeness_score: float
    validity_score: float
    overall_score: float
    timestamp: datetime
    field_breakdown: dict[str, FieldQuality]
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    def to_dict(self) -> dict:
        """Convert to a dictionary."""
        return {
            "device_name": self.device_name,
            "completeness_score": self.completeness_score,
            "validity_score": self.validity_score,
            "overall_score": self.overall_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "field_breakdown": {k: v.to_dict() for k, v in self.field_breakdown.items()},
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> QualityMetrics:
        """Create a QualityMetrics from a dictionary."""

        field_breakdown = {}
        for k, v in data.get("field_breakdown", {}).items():
            field_breakdown[k] = FieldQuality.from_dict(v)

        timestamp_str = data.get("timestamp")
        timestamp = None
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                timestamp = None

        return cls(
            device_name=data["device_name"],
            completeness_score=data["completeness_score"],
            validity_score=data["validity_score"],
            overall_score=data["overall_score"],
            timestamp=timestamp,
            field_breakdown=field_breakdown,
            error_count=data.get("error_count", 0),
            warning_count=data.get("warning_count", 0),
            info_count=data.get("info_count", 0),
        )

    @property
    def score_status(self) -> str:
        """Get the status based on overall score."""
        if self.overall_score >= 0.90:
            return "Excellent"
        elif self.overall_score >= 0.70:
            return "Good"
        elif self.overall_score >= 0.50:
            return "Fair"
        elif self.overall_score >= 0.30:
            return "Poor"
        else:
            return "Critical"


class CompletenessCalculator:
    """Calculate completeness score for a device.

    Completeness measures what percentage of expected fields are present.

    Attributes:
        required_fields: List of required field names
        optional_fields: List of optional field names
    """

    # Common required fields for network devices
    DEFAULT_REQUIRED = ["name", "site", "device_type", "role"]
    DEFAULT_OPTIONAL = [
        "serial",
        "asset_tag",
        "platform",
        "status",
        "custom_fields",
        "business_unit",
    ]

    def __init__(
        self,
        required_fields: Optional[list[str]] = None,
        optional_fields: Optional[list[str]] = None,
    ) -> None:
        """Initialize the completeness calculator.

        Args:
            required_fields: List of required field names (default: common network fields)
            optional_fields: List of optional field names
        """
        self.required_fields = required_fields or self.DEFAULT_REQUIRED
        self.optional_fields = optional_fields or self.DEFAULT_OPTIONAL

    def calculate(self, device: DiodeDevice) -> float:
        """Calculate completeness score.

        Args:
            device: The DiodeDevice to evaluate

        Returns:
            Score from 0.0 (no fields present) to 1.0 (all fields present)
        """
        device_dict = device.model_dump() if hasattr(device, "model_dump") else device.__dict__

        # Count required fields present
        required_present = sum(
            1 for field in self.required_fields if device_dict.get(field) is not None
        )

        # Count optional fields present
        optional_present = sum(
            1 for field in self.optional_fields if device_dict.get(field) is not None
        )

        # Calculate score: required fields weight more than optional
        total_required = len(self.required_fields)
        total_optional = len(self.optional_fields)

        if total_required == 0 and total_optional == 0:
            return 1.0

        # Weight: required fields count 2x more than optional
        weighted_present = required_present * 2 + optional_present
        weighted_total = total_required * 2 + total_optional

        return weighted_present / weighted_total

    def get_field_breakdown(self, device: DiodeDevice) -> dict[str, FieldQuality]:
        """Get per-field completeness breakdown.

        Args:
            device: The DiodeDevice to evaluate

        Returns:
            Dictionary mapping field names to FieldQuality instances
        """
        device_dict = device.model_dump() if hasattr(device, "model_dump") else device.__dict__
        breakdown: dict[str, FieldQuality] = {}

        # Required fields
        for field in self.required_fields:
            value = device_dict.get(field)
            present = value is not None
            breakdown[field] = FieldQuality(
                field_name=field,
                present=present,
                valid=present,  # For required fields, present means valid
                value=value,
                score=1.0 if present else 0.0,
                issues=["Missing required field"] if not present else [],
            )

        # Optional fields
        for field in self.optional_fields:
            value = device_dict.get(field)
            present = value is not None
            breakdown[field] = FieldQuality(
                field_name=field,
                present=present,
                valid=True,  # Optional fields are always valid when present
                value=value,
                score=1.0 if present else 0.0,
                issues=[] if present else ["Missing optional field"],
            )

        return breakdown


class ValidityCalculator:
    """Calculate validity score for a device.

    Validity measures what percentage of fields are valid based on
    validation results.

    Attributes:
        pipeline: ValidatorPipeline for running validation
    """

    def __init__(self, pipeline: Optional[ValidatorPipeline] = None) -> None:
        """Initialize the validity calculator.

        Args:
            pipeline: Optional ValidatorPipeline for running validation.
                     If None, creates a new pipeline with built-in rules.
        """
        if pipeline is None:
            from netbox_dio.validators.framework import get_builtin_rules
            pipeline = ValidatorPipeline()
            for rule in get_builtin_rules():
                pipeline.add_rule(rule)
        self.pipeline = pipeline

    def calculate(self, device: DiodeDevice) -> float:
        """Calculate validity score.

        Args:
            device: The DiodeDevice to validate

        Returns:
            Score from 0.0 (all fields invalid) to 1.0 (all fields valid)
        """
        results = self.pipeline.run(device)

        if not results:
            return 1.0

        # Count valid vs invalid results
        valid_count = sum(1 for r in results if r.passed)
        return valid_count / len(results)

    def get_results(self, device: DiodeDevice) -> list[ValidationResult]:
        """Get validation results for a device.

        Args:
            device: The DiodeDevice to validate

        Returns:
            List of validation results
        """
        return self.pipeline.run(device)


class QualityReporter:
    """Generate formatted quality reports.

    Provides methods for generating human-readable, JSON, and YAML
    quality reports for devices.

    Attributes:
        completeness_calc: CompletenessCalculator instance
        validity_calc: ValidityCalculator instance
    """

    def __init__(
        self,
        completeness_calc: Optional[CompletenessCalculator] = None,
        validity_calc: Optional[ValidityCalculator] = None,
    ) -> None:
        """Initialize the quality reporter.

        Args:
            completeness_calc: CompletenessCalculator instance
            validity_calc: ValidityCalculator instance
        """
        self.completeness_calc = completeness_calc or CompletenessCalculator()
        self.validity_calc = validity_calc or ValidityCalculator()

    def calculate_metrics(self, device: DiodeDevice) -> QualityMetrics:
        """Calculate quality metrics for a device.

        Args:
            device: The DiodeDevice to evaluate

        Returns:
            QualityMetrics with complete quality assessment
        """
        # Calculate scores
        completeness = self.completeness_calc.calculate(device)
        validity = self.validity_calc.calculate(device)

        # Weighted overall score: 70% validity, 30% completeness
        overall = (validity * 0.7) + (completeness * 0.3)

        # Get field breakdown
        field_breakdown = self.completeness_calc.get_field_breakdown(device)

        # Count results by severity
        results = self.validity_calc.get_results(device)
        error_count = sum(1 for r in results if r.severity == Severity.ERROR)
        warning_count = sum(1 for r in results if r.severity == Severity.WARNING)
        info_count = sum(1 for r in results if r.severity == Severity.INFO)

        return QualityMetrics(
            device_name=device.name,
            completeness_score=round(completeness, 4),
            validity_score=round(validity, 4),
            overall_score=round(overall, 4),
            timestamp=datetime.now(),
            field_breakdown=field_breakdown,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
        )

    def generate_report(self, device: DiodeDevice, metrics: QualityMetrics) -> str:
        """Generate a human-readable report.

        Args:
            device: The DiodeDevice
            metrics: QualityMetrics for the device

        Returns:
            Human-readable report string
        """
        lines = [
            f"{'=' * 60}",
            f"Quality Report for Device: {metrics.device_name}",
            f"{'=' * 60}",
            "",
            "Overall Scores:",
            f"  Completeness: {metrics.completeness_score:.1%}",
            f"  Validity:     {metrics.validity_score:.1%}",
            f"  Overall:      {metrics.overall_score:.1%}",
            f"  Status:       {metrics.score_status}",
            "",
            "Result Counts:",
            f"  Errors:   {metrics.error_count}",
            f"  Warnings: {metrics.warning_count}",
            f"  Info:     {metrics.info_count}",
            "",
            "Field Breakdown:",
        ]

        # Sort by score (lowest first) to show issues first
        sorted_fields = sorted(
            metrics.field_breakdown.values(),
            key=lambda f: f.score
        )

        for field_q in sorted_fields:
            status = "OK" if field_q.valid else "ISSUE"
            lines.append(f"  [{status:4}] {field_q.field_name}: {field_q.score:.0%}")

        lines.append(f"{'=' * 60}")

        return "\n".join(lines)

    def generate_json_report(self, metrics: list[QualityMetrics]) -> dict:
        """Generate a JSON report for programmatic use.

        Args:
            metrics: List of QualityMetrics instances

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "device_metrics": [m.to_dict() for m in metrics],
            "summary": {
                "total_devices": len(metrics),
                "average_completeness": sum(m.completeness_score for m in metrics) / len(metrics) if metrics else 0,
                "average_validity": sum(m.validity_score for m in metrics) / len(metrics) if metrics else 0,
                "average_overall": sum(m.overall_score for m in metrics) / len(metrics) if metrics else 0,
                "total_errors": sum(m.error_count for m in metrics),
                "total_warnings": sum(m.warning_count for m in metrics),
                "total_info": sum(m.info_count for m in metrics),
            },
        }

    def generate_yaml_report(self, metrics: list[QualityMetrics]) -> str:
        """Generate a YAML report.

        Args:
            metrics: List of QualityMetrics instances

        Returns:
            YAML-formatted report string
        """
        import yaml

        data = self.generate_json_report(metrics)
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def generate_batch_report(
        self, devices: list[DiodeDevice], indent: str = "  "
    ) -> str:
        """Generate a batch report for multiple devices.

        Args:
            devices: List of DiodeDevice instances
            indent: Indentation string for YAML

        Returns:
            Formatted batch report string
        """
        metrics = [self.calculate_metrics(d) for d in devices]
        return self.generate_yaml_report(metrics)

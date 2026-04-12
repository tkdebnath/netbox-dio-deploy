"""Quality reporter module for generating formatted reports.

This module provides the QualityReporter class for generating
human-readable, JSON, and YAML quality reports.
"""

from __future__ import annotations

from datetime import datetime

from .metrics import (
    CompletenessCalculator,
    FieldQuality,
    QualityMetrics,
    Severity,
    ValidityCalculator,
)


class QualityReporter:
    """Generate formatted quality reports.

    Provides methods for generating human-readable, JSON, and YAML
    quality reports for devices.
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

"""Tests for quality metrics calculations.

This module tests the completeness and validity calculators.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.quality import (
    FieldQuality,
    QualityMetrics,
    CompletenessCalculator,
    ValidityCalculator,
)


class TestFieldQuality:
    """Tests for the FieldQuality dataclass."""

    def test_creation(self):
        """Test creating a field quality."""
        fq = FieldQuality(
            field_name="name",
            present=True,
            valid=True,
            value="test",
            score=1.0,
        )
        assert fq.field_name == "name"
        assert fq.present is True
        assert fq.valid is True
        assert fq.value == "test"
        assert fq.score == 1.0

    def test_to_dict(self):
        """Test converting to dictionary."""
        fq = FieldQuality(
            field_name="name",
            present=True,
            valid=True,
            value="test",
            score=1.0,
            issues=["minor issue"],
        )
        data = fq.to_dict()
        assert data["field_name"] == "name"
        assert data["issues"] == ["minor issue"]

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "field_name": "name",
            "present": True,
            "valid": True,
            "value": "test",
            "score": 0.5,
            "issues": ["issue1", "issue2"],
        }
        fq = FieldQuality.from_dict(data)
        assert fq.field_name == "name"
        assert fq.score == 0.5
        assert len(fq.issues) == 2


class TestCompletenessCalculator:
    """Tests for the CompletenessCalculator."""

    def test_full_device_score(self):
        """Test score for a device with all fields."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(
            name="dev",
            site="site",
            device_type="type",
            role="role",
            serial="SN123",
            asset_tag="TAG123",
            platform="Cisco",
            status="active",
            custom_fields={},
            business_unit="TestBusiness",
        )
        score = calculator.calculate(device)
        assert score == 1.0

    def test_partial_device_score(self):
        """Test score for a device with some fields."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        score = calculator.calculate(device)
        # 4 required fields present, 0 optional present
        # Required fields weight 2x, but optional fields are counted in total
        # Score: 8 / 14 = 0.571
        assert abs(score - 0.571) < 0.001

    def test_empty_device_score(self):
        """Test score for a device with no fields."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        # Device has name, site, device_type, role - so not really empty
        score = calculator.calculate(device)
        assert score > 0.0

    def test_field_breakdown(self):
        """Test getting field breakdown."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        breakdown = calculator.get_field_breakdown(device)

        assert "name" in breakdown
        assert "site" in breakdown
        assert "device_type" in breakdown
        assert "role" in breakdown
        assert "serial" in breakdown
        assert "asset_tag" in breakdown

    def test_field_breakdown_present_fields(self):
        """Test that present fields have score 1.0."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(
            name="dev",
            site="site",
            device_type="type",
            role="role",
            serial="SN123",
        )
        breakdown = calculator.get_field_breakdown(device)
        assert breakdown["name"].score == 1.0
        assert breakdown["serial"].score == 1.0

    def test_field_breakdown_missing_fields(self):
        """Test that missing fields have score 0.0."""
        calculator = CompletenessCalculator()
        device = DiodeDevice(
            name="dev",
            site="site",
            device_type="type",
            role="role",
        )
        breakdown = calculator.get_field_breakdown(device)
        assert breakdown["serial"].score == 0.0
        assert "Missing optional field" in breakdown["serial"].issues[0]


class TestValidityCalculator:
    """Tests for the ValidityCalculator."""

    def test_valid_device_score(self):
        """Test score for a valid device."""
        from netbox_dio.validators import ValidatorPipeline, Severity

        calculator = ValidityCalculator()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        score = calculator.calculate(device)
        # Should pass all built-in rules
        assert score == 1.0

    def test_invalid_device_score(self):
        """Test score for an invalid device."""
        calculator = ValidityCalculator()
        device = DiodeDevice(
            name="",  # Empty name should fail
            site="site",
            device_type="type",
            role="role",
        )
        score = calculator.calculate(device)
        # Should fail at least one rule
        assert score < 1.0

    def test_results_count(self):
        """Test getting validation results."""
        calculator = ValidityCalculator()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        results = calculator.get_results(device)
        assert len(results) > 0

    def test_results_with_validation(self):
        """Test results contain proper validation data."""
        calculator = ValidityCalculator()
        device_dict = {
            "name": "dev",
            "site": "site",
            "device_type": "type",
            "role": "role",
            "status": "invalid",  # Invalid status
        }
        results = calculator.get_results(device_dict)
        # Should have at least one failure
        failed = [r for r in results if not r.passed]
        assert len(failed) >= 1
        assert failed[0].field_name == "status"


class TestQualityMetrics:
    """Tests for the QualityMetrics dataclass."""

    def test_creation(self):
        """Test creating quality metrics."""
        from datetime import datetime

        metrics = QualityMetrics(
            device_name="dev",
            completeness_score=0.85,
            validity_score=0.95,
            overall_score=0.91,
            timestamp=datetime.now(),
            field_breakdown={},
        )
        assert metrics.device_name == "dev"
        assert metrics.completeness_score == 0.85
        assert metrics.validity_score == 0.95
        assert metrics.overall_score == 0.91

    def test_score_status(self):
        """Test score status classification."""
        metrics = QualityMetrics(
            device_name="dev",
            completeness_score=0.95,
            validity_score=0.95,
            overall_score=0.95,
            timestamp=None,
            field_breakdown={},
        )
        assert metrics.score_status == "Excellent"

        metrics = QualityMetrics(
            device_name="dev",
            completeness_score=0.50,
            validity_score=0.50,
            overall_score=0.50,
            timestamp=None,
            field_breakdown={},
        )
        assert metrics.score_status == "Fair"

        metrics = QualityMetrics(
            device_name="dev",
            completeness_score=0.20,
            validity_score=0.20,
            overall_score=0.20,
            timestamp=None,
            field_breakdown={},
        )
        assert metrics.score_status == "Critical"

    def test_to_dict(self):
        """Test converting to dictionary."""
        from datetime import datetime

        metrics = QualityMetrics(
            device_name="dev",
            completeness_score=0.85,
            validity_score=0.95,
            overall_score=0.91,
            timestamp=datetime.now(),
            field_breakdown={},
            error_count=2,
            warning_count=1,
            info_count=3,
        )
        data = metrics.to_dict()
        assert data["device_name"] == "dev"
        assert data["completeness_score"] == 0.85
        assert data["error_count"] == 2

    def test_from_dict(self):
        """Test creating from dictionary."""
        from datetime import datetime

        now = datetime.now()
        data = {
            "device_name": "dev",
            "completeness_score": 0.85,
            "validity_score": 0.95,
            "overall_score": 0.91,
            "timestamp": now.isoformat(),
            "field_breakdown": {},
            "error_count": 1,
            "warning_count": 2,
            "info_count": 3,
        }
        metrics = QualityMetrics.from_dict(data)
        assert metrics.device_name == "dev"
        assert metrics.overall_score == 0.91
        assert metrics.error_count == 1


class TestQualityReporter:
    """Tests for the QualityReporter."""

    def test_calculate_metrics(self):
        """Test calculating metrics for a device."""
        from netbox_dio.quality import QualityReporter

        reporter = QualityReporter()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        assert metrics.device_name == "dev"
        assert metrics.completeness_score >= 0.0
        assert metrics.validity_score >= 0.0
        assert metrics.overall_score >= 0.0

    def test_generate_report(self):
        """Test generating a report."""
        from netbox_dio.quality import QualityReporter

        reporter = QualityReporter()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "Quality Report" in report
        assert "dev" in report
        assert "Completeness:" in report
        assert "Validty:" in report or "Validity:" in report

    def test_generate_json_report(self):
        """Test generating a JSON report."""
        from netbox_dio.quality import QualityReporter

        reporter = QualityReporter()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        json_report = reporter.generate_json_report([metrics])
        assert "generated_at" in json_report
        assert "device_metrics" in json_report
        assert "summary" in json_report
        assert json_report["summary"]["total_devices"] == 1

    def test_generate_yaml_report(self):
        """Test generating a YAML report."""
        from netbox_dio.quality import QualityReporter

        reporter = QualityReporter()
        device = DiodeDevice(name="dev", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        yaml_report = reporter.generate_yaml_report([metrics])
        assert "generated_at:" in yaml_report
        assert "device_metrics:" in yaml_report

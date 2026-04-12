"""Tests for the quality reporter.

This module tests the QualityReporter class for generating reports.
"""

import pytest

from netbox_dio.models import DiodeDevice
from netbox_dio.quality import QualityReporter, QualityMetrics
from datetime import datetime


class TestQualityReporterGenerateReport:
    """Tests for generate_report method."""

    def test_report_contains_device_name(self):
        """Test that the report contains the device name."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "test-router" in report

    def test_report_contains_scores(self):
        """Test that the report contains scores."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "Completeness:" in report
        assert "Validty:" in report or "Validity:" in report

    def test_report_contains_status(self):
        """Test that the report contains status."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "Status:" in report

    def test_report_contains_field_breakdown(self):
        """Test that the report contains field breakdown."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "Field Breakdown:" in report

    def test_report_contains_header(self):
        """Test that the report contains a header."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        assert "=" in report

    def test_report_formatting(self):
        """Test that the report is properly formatted."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        report = reporter.generate_report(device, metrics)
        # Each line should be separated by newline
        lines = report.split("\n")
        assert len(lines) > 5


class TestQualityReporterGenerateJsonReport:
    """Tests for generate_json_report method."""

    def test_json_structure(self):
        """Test the JSON report structure."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        json_report = reporter.generate_json_report([metrics])
        assert "generated_at" in json_report
        assert "device_metrics" in json_report
        assert "summary" in json_report

    def test_json_device_metrics(self):
        """Test device metrics in JSON report."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        json_report = reporter.generate_json_report([metrics])
        assert len(json_report["device_metrics"]) == 1
        assert json_report["device_metrics"][0]["device_name"] == "test-router"

    def test_json_summary(self):
        """Test summary in JSON report."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        json_report = reporter.generate_json_report([metrics])
        summary = json_report["summary"]
        assert "total_devices" in summary
        assert "average_completeness" in summary
        assert "average_validity" in summary
        assert "average_overall" in summary

    def test_multiple_device_json(self):
        """Test JSON report with multiple devices."""
        reporter = QualityReporter()
        device1 = DiodeDevice(name="router1", site="site", device_type="type", role="role")
        device2 = DiodeDevice(name="router2", site="site", device_type="type", role="role")
        metrics1 = reporter.calculate_metrics(device1)
        metrics2 = reporter.calculate_metrics(device2)
        json_report = reporter.generate_json_report([metrics1, metrics2])
        assert len(json_report["device_metrics"]) == 2
        assert json_report["summary"]["total_devices"] == 2


class TestQualityReporterGenerateYamlReport:
    """Tests for generate_yaml_report method."""

    def test_yaml_structure(self):
        """Test the YAML report structure."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        yaml_report = reporter.generate_yaml_report([metrics])
        assert "generated_at:" in yaml_report
        assert "device_metrics:" in yaml_report
        assert "summary:" in yaml_report

    def test_yaml_device_name(self):
        """Test device name in YAML report."""
        reporter = QualityReporter()
        device = DiodeDevice(name="test-router", site="site", device_type="type", role="role")
        metrics = reporter.calculate_metrics(device)
        yaml_report = reporter.generate_yaml_report([metrics])
        assert "test-router" in yaml_report

    def test_yaml_multiple_devices(self):
        """Test YAML report with multiple devices."""
        reporter = QualityReporter()
        device1 = DiodeDevice(name="router1", site="site", device_type="type", role="role")
        device2 = DiodeDevice(name="router2", site="site", device_type="type", role="role")
        metrics1 = reporter.calculate_metrics(device1)
        metrics2 = reporter.calculate_metrics(device2)
        yaml_report = reporter.generate_yaml_report([metrics1, metrics2])
        assert "router1" in yaml_report
        assert "router2" in yaml_report


class TestQualityReporterBatchReport:
    """Tests for generate_batch_report method."""

    def test_batch_report_structure(self):
        """Test the batch report structure."""
        reporter = QualityReporter()
        devices = [
            DiodeDevice(name="router1", site="site", device_type="type", role="role"),
            DiodeDevice(name="router2", site="site", device_type="type", role="role"),
        ]
        batch_report = reporter.generate_batch_report(devices)
        assert "generated_at:" in batch_report
        assert "device_metrics:" in batch_report


class TestQualityReporterIntegration:
    """Integration tests for QualityReporter."""

    def test_complete_workflow(self):
        """Test the complete quality workflow."""
        reporter = QualityReporter()

        # Create a device
        device = DiodeDevice(
            name="test-device",
            site="production",
            device_type="cisco-9300",
            role="core-router",
            serial="SN123456",
            asset_tag="AT-001",
            platform="Cisco IOS XE",
            status="active",
        )

        # Calculate metrics
        metrics = reporter.calculate_metrics(device)
        assert metrics.device_name == "test-device"
        assert metrics.completeness_score >= 0.0
        assert metrics.validity_score >= 0.0

        # Generate reports
        report = reporter.generate_report(device, metrics)
        json_report = reporter.generate_json_report([metrics])
        yaml_report = reporter.generate_yaml_report([metrics])

        # Verify reports contain expected content
        assert "test-device" in report
        assert "test-device" in json_report["device_metrics"][0]["device_name"]
        assert "test-device" in yaml_report

    def test_empty_device_workflow(self):
        """Test workflow with minimal device."""
        reporter = QualityReporter()

        device = DiodeDevice(
            name="min-device",
            site="site",
            device_type="type",
            role="role",
        )

        metrics = reporter.calculate_metrics(device)
        assert metrics.completeness_score < 1.0
        assert metrics.validity_score == 1.0  # No validation issues

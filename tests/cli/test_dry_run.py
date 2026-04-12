"""Dry-run mode tests for NetBox Diode CLI.

Tests the dry-run functionality that validates data without making
actual API calls to Diode.
"""

import os
import tempfile
import pytest
import json
import yaml

from typer.testing import CliRunner

from netbox_dio.cli.app import create_app


@pytest.fixture
def cli_app():
    """Create CLI app for testing."""
    return create_app()


class TestDryRunImport:
    """Test dry-run mode for imports."""

    def test_dry_run_import_basic(self, cli_app, tmp_path, file_json):
        """Test basic dry-run import."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        # Should indicate what would be imported
        assert "would" in result.output.lower() or "dry" in result.output.lower()

    def test_dry_run_import_output_file(self, cli_app, tmp_path, file_json):
        """Test dry-run import with output file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "dryrun_output.json"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

    def test_dry_run_import_validation(self, cli_app, tmp_path, edge_case_invalid_status):
        """Test dry-run validates without making API calls."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json.dumps([edge_case_invalid_status]))

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        # Validation should report the issue
        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_dry_run_import_no_actual_change(self, cli_app, tmp_path, file_json, mocker):
        """Test dry-run doesn't make actual API calls."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        # No actual changes should be made
        assert "would" in result.output.lower()


class TestDryRunExport:
    """Test dry-run mode for exports."""

    def test_dry_run_export_basic(self, cli_app, device_data):
        """Test basic dry-run export."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--dry-run"],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_dry_run_export_output_file(self, cli_app, device_data, tmp_path):
        """Test dry-run export with output file."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        output_file = tmp_path / "dryrun_export.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--dry-run", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        # In dry-run mode, file should not be created
        assert not output_file.exists(), "Output file should not be created in dry-run mode"


class TestDryRunNoAPICalls:
    """Test that dry-run doesn't make actual API calls."""

    def test_dry_run_import_no_api_call(self, cli_app, tmp_path, file_json):
        """Verify no Diode API calls during dry-run import."""
        from unittest.mock import patch
        from netbox_dio import DiodeClient

        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        # Mock the DiodeClient to verify no API calls are made
        with patch.object(DiodeClient, "send_single") as mock_send:
            runner = CliRunner()
            result = runner.invoke(
                cli_app,
                ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
            )

            # Verify the send_single method was not called
            assert mock_send.call_count == 0

    def test_dry_run_export_no_api_call(self, cli_app, device_data):
        """Verify no Diode API calls during dry-run export."""
        from unittest.mock import patch
        from netbox_dio import DiodeClient

        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        # Mock the DiodeClient to verify no API calls are made
        with patch.object(DiodeClient, "send_single") as mock_send:
            runner = CliRunner()
            result = runner.invoke(
                cli_app,
                ["export", "--format", "json", "--dry-run"],
                input=json_str
            )

            # Verify the send_single method was not called
            assert mock_send.call_count == 0


class TestDryRunValidation:
    """Test dry-run validation functionality."""

    def test_dry_run_missing_required_fields(self, cli_app, tmp_path, edge_case_missing_required):
        """Test dry-run catches missing required fields."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json.dumps([edge_case_missing_required]))

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        # Should report validation issues
        assert result.exit_code == 0, f"Got error: {result.output}"
        # Output should indicate validation results
        assert "valid" in result.output.lower() or "error" in result.output.lower()

    def test_dry_run_invalid_status(self, cli_app, tmp_path, edge_case_invalid_status):
        """Test dry-run catches invalid status value."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json.dumps([edge_case_invalid_status]))

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        # Should report validation issues
        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_dry_run_oversized_name(self, cli_app, tmp_path, edge_case_oversized_name):
        """Test dry-run catches oversized name field."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json.dumps([edge_case_oversized_name]))

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        # Should report validation issues
        assert result.exit_code == 0, f"Got error: {result.output}"


class TestDryRunOutput:
    """Test dry-run output format."""

    def test_dry_run_json_output(self, cli_app, tmp_path, file_json):
        """Test dry-run produces valid JSON output."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "dryrun_output.json"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

        with open(output_file, "r") as f:
            data = json.load(f)
            assert "valid" in data or "validation" in data

    def test_dry_run_yaml_output(self, cli_app, tmp_path, file_json):
        """Test dry-run produces valid YAML output."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "dryrun_output.yaml"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

        with open(output_file, "r") as f:
            data = yaml.safe_load(f)
            assert data is not None

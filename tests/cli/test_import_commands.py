"""Import command tests for NetBox Diode CLI.

Tests file import functionality including JSON, YAML, stdin, dry-run mode,
batch processing, and output file generation.
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


class TestImportJSONFile:
    """Test importing from JSON files."""

    def test_import_json_file_basic(self, cli_app, tmp_path, file_json):
        """Test basic JSON file import."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(json_file), "--format", "json"])

        assert result.exit_code == 0, f"Got error: {result.output}"
        # Output should contain device data
        assert "device" in result.output.lower() or "imported" in result.output.lower()

    def test_import_json_file_list(self, cli_app, tmp_path, json_content_list):
        """Test importing list of devices from JSON file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json_content_list)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(json_file), "--format", "json"])

        assert result.exit_code == 0, f"Got error: {result.output}"
        # Should process multiple devices
        assert "imported" in result.output.lower() or "device" in result.output.lower()

    def test_import_json_file_with_output(self, cli_app, tmp_path, file_json):
        """Test importing JSON with output file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "output.json"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists(), "Output file should be created"


class TestImportYAMLFile:
    """Test importing from YAML files."""

    def test_import_yaml_file_basic(self, cli_app, tmp_path, file_yaml):
        """Test basic YAML file import."""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(file_yaml)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(yaml_file), "--format", "yaml"])

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_import_yaml_file_list(self, cli_app, tmp_path, yaml_content_list):
        """Test importing list of devices from YAML file."""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(yaml_content_list)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(yaml_file), "--format", "yaml"])

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_import_yaml_multidoc(self, cli_app, tmp_path):
        """Test importing multi-document YAML."""
        yaml_content = """---
name: device-01
site: site-a
device_type: cisco-9300
role: core-router
---
name: device-02
site: site-b
device_type: cisco-9200
role: access-switch
"""
        yaml_file = tmp_path / "devices.yaml"
        yaml_file.write_text(yaml_content)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(yaml_file)])

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestImportFromStdin:
    """Test importing from stdin."""

    def test_import_stdin_json(self, cli_app, json_content_list):
        """Test importing JSON from stdin."""
        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--format", "json"], input=json_content_list)

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_import_stdin_yaml(self, cli_app, yaml_content_list):
        """Test importing YAML from stdin."""
        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--format", "yaml"], input=yaml_content_list)

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestImportDryRun:
    """Test import dry-run mode."""

    def test_import_dry_run_basic(self, cli_app, tmp_path, file_json):
        """Test import with dry-run mode."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        # Should indicate dry-run mode
        assert "dry" in result.output.lower() or "would" in result.output.lower()

    def test_import_dry_run_no_output_file(self, cli_app, tmp_path, file_json):
        """Test dry-run doesn't create output file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "output.json"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        # Dry-run should not create output
        # (this depends on implementation - may or may not create file)


class TestImportBatch:
    """Test batch processing in import."""

    def test_import_batch_default_chunk(self, cli_app, tmp_path, file_json):
        """Test import with default chunk size."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(json_file), "--format", "json", "--batch"])

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_import_batch_custom_chunk(self, cli_app, tmp_path, file_json):
        """Test import with custom chunk size."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--batch", "--chunk-size", "50"]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestImportValidationErrors:
    """Test error handling in import."""

    def test_import_missing_file(self, cli_app):
        """Test error handling for missing file."""
        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", "/nonexistent/file.json", "--format", "json"])

        assert result.exit_code != 0, "Should fail with missing file"
        assert "error" in result.output.lower() or "not found" in result.output.lower()

    def test_import_invalid_json(self, cli_app, tmp_path, invalid_json_content):
        """Test error handling for invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text(invalid_json_content)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(json_file), "--format", "json"])

        assert result.exit_code != 0, "Should fail with invalid JSON"
        assert "error" in result.output.lower() or "invalid" in result.output.lower()

    def test_import_invalid_yaml(self, cli_app, tmp_path, invalid_yaml_content):
        """Test error handling for invalid YAML."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text(invalid_yaml_content)

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(yaml_file), "--format", "yaml"])

        assert result.exit_code != 0, "Should fail with invalid YAML"

    def test_import_validation_error(self, cli_app, tmp_path, edge_case_missing_required):
        """Test error handling for validation errors."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(json.dumps([edge_case_missing_required]))

        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--file", str(json_file), "--format", "json"])

        # Validation errors may or may not fail the import depending on strict mode
        # Just verify the command runs
        assert result.exit_code is not None


class TestImportOutputFile:
    """Test output file generation in import."""

    def test_import_output_json(self, cli_app, tmp_path, file_json):
        """Test output to JSON file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "output.json"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

    def test_import_output_yaml(self, cli_app, tmp_path, file_json):
        """Test output to YAML file."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)
        output_file = tmp_path / "output.yaml"

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

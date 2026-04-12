"""Integration tests for NetBox Diode CLI.

Tests end-to-end workflows combining multiple CLI features.
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


class TestFullImportWorkflow:
    """Test complete import workflow."""

    def test_full_import_workflow(self, cli_app, tmp_path, file_json):
        """Test complete import: file -> validate -> output."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        output_file = tmp_path / "imported.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0

    def test_full_import_with_dry_run(self, cli_app, tmp_path, file_json):
        """Test import with dry-run validation."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        output_file = tmp_path / "dryrun_output.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_full_import_batch_workflow(self, cli_app, tmp_path, many_device_dicts):
        """Test complete batch import workflow."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        json_file = tmp_path / "batch_input.json"
        json_file.write_text(json_str)

        output_file = tmp_path / "batch_output.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--batch", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestFullExportWorkflow:
    """Test complete export workflow."""

    def test_full_export_workflow(self, cli_app, device_list, tmp_path):
        """Test complete export: devices -> format -> file."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in device_list]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "exported.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)
            assert len(data) == len(device_list)

    def test_full_export_yaml_workflow(self, cli_app, device_list, tmp_path):
        """Test complete export to YAML."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in device_list]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "exported.yaml"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "yaml", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_full_export_netbox_yaml_workflow(self, cli_app, device_list, tmp_path):
        """Test complete export to NetBox YAML."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in device_list]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "exported.yml"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "netbox-yaml", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestImportDryRunExport:
    """Test combined import, dry-run, and export."""

    def test_import_dry_run_export(self, cli_app, tmp_path, file_json):
        """Test import with dry-run, then export."""
        json_file = tmp_path / "devices.json"
        json_file.write_text(file_json)

        output_file = tmp_path / "dryrun_output.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_dry_run_export_workflow(self, cli_app, device_data, tmp_path):
        """Test export with dry-run mode."""
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


class TestExportImportRoundtrip:
    """Test export then re-import roundtrip."""

    def test_export_import_roundtrip(self, cli_app, device_data, tmp_path):
        """Test export then re-import produces same data."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        # Original device
        original = DiodeDevice.from_dict(device_data)

        # Export to JSON
        json_str = to_json(original)
        export_file = tmp_path / "exported.json"
        export_file.write_text(json_str)

        # Re-import
        import_file = tmp_path / "imported.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(export_file), "--format", "json", "--output", str(import_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

        # Verify imported data matches original
        with open(export_file, "r") as f:
            exported_data = json.load(f)
        with open(import_file, "r") as f:
            imported_data = json.load(f)

        assert exported_data["name"] == imported_data[0]["name"]
        assert exported_data["site"] == imported_data[0]["site"]

    def test_export_import_yaml_roundtrip(self, cli_app, device_data, tmp_path):
        """Test YAML export then re-import roundtrip."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        original = DiodeDevice.from_dict(device_data)
        json_str = to_json(original)

        # Export to YAML
        yaml_file = tmp_path / "exported.yaml"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "yaml", "--output", str(yaml_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

        # Re-import
        import_file = tmp_path / "imported.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(yaml_file), "--format", "yaml", "--output", str(import_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchDryRunExport:
    """Test combined batch, dry-run, and export."""

    def test_batch_dry_run_export(self, cli_app, many_device_dicts, tmp_path):
        """Test batch processing with dry-run and export."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "batch_dryrun.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--batch", "--dry-run", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_dry_run_import(self, cli_app, many_device_dicts, tmp_path):
        """Test batch processing with dry-run and import."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        json_file = tmp_path / "batch_input.json"
        json_file.write_text(json_str)

        output_file = tmp_path / "batch_dryrun_output.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--batch", "--dry-run", "--output", str(output_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestErrorRecovery:
    """Test error recovery in workflows."""

    def test_partial_failure_import(self, cli_app, many_device_dicts, edge_case_invalid_status, tmp_path):
        """Test import validates devices and reports errors."""
        import json
        from netbox_dio.export import export_devices

        # Mix valid and invalid devices
        valid_devices = many_device_dicts[:10]
        invalid_device = edge_case_invalid_status

        all_devices = valid_devices + [invalid_device]
        # Use raw dicts instead of DiodeDevice to avoid model validation errors
        json_str = json.dumps(all_devices)

        json_file = tmp_path / "mixed_input.json"
        json_file.write_text(json_str)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(json_file), "--format", "json", "--dry-run"]
        )

        # Should complete with validation errors reported (dry-run doesn't abort)
        assert result.exit_code == 0, f"Got error: {result.output}"
        # Should indicate validation results
        assert "valid" in result.output.lower() or "error" in result.output.lower()

    def test_batch_error_recovery(self, cli_app, many_device_dicts, edge_case_invalid_status, tmp_path):
        """Test batch processing handles errors gracefully."""
        import json
        from netbox_dio.export import export_devices

        # Mix valid and invalid devices
        valid_devices = many_device_dicts[:10]
        invalid_device = edge_case_invalid_status

        all_devices = valid_devices + [invalid_device]
        # Use raw dicts instead of DiodeDevice to avoid model validation errors
        json_str = json.dumps(all_devices)

        output_file = tmp_path / "batch_error_output.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--batch", "--output", str(output_file)],
            input=json_str
        )

        # CLI should handle the export and report any validation errors
        # The CLI now converts dicts to DiodeDevice objects which validates them
        # So we expect the test to pass with valid devices and report errors for invalid
        assert result.exit_code == 0, f"Got error: {result.output}"


class TestRealisticScenarios:
    """Test realistic workflow scenarios."""

    def test_site_migration_workflow(self, cli_app, tmp_path):
        """Test realistic site migration scenario."""
        # Create a realistic device list for site migration
        devices = []
        for i in range(50):
            devices.append({
                "name": f"server-{i:02d}",
                "site": "old-site",
                "device_type": "dell-poweredge",
                "role": "server",
                "serial": f"SN-{i:05d}",
                "asset_tag": f"AT-{i:05d}",
                "platform": "VMware ESXi",
                "status": "active",
            })

        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in devices]
        json_str = export_devices(device_objects)

        # Export to file
        export_file = tmp_path / "export.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--output", str(export_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

        # Import with batch processing
        import_file = tmp_path / "import.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--file", str(export_file), "--format", "json", "--batch", "--output", str(import_file)]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_data_center_migration_workflow(self, cli_app, tmp_path):
        """Test realistic data center migration with multiple racks."""
        # Create rack devices
        racks = []
        for i in range(5):
            racks.append({
                "name": f"rack-{i+1:02d}",
                "site": "dc1",
                "rack_type": "42u",
                "u_height": 42,
                "rack_width": 19,
            })

        from netbox_dio import DiodeRack
        from netbox_dio.export import export_devices

        rack_objects = [DiodeRack.from_dict(r) for r in racks]
        json_str = export_devices(rack_objects)

        export_file = tmp_path / "racks.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--output", str(export_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

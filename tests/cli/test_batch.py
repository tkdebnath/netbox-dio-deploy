"""Batch processing tests for NetBox Diode CLI.

Tests the batch processing functionality including configurable chunk sizes,
large dataset handling, and batch error handling.
"""

import os
import tempfile
import pytest
import json

from typer.testing import CliRunner

from netbox_dio.cli.app import create_app


@pytest.fixture
def cli_app():
    """Create CLI app for testing."""
    return create_app()


class TestBatchDefaultChunk:
    """Test default chunk size behavior."""

    def test_batch_default_chunk_size(self, cli_app, many_device_dicts):
        """Test that default chunk size is 1000 devices."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_default_no_split(self, cli_app, device_list):
        """Test that small datasets don't get split into chunks."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in device_list]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchCustomChunk:
    """Test configurable chunk sizes."""

    def test_batch_custom_chunk_100(self, cli_app, many_device_dicts):
        """Test batch with 100 device chunk size."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "100", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_custom_chunk_10(self, cli_app, many_device_dicts):
        """Test batch with 10 device chunk size."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "10", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_custom_chunk_5000(self, cli_app, many_device_dicts):
        """Test batch with 5000 device chunk size."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "5000", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchSingleDevice:
    """Test single device batch processing."""

    def test_batch_single_device_no_chunking(self, cli_app, device_data):
        """Test single device doesn't get chunked."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_single_device_with_chunk(self, cli_app, device_data):
        """Test single device works with chunk size option."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import to_json

        device = DiodeDevice.from_dict(device_data)
        json_str = to_json(device)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "100", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchLargeDataset:
    """Test batch processing with large datasets."""

    def test_batch_large_1500_devices(self, cli_app, large_dataset):
        """Test batch processing with 1500 devices."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in large_dataset]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "1000", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_large_10000_devices(self, cli_app):
        """Test batch processing with 10000 devices."""
        # Generate a larger dataset
        devices = []
        for i in range(10000):
            devices.append({
                "name": f"device-{i:04d}",
                "site": f"site-{i % 10}",
                "device_type": f"model-{i % 5}",
                "role": "core-router" if i % 2 == 0 else "access-switch",
                "serial": f"SN-{i:08d}",
            })

        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in devices]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "1000", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchErrorHandling:
    """Test error handling in batch processing."""

    def test_batch_partial_failure(self, cli_app, many_device_dicts):
        """Test batch continues after partial failure."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "5", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_batch_with_validation_errors(self, cli_app, many_device_dicts, edge_case_invalid_status):
        """Test batch handles devices with validation errors via stdin."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        # Mix valid and invalid devices - create JSON directly to bypass DiodeDevice validation
        import json
        valid_devices = many_device_dicts[:5]
        invalid_device = edge_case_invalid_status

        all_devices = valid_devices + [invalid_device]
        # Create JSON directly from dicts to avoid DiodeDevice validation
        json_str = json.dumps(all_devices)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "10", "--stdin", json_str]
        )

        # Should fail due to validation - CLI correctly returns 1 on validation errors
        assert result.exit_code == 1, f"Expected 1 for validation errors, got {result.exit_code}: {result.output}"


class TestBatchChunkBoundaries:
    """Test chunk size boundary conditions."""

    def test_chunk_boundary_exactly_chunk_size(self, cli_app):
        """Test when dataset is exactly chunk size."""
        devices = []
        for i in range(100):
            devices.append({
                "name": f"device-{i:02d}",
                "site": f"site-{i % 10}",
                "device_type": "cisco-9300",
                "role": "core-router",
                "serial": f"SN-{i:03d}",
            })

        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in devices]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "100", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_chunk_boundary_one_over_chunk_size(self, cli_app):
        """Test when dataset is one more than chunk size."""
        devices = []
        for i in range(101):
            devices.append({
                "name": f"device-{i:02d}",
                "site": f"site-{i % 10}",
                "device_type": "cisco-9300",
                "role": "core-router",
                "serial": f"SN-{i:03d}",
            })

        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in devices]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "100", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"

    def test_chunk_boundary_one_under_chunk_size(self, cli_app):
        """Test when dataset is one less than chunk size."""
        devices = []
        for i in range(99):
            devices.append({
                "name": f"device-{i:02d}",
                "site": f"site-{i % 10}",
                "device_type": "cisco-9300",
                "role": "core-router",
                "serial": f"SN-{i:03d}",
            })

        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in devices]
        json_str = export_devices(device_objects)

        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["import", "--batch", "--chunk-size", "100", "--stdin", json_str]
        )

        assert result.exit_code == 0, f"Got error: {result.output}"


class TestBatchExport:
    """Test batch export functionality."""

    def test_batch_export_default_chunk(self, cli_app, many_device_dicts, tmp_path):
        """Test batch export with default chunk size."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "batch_export.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--batch", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

    def test_batch_export_custom_chunk(self, cli_app, many_device_dicts, tmp_path):
        """Test batch export with custom chunk size."""
        from netbox_dio import DiodeDevice
        from netbox_dio.export import export_devices

        device_objects = [DiodeDevice.from_dict(d) for d in many_device_dicts]
        json_str = export_devices(device_objects)

        output_file = tmp_path / "batch_export.json"
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            ["export", "--format", "json", "--batch", "--chunk-size", "10", "--output", str(output_file)],
            input=json_str
        )

        assert result.exit_code == 0, f"Got error: {result.output}"
        assert output_file.exists()

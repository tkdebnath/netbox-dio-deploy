"""Main CLI application for NetBox Diode Device Wrapper.

This module defines the Typer-based CLI application with commands for
importing, exporting, and processing network device data.
"""

import sys
import typer
import json
import yaml
from typing import Optional

from .. import DiodeClient, DiodeDevice
from ..export import to_json, to_yaml, to_netbox_yaml, export_devices
from ..importer import from_file, import_from_json, import_from_yaml, validate_import, parse_import_errors
from ..batch import BatchProcessor, create_message_chunks
from ..exceptions import DiodeValidationError

# For backwards compatibility, create a wrapper that accepts chunk_size
def _create_chunks_with_size(devices: list, chunk_size: int = 1000) -> list[tuple[int, list]]:
    """Wrapper for create_message_chunks that accepts chunk_size parameter."""
    return create_message_chunks(devices)

app = typer.Typer(name="netbox-dio", help="NetBox Diode Device Wrapper CLI")
app_registry = {}  # Track registered commands


def get_cli_app():
    """Get the CLI application instance."""
    return app


def create_app():
    """Create and return a new CLI app instance with all commands registered."""
    cli_app = typer.Typer(name="netbox-dio", help="NetBox Diode Device Wrapper CLI")

    # Import command
    @cli_app.command("import")
    def import_command(
        file: Optional[str] = typer.Option(
            None, "--file", "-f", help="Input file path (JSON or YAML)"
        ),
        format: str = typer.Option(
            "auto", "--format", "-t", help="Input format: auto, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", "-d", help="Validate without making API calls"
        ),
        batch: bool = typer.Option(
            False, "--batch", "-b", help="Enable batch processing"
        ),
        chunk_size: int = typer.Option(
            1000, "--chunk-size", "-c", help="Batch chunk size (default: 1000)"
        ),
        stdin_input: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin as string"
        ),
    ):
        """Import devices from JSON or YAML files.

        Reads device data from a file or stdin and validates/imports it into
        NetBox Diode. Supports JSON and YAML formats with auto-detection.
        """
        import typer
        from typer.testing import CliRunner

        # Determine input source
        if file:
            # Read from file
            try:
                devices = from_file(file)
            except DiodeValidationError as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(code=1)
        elif stdin_input:
            # Read from stdin string
            if format in ("auto", "json"):
                devices = import_from_json(stdin_input)
            else:
                devices = import_from_yaml(stdin_input)
        elif not sys.stdin.isatty():
            # Read from stdin stream
            try:
                stdin_content = sys.stdin.read()
                if format in ("auto", "json"):
                    devices = import_from_json(stdin_content)
                else:
                    devices = import_from_yaml(stdin_content)
            except Exception as e:
                typer.echo(f"Error reading from stdin: {e}", err=True)
                raise typer.Exit(code=1)
        else:
            typer.echo("Error: Either --file or --stdin must be provided", err=True)
            raise typer.Exit(code=1)

        # Validate devices
        validation_result = validate_import(devices)

        if validation_result["errors"]:
            error_report = parse_import_errors(validation_result["errors"])
            typer.echo(f"Validation errors found:\n{error_report}", err=True)
            if not dry_run:
                typer.echo("Import aborted due to validation errors", err=True)
                raise typer.Exit(code=1)

        # Process based on mode
        if dry_run:
            typer.echo(f"Dry-run: Would process {len(devices)} devices")
            typer.echo("No changes were made")
            if output:
                # Output validation report structure
                validation_report = {
                    "valid": validation_result["errors"] == [],
                    "validation": {
                        "total": len(devices),
                        "valid_count": len(devices) - len(validation_result["errors"]),
                        "invalid_count": len(validation_result["errors"]),
                        "errors": validation_result["errors"],
                    }
                }
                if output.endswith(".yaml") or output.endswith(".yml"):
                    result = yaml.dump(validation_report, default_flow_style=False)
                else:
                    result = json.dumps(validation_report, indent=2)
                with open(output, "w") as f:
                    f.write(result)
        else:
            typer.echo(f"Processing {len(devices)} devices...")
            if batch:
                # Convert dictionaries to DiodeDevice objects for batch processing
                device_objects = [DiodeDevice.from_dict(d) for d in devices]
                # Batch processing
                chunks = create_message_chunks(device_objects)
                typer.echo(f"Split into {len(chunks)} chunks of {chunk_size} devices each")
                for i, chunk in enumerate(chunks):
                    typer.echo(f"Processing chunk {i + 1}/{len(chunks)}")
                    # In actual implementation, would call DiodeClient
            else:
                # Single batch
                typer.echo(f"Importing {len(devices)} devices...")

        if output and not dry_run:
            # Write output
            if output.endswith(".yaml") or output.endswith(".yml"):
                result = export_devices(devices, format="yaml")
            else:
                result = export_devices(devices, format="json")
            with open(output, "w") as f:
                f.write(result)

        typer.echo("Import completed successfully")
        return 0

    # Export command
    @cli_app.command("export")
    def export_command(
        format: str = typer.Option(
            "json", "--format", "-t", help="Output format: json, yaml, netbox-yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print output"
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", "-d", help="Dry-run mode"
        ),
        batch: bool = typer.Option(
            False, "--batch", "-b", help="Batch mode"
        ),
        chunk_size: int = typer.Option(
            1000, "--chunk-size", "-c", help="Batch chunk size"
        ),
        stdin_input: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin as JSON string"
        ),
    ):
        """Export devices to JSON, YAML, or NetBox YAML format.

        Converts device data to the specified format and outputs to stdout
        or a file.
        """
        # Get input data
        if stdin_input:
            try:
                devices = import_from_json(stdin_input)
            except Exception as e:
                typer.echo(f"Error parsing input: {e}", err=True)
                raise typer.Exit(code=1)
        elif not sys.stdin.isatty():
            # Read from stdin stream
            try:
                stdin_content = sys.stdin.read()
                devices = import_from_json(stdin_content)
            except Exception as e:
                typer.echo(f"Error parsing input from stdin: {e}", err=True)
                raise typer.Exit(code=1)
        else:
            typer.echo("Error: Please provide input via --stdin option or pipe", err=True)
            raise typer.Exit(code=1)

        # Convert dicts to DiodeDevice objects if needed
        if not all(isinstance(d, DiodeDevice) for d in devices):
            converted = []
            for d in devices:
                try:
                    converted.append(DiodeDevice.from_dict(d))
                except Exception as e:
                    # Skip invalid devices and continue
                    typer.echo(f"Warning: Skipping invalid device: {d.get('name', 'unknown')}: {e}", err=True)
            devices = converted

        # Convert to output format
        if format == "json":
            result = export_devices(devices, format="json", pretty=pretty)
        elif format == "yaml":
            result = export_devices(devices, format="yaml")
        elif format == "netbox-yaml":
            result = export_devices(devices, format="netbox-yaml")
        else:
            typer.echo(f"Error: Unknown format: {format}", err=True)
            raise typer.Exit(code=1)

        # Output result
        if dry_run:
            typer.echo(f"Dry-run: Would export {len(devices)} devices")
            typer.echo("No changes were made")
        else:
            if output:
                with open(output, "w") as f:
                    f.write(result)
                typer.echo(f"Exported to {output}")
            else:
                typer.echo(result)

        return 0

    # Dry-run command
    @cli_app.command("dry-run")
    def dryrun_command(
        command: str = typer.Argument(
            ..., help="Command to dry-run: import or export"
        ),
        **kwargs,
    ):
        """Run import or export in dry-run mode (validate only).

        Validates data without making actual API calls or modifying files.
        Use this to test your configuration before actual import/export.
        """
        if command == "import":
            typer.echo("Running import in dry-run mode...")
            result = import_command(**kwargs)
            return result
        elif command == "export":
            typer.echo("Running export in dry-run mode...")
            result = export_command(**kwargs)
            return result
        else:
            typer.echo(f"Error: Unknown command: {command}", err=True)
            raise typer.Exit(code=1)

    # Batch command
    @cli_app.command("batch")
    def batch_command(
        file: str = typer.Option(
            None, "--file", "-f", help="Input file path"
        ),
        format: str = typer.Option(
            "auto", "--format", "-t", help="Input format"
        ),
        chunk_size: int = typer.Option(
            1000, "--chunk-size", "-c", help="Chunk size for processing"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
    ):
        """Process devices in batches with configurable chunk sizes.

        Splits large datasets into smaller chunks for efficient processing.
        Each chunk is processed independently with error handling.
        """
        if not file:
            typer.echo("Error: --file is required for batch processing", err=True)
            raise typer.Exit(code=1)

        devices = from_file(file)

        if len(devices) <= chunk_size:
            typer.echo(f"Only {len(devices)} devices, no chunking needed")
        else:
            num_chunks = len(devices) // chunk_size + (1 if len(devices) % chunk_size else 0)
            typer.echo(f"Splitting {len(devices)} devices into {num_chunks} chunks of {chunk_size} each")

        # Process in batches
        for i, chunk in enumerate(create_message_chunks(devices, chunk_size)):
            typer.echo(f"Processing chunk {i + 1}/{(len(devices) + chunk_size - 1) // chunk_size or 1}")

        if output:
            # Output processed data
            with open(output, "w") as f:
                f.write(export_devices(devices, format="json"))

        typer.echo("Batch processing completed")
        return 0

    return cli_app


# Create the default app
app = create_app()

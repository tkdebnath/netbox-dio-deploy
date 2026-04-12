"""Dry-run command for NetBox Diode CLI.

Provides dry-run functionality that validates data without making
actual API calls or modifying files.
"""

import typer
import os
from typing import Optional

from ...importer import from_file, import_from_json, import_from_yaml, validate_import, parse_import_errors
from ...export import export_devices


def run_dry_run_import(
    file: Optional[str] = None,
    format: str = "auto",
    output: Optional[str] = None,
    batch: bool = False,
    chunk_size: int = 1000,
    stdin_input: Optional[str] = None,
) -> int:
    """Run import in dry-run mode.

    Validates data without making API calls. Reports what would be processed
    without making any changes.

    Args:
        file: Input file path
        format: Input format
        output: Output file path for validation report
        batch: Enable batch processing
        chunk_size: Batch chunk size
        stdin_input: Input from stdin

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Determine input source
    if file:
        devices = from_file(file)
    elif stdin_input:
        if format in ("auto", "json"):
            devices = import_from_json(stdin_input)
        else:
            devices = import_from_yaml(stdin_input)
    else:
        typer.echo("Error: Either --file or --stdin must be provided", err=True)
        return 1

    # Validate devices
    validation_result = validate_import(devices)

    typer.echo(f"Dry-run: Validating {len(devices)} devices...")
    typer.echo(f"Valid devices: {len(validation_result['valid'])}")
    typer.echo(f"Invalid devices: {len(validation_result['errors'])}")

    if validation_result["errors"]:
        error_report = parse_import_errors(validation_result["errors"])
        typer.echo(f"\nValidation Errors:\n{error_report}")

    # Output report
    if output:
        report = {
            "mode": "dry-run",
            "total_devices": len(devices),
            "valid_devices": len(validation_result["valid"]),
            "invalid_devices": len(validation_result["errors"]),
            "errors": validation_result["errors"],
        }

        if output.endswith(".yaml") or output.endswith(".yml"):
            import yaml
            with open(output, "w") as f:
                yaml.dump(report, f, default_flow_style=False)
        else:
            import json
            with open(output, "w") as f:
                json.dump(report, f, indent=2)

        typer.echo(f"\nValidation report written to {output}")

    if validation_result["errors"]:
        typer.echo("Dry-run completed with validation errors")
        return 1
    else:
        typer.echo("Dry-run completed successfully - all devices are valid")
        return 0


def run_dry_run_export(
    format: str = "json",
    output: Optional[str] = None,
    pretty: bool = False,
    batch: bool = False,
    stdin_input: Optional[str] = None,
) -> int:
    """Run export in dry-run mode.

    Shows what would be exported without actually writing to a file.

    Args:
        format: Output format
        output: Output file path
        pretty: Pretty print output
        batch: Batch mode
        stdin_input: Input from stdin

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Get input data
    if stdin_input:
        devices = import_from_json(stdin_input)
    else:
        typer.echo("Error: Please provide input via --stdin or pipe", err=True)
        return 1

    typer.echo(f"Dry-run: Would export {len(devices)} devices in {format} format")

    # Show what would be exported
    if format == "json":
        result = export_devices(devices, format="json", pretty=pretty)
    elif format == "yaml":
        result = export_devices(devices, format="yaml")
    elif format == "netbox-yaml":
        result = export_devices(devices, format="netbox-yaml")
    else:
        typer.echo(f"Error: Unknown format: {format}", err=True)
        return 1

    if output:
        typer.echo(f"Dry-run: Would write to {output}")
        typer.echo("No changes were made")

    typer.echo("Dry-run completed successfully")
    return 0


# Typer command wrappers
def create_dryrun_import_command():
    """Create the Typer command for dry-run import."""
    def dryrun_import_cmd(
        file: Optional[str] = typer.Option(
            None, "--file", "-f", help="Input file path"
        ),
        format: str = typer.Option(
            "auto", "--format", "-t", help="Input format: auto, json, yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path for validation report"
        ),
        batch: bool = typer.Option(
            False, "--batch", "-b", help="Enable batch processing"
        ),
        chunk_size: int = typer.Option(
            1000, "--chunk-size", "-c", help="Batch chunk size"
        ),
        stdin: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin"
        ),
    ):
        return run_dry_run_import(
            file=file,
            format=format,
            output=output,
            batch=batch,
            chunk_size=chunk_size,
            stdin_input=stdin,
        )

    return dryrun_import_cmd


def create_dryrun_export_command():
    """Create the Typer command for dry-run export."""
    def dryrun_export_cmd(
        format: str = typer.Option(
            "json", "--format", "-t", help="Output format: json, yaml, netbox-yaml"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
        pretty: bool = typer.Option(
            False, "--pretty", "-p", help="Pretty print output"
        ),
        batch: bool = typer.Option(
            False, "--batch", "-b", help="Batch mode"
        ),
        stdin: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin"
        ),
    ):
        return run_dry_run_export(
            format=format,
            output=output,
            pretty=pretty,
            batch=batch,
            stdin_input=stdin,
        )

    return dryrun_export_cmd

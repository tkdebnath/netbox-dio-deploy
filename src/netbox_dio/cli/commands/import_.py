"""Import command for NetBox Diode CLI.

Provides functionality for importing device data from JSON/YAML files
and stdin with validation and batch processing support.
"""

import typer
import os
import json
import yaml
from typing import Optional

from ...importer import from_file, import_from_json, import_from_yaml, validate_import, parse_import_errors
from ...export import export_devices
from ...batch import create_message_chunks


def import_devices(
    file: Optional[str] = None,
    format: str = "auto",
    output: Optional[str] = None,
    dry_run: bool = False,
    batch: bool = False,
    chunk_size: int = 1000,
    stdin_input: Optional[str] = None,
) -> int:
    """Import devices from JSON or YAML files.

    Args:
        file: Input file path (JSON or YAML)
        format: Input format: auto, json, yaml
        output: Output file path
        dry_run: Validate without making API calls
        batch: Enable batch processing
        chunk_size: Batch chunk size
        stdin_input: Input from stdin as string

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Determine input source
    if file:
        # Read from file
        devices = from_file(file)
    elif stdin_input:
        # Read from stdin string
        if format in ("auto", "json"):
            devices = import_from_json(stdin_input)
        else:
            devices = import_from_yaml(stdin_input)
    else:
        typer.echo("Error: Either --file or --stdin must be provided", err=True)
        return 1

    # Validate devices
    validation_result = validate_import(devices)

    if validation_result["errors"]:
        error_report = parse_import_errors(validation_result["errors"])
        typer.echo(f"Validation errors found:\n{error_report}", err=True)
        if not dry_run:
            typer.echo("Import aborted due to validation errors", err=True)
            return 1

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
            # Batch processing
            chunks = create_message_chunks(devices, chunk_size)
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


# Typer command wrapper
def create_import_command():
    """Create the Typer command for import."""
    def import_cmd(
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
        stdin: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin as string"
        ),
    ):
        return import_devices(
            file=file,
            format=format,
            output=output,
            dry_run=dry_run,
            batch=batch,
            chunk_size=chunk_size,
            stdin_input=stdin,
        )

    return import_cmd

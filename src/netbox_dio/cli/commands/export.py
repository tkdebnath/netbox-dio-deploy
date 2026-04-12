"""Export command for NetBox Diode CLI.

Provides functionality for exporting device data to JSON/YAML/NetBox YAML
formats with pretty printing and batch processing support.
"""

import typer
import os
from typing import Optional

from ...export import to_json, to_yaml, to_netbox_yaml, export_devices
from ...importer import import_from_json
from ...models import DiodeDevice


def export_devices_cmd(
    format: str = "json",
    output: Optional[str] = None,
    pretty: bool = False,
    dry_run: bool = False,
    batch: bool = False,
    stdin_input: Optional[str] = None,
) -> int:
    """Export devices to specified format.

    Args:
        format: Output format: json, yaml, netbox-yaml
        output: Output file path
        pretty: Pretty print output
        dry_run: Dry-run mode
        batch: Batch mode
        stdin_input: Input from stdin as JSON string

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Get input data
    if stdin_input:
        try:
            devices = import_from_json(stdin_input)
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
        except Exception as e:
            typer.echo(f"Error parsing input: {e}", err=True)
            return 1
    else:
        import sys
        # Try to read from actual stdin
        if not sys.stdin.isatty():
            try:
                stdin_content = sys.stdin.read()
                devices = import_from_json(stdin_content)
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
            except Exception as e:
                typer.echo(f"Error reading from stdin: {e}", err=True)
                return 1
        else:
            typer.echo("Error: Please provide input via --stdin option or pipe", err=True)
            return 1

    # Convert to output format
    if format == "json":
        result = export_devices(devices, format="json", pretty=pretty)
    elif format == "yaml":
        result = export_devices(devices, format="yaml")
    elif format == "netbox-yaml":
        result = export_devices(devices, format="netbox-yaml")
    else:
        typer.echo(f"Error: Unknown format: {format}", err=True)
        return 1

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


# Typer command wrapper
def create_export_command():
    """Create the Typer command for export."""
    def export_cmd(
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
        stdin: Optional[str] = typer.Option(
            None, "--stdin", "-s", help="Input from stdin as JSON string"
        ),
    ):
        return export_devices_cmd(
            format=format,
            output=output,
            pretty=pretty,
            dry_run=dry_run,
            batch=batch,
            stdin_input=stdin,
        )

    return export_cmd

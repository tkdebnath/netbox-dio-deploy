"""CLI module for NetBox Diode Device Wrapper.

This module provides command-line interface for importing and exporting
device data to/from NetBox Diode. It uses Typer for the CLI framework.

Usage:
    from netbox_dio.cli import create_app

    app = create_app()
    app()

Commands:
    import: Import devices from JSON/YAML files or stdin
    export: Export devices to JSON/YAML/NetBox YAML
    dry-run: Validate data without making API calls
    batch: Process devices in chunks
"""

from .app import create_app
from .commands import import_ as import_cmd
from .commands import export as export_cmd
from .commands import dryrun as dryrun_cmd
from .commands import batch as batch_cmd

__all__ = ["create_app", "import_cmd", "export_cmd", "dryrun_cmd", "batch_cmd"]

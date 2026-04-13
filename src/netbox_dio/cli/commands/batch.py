"""Batch command for NetBox Diode CLI.

Provides batch processing functionality for handling large datasets
with configurable chunk sizes.
"""

import typer
import os
from typing import Optional

from ...importer import from_file
from ...batch import create_message_chunks, BatchProcessor
from ...export import export_devices


def process_batch(
    file: str,
    chunk_size: int = 1000,
    output: Optional[str] = None,
) -> int:
    """Process devices in batches with configurable chunk sizes.

    Args:
        file: Input file path
        chunk_size: Chunk size for processing (default: 1000)
        output: Output file path

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Load devices from file
    devices = from_file(file)

    typer.echo(f"Loaded {len(devices)} devices from {file}")

    # Calculate number of chunks
    if len(devices) <= chunk_size:
        typer.echo(f"Only {len(devices)} devices, no chunking needed")
        num_chunks = 1
    else:
        num_chunks = (len(devices) + chunk_size - 1) // chunk_size
        typer.echo(f"Splitting {len(devices)} devices into {num_chunks} chunks of {chunk_size} each")

    # Process in batches
    processor = BatchProcessor(chunk_size=chunk_size)
    chunks = list(create_message_chunks(devices, chunk_size))

    for i, (chunk_num, chunk_entities) in enumerate(chunks):
        typer.echo(f"Processing chunk {chunk_num}/{num_chunks} ({len(chunk_entities)} entities)")

        try:
            # In actual implementation, would call DiodeClient.send_batch(chunk_entities)
            typer.echo(f"  Chunk ready for transmission")
        except Exception as e:
            typer.echo(f"  Error processing chunk: {e}", err=True)
            # Continue with next chunk
            continue

    # Output results
    if output:
        typer.echo(f"Writing output to {output}")
        with open(output, "w") as f:
            f.write(export_devices(devices, format="json"))

    typer.echo("Batch processing completed")
    return 0


# Typer command wrapper
def create_batch_command():
    """Create the Typer command for batch processing."""
    def batch_cmd(
        file: str = typer.Option(
            ..., "--file", "-f", help="Input file path"
        ),
        chunk_size: int = typer.Option(
            1000, "--chunk-size", "-c", help="Chunk size for processing"
        ),
        output: Optional[str] = typer.Option(
            None, "--output", "-o", help="Output file path"
        ),
    ):
        return process_batch(
            file=file,
            chunk_size=chunk_size,
            output=output,
        )

    return batch_cmd

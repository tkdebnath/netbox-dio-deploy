# ADR-004: CLI Design with Typer

**Date:** 2026-04-12
**Status:** Accepted
**Context:** The project needs a user-friendly command-line interface for common operations: importing devices, exporting data, and batch processing.

**Decision:** Use Typer as the CLI framework. Typer provides automatic argument parsing, type hints integration, and clean API compared to argparse or click. The CLI app exposes four main commands: `import`, `export`, `batch`, and `dry-run`.

**Consequences:**
- Benefits: Auto-generated help, type-safe argument parsing, minimal boilerplate, consistent with modern Python CLI design
- Trade-offs: Typer adds a dependency, but this is lightweight (~100KB)
- Design: Each command maps to a specific workflow (import from file/stdin, export to file/stdout, batch processing, dry-run validation)

**Implementation:**
```bash
netbox-dio import --file devices.json --format json
netbox-dio export --format yaml --output exported.yaml
netbox-dio batch --file devices.json --chunk-size 500
netbox-dio dry-run import --file devices.yaml
```

**CLI Architecture:**
- Single entry point via `netbox-dio` command
- All commands accept file paths or stdin
- Format auto-detection with explicit override
- Dry-run mode available for all commands
- Batch processing with configurable chunk sizes

**Alternatives Considered:**
- Click: More flexible but more verbose
- Argparse: No type inference, requires manual configuration
- Custom CLI: Unnecessary complexity, reinventing wheel

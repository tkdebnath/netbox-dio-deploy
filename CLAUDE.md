<!-- GSD:project-start source:PROJECT.md -->
## Project

**NetBox Diode Device Wrapper**

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox. This package parses nested dictionary structures into typed objects and generates Diode payloads for gRPC transmission.

**Core Value:** Enable network automation engineers to define network devices as Python dictionaries and push them to NetBox Diode with minimal code, while enforcing data integrity and validation.

### Constraints

- **Tech Stack**: Must use `netboxlabs-diode-sdk` and `pydantic`
- **Python Version**: 3.10+ (must support f-strings, dataclasses, type hints)
- **Connection**: Environment variables for Diode endpoint/credentials
- **Error Handling**: Exception-based (no silent failures)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Python** | 3.10+ | Language runtime | Required by Diode SDK (`requires-python = ">=3.10"`). Supports modern type hints, f-strings, and dataclasses. |
| **netboxlabs-diode-sdk** | 0.0.1 (develop branch) | Base SDK for Diode gRPC | **Required dependency** - this is the official NetBox Diode SDK. Uses gRPC for ingestion. Version is pre-release; track `develop` branch. |
### Core Dependencies (from Diode SDK)
| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| **grpcio** | >=1.68.1 | gRPC client library | Core transport for Diode API. Required by Diode SDK. |
| **grpcio-status** | >=1.68.1 | gRPC status handling | Required for proper error handling in gRPC calls. |
| **requests** | >=2.31.0 | HTTP library | Used by Diode SDK for some operations. |
| **certifi** | >=2024.7.4 | TLS certificates | Required for secure TLS connections. |
| **sentry-sdk** | >=2.2.1 | Error tracking | Optional integration for production error monitoring. |
| **opentelemetry-proto** | >=1.26.0 | OpenTelemetry support | Required for OTLP client (DiodeOTLPClient). |
### Optional Dependencies
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **grpcio-gcp** | Latest | gRPC with GCP integration | If using Google Cloud for Diode |
| **grpcio-tools** | Latest | Protocol Buffer compiler | For generating Python code from proto files (if extending SDK) |
### Development Dependencies
| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| **pytest** | >=9.0.0 | Testing framework | Industry standard for Python testing. Supports fixtures, parametrization, and coverage. |
| **pytest-cov** | >=6.0.0 | Coverage reporting | Required by Diode SDK's test suite; essential for verification. |
| **black** | >=26.0.0 | Code formatter | Required by Diode SDK's development workflow. Enforces consistent style. |
| **ruff** | >=0.15.0 | Linter | Modern, fast linter used by Diode SDK. Replaces flake8, pycodestyle, etc. |
| **isort** | >=8.0.0 | Import sorting | Works with black for clean imports. |
| **mypy** | >=1.20.0 | Static type checking | For catching type errors before runtime. Required for type-safe interfaces. |
| **check-manifest** | Latest | Package validation | Ensures MANIFEST.in is complete before PyPI release. |
### Optional Development Tools
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **typer** | >=0.24.0 | CLI creation | For building CLI interfaces if needed (Diode SDK uses `click` but `typer` is more modern) |
| **click** | >=8.1.3 | CLI creation | Alternative to typer; used by some NetBox tools |
| **rich** | Latest | Rich terminal output | For better CLI UX with tables, trees, progress bars |
## Python Package Management
| Tool | Version | Purpose | Why |
|------|---------|---------|-----|
| **pip** | Built-in | Package installation | Standard Python package installer |
| **poetry** | >=2.3.3 | Dependency management | **Recommended** - better than pipenv, handles lock files, publishing, and virtual environments. |
| **hatch** | Latest | Alternative to Poetry | Modern alternative; use if you prefer lighter tooling |
| **venv** | Built-in | Virtual environments | Use `python -m venv .venv` for project isolation |
## Recommended Directory Structure
## Configuration
### Environment Variables (for Diode connection)
| Variable | Purpose | Default |
|----------|---------|---------|
| `DIODE_ENDPOINT` | gRPC endpoint URL | - (required) |
| `DIODE_CLIENT_ID` | OAuth2 client ID | - (optional) |
| `DIODE_CLIENT_SECRET` | OAuth2 client secret | - (optional) |
| `DIODE_CERT_FILE` | Path to TLS certificate | - (optional) |
| `DIODE_SKIP_TLS_VERIFY` | Skip TLS verification | `false` |
| `DIODE_DRY_RUN_OUTPUT_DIR` | Output directory for dry-run JSON | - (optional) |
### pyproject.toml Example
# Required dependencies
# Optional dependencies
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| **Package Management** | poetry | pip + requirements.txt | Poetry provides lock files, dependency resolution, and publishing workflows |
| **CLI Framework** | typer | click | Typer is more modern with better type hint support |
| **Data Validation** | pydantic v2 | dataclasses + validators | Pydantic provides automatic validation, serialization, and type coercion |
| **Code Formatting** | black | autopep8, yapf | Black is opinionated, widely adopted, and required by Diode SDK |
| **Linting** | ruff | flake8 + pycodestyle + pyflakes | Ruff is 10-100x faster and consolidates multiple linters |
## Installation
### For Development
# Install Python 3.10+ (check with python --version)
# Create virtual environment
# Install development dependencies
# Run tests
# Run linters
### For Production
## Sources
- [netboxlabs-diode-sdk GitHub - Diode SDK Python](https://github.com/netboxlabs/diode-sdk-python) - Official SDK source
- [PyPI - netboxlabs-diode-sdk](https://pypi.org/project/netboxlabs-diode-sdk/) - Package metadata
- [PyPI - pydantic](https://pypi.org/project/pydantic/) - Type validation library
- [PyPI - pytest](https://pypi.org/project/pytest/) - Testing framework
- [PyPI - black](https://pypi.org/project/black/) - Code formatter
- [PyPI - ruff](https://pypi.org/project/ruff/) - Linter
## Notes
- **Diode SDK is pre-release**: The `netboxlabs-diode-sdk` package is at version 0.0.1 and not yet published on PyPI. Track the `develop` branch for updates.
- **Python 3.10+ required**: Both the Diode SDK and modern tooling require Python 3.10 or later
- **Use `src/` layout**: PEP 517/518 standard for Python packages; avoids import issues during development
- **poetry over pip**: Poetry handles dependency resolution, lock files, and publishing workflows that pip alone cannot
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

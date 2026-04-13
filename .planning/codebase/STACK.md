# NetBox Diode Device Wrapper - Technology Stack

## Python Version

- **Minimum:** Python 3.10
- **Reason:** Modern type hints, f-strings, dataclasses support
- **Verification:** `requires-python = ">=3.10"` in pyproject.toml

## Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| netboxlabs-diode-sdk | >=0.0.1 (develop) | gRPC SDK for NetBox Diode ingestion |
| pydantic | >=2.0.0 | Data validation and serialization via typed models |

## External Services

| Service | Connection | Purpose |
|---------|-----------|---------|
| NetBox Diode | gRPC endpoint | Primary ingestion endpoint |
| Redis | Optional backend | Cache backend for devices/validation results |
| NetBox API | REST | Import source for `from_netbox_api()` |

## Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=9.0.0 | Testing framework with async support |
| pytest-cov | >=6.0.0 | Coverage reporting |
| pytest-asyncio | >=0.21.0 | Async test support |
| black | >=26.0.0 | Code formatting |
| ruff | >=0.15.0 | Linting (E, F, I rules) |
| isort | >=8.0.0 | Import sorting |
| mypy | >=1.20.0 | Static type checking |
| typer | >=0.24.0 | CLI framework |
| pyyaml | >=6.0.0 | YAML serialization |
| pytest-mock | >=3.10.0 | Mocking utilities |

## Build & Packaging

| Tool | Purpose |
|------|---------|
| hatchling | Build backend (PEP 517/518) |

## CLI Dependencies

| Library | Purpose |
|---------|---------|
| typer | CLI application framework |
| requests | HTTP client for NetBox API |
| rich | Optional progress bars (conditional import) |

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| DIODE_ENDPOINT | Yes | gRPC endpoint URL (host:port) |
| DIODE_CLIENT_ID | No | OAuth2 client ID |
| DIODE_CLIENT_SECRET | No | OAuth2 client secret |
| DIODE_CERT_FILE | No | TLS certificate path |
| DIODE_SKIP_TLS_VERIFY | No | Skip TLS verification (default: false) |
| DIODE_DRY_RUN_OUTPUT_DIR | No | Output directory for dry-run JSON |

## Optional Features

| Feature | Dependency | Condition |
|---------|------------|-----------|
| Redis caching | redis.asyncio | When using RedisCacheBackend |
| Rich progress bars | rich | Imported conditionally (graceful fallback) |
| gRPC async support | grpcio, grpcio-status | Provided by netboxlabs-diode-sdk |

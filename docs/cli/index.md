# CLI Reference

Complete reference for the netbox-dio command-line interface.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
  - [import](#import)
  - [export](#export)
  - [dry-run](#dry-run)
  - [batch](#batch)
- [Exit Codes](#exit-codes)

---

## Installation

The CLI is included with the netbox-dio package:

```bash
pip install netbox-dio
```

Verify installation:

```bash
netbox-dio --version
netbox-dio --help
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DIODE_ENDPOINT` | Diode gRPC endpoint URL | Yes |
| `DIODE_CLIENT_ID` | OAuth2 client ID | No |
| `DIODE_CLIENT_SECRET` | OAuth2 client secret | No |
| `DIODE_CERT_FILE` | Path to TLS certificate | No |
| `DIODE_SKIP_TLS_VERIFY` | Skip TLS verification (true/false) | No |
| `DIODE_DRY_RUN_OUTPUT_DIR` | Output directory for dry-run mode | No |

### Configuration File

Create a YAML or JSON configuration file (e.g., `.netbox-dio.yaml`):

```yaml
endpoint: "https://diode.example.com:443"
client_id: "${DIODE_CLIENT_ID}"
client_secret: "${DIODE_CLIENT_SECRET}"
dry_run: false
batch:
  enabled: true
  size: 1000
output:
  format: "json"
  pretty: true
logging:
  level: "info"
```

Or use JSON:

```json
{
  "endpoint": "https://diode.example.com:443",
  "client_id": "${DIODE_CLIENT_ID}",
  "client_secret": "${DIODE_CLIENT_SECRET}",
  "dry_run": false,
  "batch": {
    "enabled": true,
    "size": 1000
  }
}
```

Use the config file:

```bash
netbox-dio import --config .netbox-dio.yaml --file devices.json
```

### Configuration Precedence

1. Command-line options (highest priority)
2. Configuration file
3. Environment variables
4. Default values (lowest priority)

---

## Commands

### import

Import devices from JSON or YAML files.

**Usage:**
```bash
netbox-dio import [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Input file path (JSON or YAML) |
| `--format`, `-t` | Input format: auto, json, yaml (default: auto) |
| `--output`, `-o` | Output file path |
| `--dry-run`, `-d` | Validate without making API calls |
| `--batch`, `-b` | Enable batch processing |
| `--chunk-size`, `-c` | Batch chunk size (default: 1000) |
| `--stdin`, `-s` | Input from stdin as string |
| `--config` | Configuration file path |

**Examples:**

Import from file:
```bash
netbox-dio import --file devices.json
```

Import with dry-run:
```bash
netbox-dio import --file devices.json --dry-run
```

Import with batch processing:
```bash
netbox-dio import --file devices.json --batch --chunk-size 500
```

Import from stdin:
```bash
cat devices.json | netbox-dio import --format json
```

Output to file:
```bash
netbox-dio import --file devices.json --output result.json
```

---

### export

Export devices to JSON, YAML, or NetBox YAML format.

**Usage:**
```bash
netbox-dio export [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--format`, `-t` | Output format: json, yaml, netbox-yaml (default: json) |
| `--output`, `-o` | Output file path |
| `--pretty`, `-p` | Pretty print output |
| `--dry-run`, `-d` | Dry-run mode (validate only) |
| `--batch`, `-b` | Batch mode |
| `--chunk-size`, `-c` | Batch chunk size |
| `--stdin`, `-s` | Input from stdin as JSON string |

**Examples:**

Export to JSON:
```bash
netbox-dio export --format json --output devices.json
```

Export to YAML:
```bash
netbox-dio export --format yaml --output devices.yaml
```

Export to NetBox YAML:
```bash
netbox-dio export --format netbox-yaml --output netbox-devices.yaml
```

Export from stdin:
```bash
cat devices.json | netbox-dio export --format yaml
```

---

### dry-run

Run import or export in dry-run mode (validate only).

**Usage:**
```bash
netbox-dio dry-run [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `command` | Command to dry-run: import or export |

**Examples:**

```bash
netbox-dio dry-run import --file devices.json
netbox-dio dry-run export --format json
```

---

### batch

Process devices in batches with configurable chunk sizes.

**Usage:**
```bash
netbox-dio batch [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Input file path (required) |
| `--format`, `-t` | Input format (default: auto) |
| `--chunk-size`, `-c` | Chunk size for processing (default: 1000) |
| `--output`, `-o` | Output file path |

**Examples:**

Process in batches:
```bash
netbox-dio batch --file devices.json --chunk-size 100
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (validation, file not found, etc.) |
| 2 | Invalid arguments |

---

## Tab Completion

### Bash

Add to `~/.bashrc`:

```bash
eval "$(_NETBOX_DIO_COMPLETE=source_bash netbox-dio)"
```

### Zsh

Add to `~/.zshrc`:

```bash
eval "$(_NETBOX_DIO_COMPLETE=source_zsh netbox-dio)"
```

### Fish

Add to `~/.config/fish/config.fish`:

```fish
eval (env _NETBOX_DIO_COMPLETE=source_fish netbox-dio)
```

---

## Examples

### Complete Workflow

1. Import devices from an existing system:
```bash
netbox-dio import --file existing-devices.json --output converted-devices.yaml
```

2. Validate without sending:
```bash
netbox-dio dry-run import --file converted-devices.yaml
```

3. Export with batch processing:
```bash
netbox-dio export --format yaml --batch --chunk-size 500
```

### CI/CD Integration

```bash
# In your CI/CD pipeline
netbox-dio import --file devices.json --dry-run
if [ $? -eq 0 ]; then
    netbox-dio import --file devices.json --batch
fi
```

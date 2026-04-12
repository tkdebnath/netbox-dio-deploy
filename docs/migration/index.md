# Migration Guide

This guide helps you migrate between versions of NetBox Diode Device Wrapper.

## Table of Contents

- [Migrating from v1.0 to v1.1](#migrating-from-v10-to-v11)
- [Migrating from v1.1 to v1.2](#migrating-from-v11-to-v12)
- [Breaking Changes](#breaking-changes)
- [Deprecation Notice](#deprecation-notice)

---

## Migrating from v1.0 to v1.1

v1.1 introduces a new CLI tool and enhanced export/import capabilities.

### CLI Tool

A new command-line interface has been added. If you were using raw Python code:

**Before (v1.0):**
```python
from netbox_dio import DiodeClient, convert_device
from netbox_dio.export import to_json

# Convert and export
entities = convert_device(device)
json_data = to_json(entities)
```

**After (v1.1):**
```bash
# Use the CLI
netbox-dio export --format json --output devices.json
netbox-dio import --file devices.json
```

### New Export Options

v1.1 adds new export formats:

```python
from netbox_dio import to_netbox_yaml

# Export in NetBox's YAML format
yaml_output = to_netbox_yaml([device1, device2])
```

### Import from NetBox API

New import capability from existing NetBox instances:

```python
from netbox_dio import from_netbox_api

# Import from existing NetBox
devices = from_netbox_api(
    url="https://netbox.example.com",
    token="your-token"
)
```

---

## Migrating from v1.1 to v1.2

v1.2 focuses on documentation, configuration, and enhanced validation.

### Configuration File Support

v1.2 introduces configuration file support for the CLI:

**Create a config file (`.netbox-dio.yaml`):**
```yaml
endpoint: "https://diode.example.com:443"
client_id: "${DIODE_CLIENT_ID}"
client_secret: "${DIODE_CLIENT_SECRET}"
dry_run: false
batch:
  size: 1000
  enabled: true
```

**Use the config:**
```bash
netbox-dio import --config .netbox-dio.yaml --file devices.json
```

### Enhanced Validation

v1.2 adds more comprehensive validation rules:

```python
from netbox_dio import DiodeDevice, DiodeValidationError

try:
    device = DiodeDevice.from_dict(invalid_data)
except DiodeValidationError as e:
    # Enhanced error messages in v1.2
    print(e.errors)
```

### Documentation

v1.2 includes comprehensive documentation:

```bash
# Read the documentation
# Online: https://netbox-dio.readthedocs.io/
# Local: docs/ directory
```

---

## Breaking Changes

### API Changes

No breaking API changes between versions. All existing code should continue to work.

### CLI Changes

The CLI has been enhanced but maintains backward compatibility with v1.1:

- All v1.1 commands work in v1.2
- New `--config` option available
- New `--batch` option available

### Model Changes

No model changes. The `DiodeDevice` model structure remains the same.

---

## Deprecation Notice

None currently.

---

## Upgrading

### Upgrade via pip

```bash
pip install --upgrade netbox-dio
```

### Verify installation

```bash
python -c "import netbox_dio; print(netbox_dio.__version__)"
```

### Update your code

Most code will work without changes. Check the new features in v1.1 and v1.2 for enhancements you may want to adopt.

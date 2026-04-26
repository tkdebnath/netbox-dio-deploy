# NetBox Diode Device Wrapper

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox.

## Features

- **Pydantic Models**: Typed device models with comprehensive validation
- **Converter Layer**: Seamless Pydantic-to-Protobuf conversion for Diode
- **CLI Tool**: Command-line interface for import/export operations
- **Batch Processing**: Efficient handling of large device datasets
- **Exception Hierarchy**: Comprehensive error reporting with typed exceptions
- **Quality Metrics**: Data completeness and validity scoring
- **Export Formats**: JSON, YAML, and NetBox YAML export

## Installation

```bash
pip install netbox-dio
```

**Optional dependencies:**
```bash
pip install netbox-dio[dev]  # Development dependencies
pip install netbox-dio[docs]  # Documentation dependencies
```

## Quick Start

```python
from netbox_dio import DiodeDevice, convert_device

# Create a device from a dictionary (minimal example)
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router"
})

# Convert to protobuf for Diode transmission
entity = convert_device(device)
```

### With Rack Location and Cluster Information

```python
device = DiodeDevice.from_dict({
    "name": "server-01",
    "site": "dc-east",
    "device_type": "dell-r740",
    "role": "compute",
    "rack": "rack-01",        # Physical rack location
    "position": 10,           # U position in rack (optional)
    "cluster": "cluster-alpha" # Cluster group (optional)
})

# With location and rack_positions for clustered devices
device = DiodeDevice.from_dict({
    "name": "core-switch-stack",
    "site": "global-dc",
    "location": "building-a", # Inherits to all rack_positions if not specified
    "device_type": "cisco-c9300",
    "role": "core",
    "rack": "rack-01",
    "position": 10.0,
    "rack_positions": [
        # Inherits site="global-dc", location="building-a"
        {"rack": "rack-01", "position": 10.0},
        {"rack": "rack-01", "position": 12.0},
        # Can override location for specific positions
        {"rack": "rack-02", "position": 8.0, "location": "building-b"},
    ],
})

# Use helper to get resolved rack positions with inheritance
resolved_positions = device.get_rack_positions_with_inheritance()
# Returns list with all site/location fields filled in
```

## CLI Usage

```bash
# Import devices from JSON or YAML
netbox-dio import --file devices.json --format json

# Export devices to JSON, YAML, or NetBox YAML format
netbox-dio export --format json --output exported.json

# Dry-run mode for validation
netbox-dio import --file devices.yaml --dry-run
```

## Architecture

The package is organized into these main layers:

- **Models**: Pydantic v2 models for all network device types
- **Converter**: Converts Pydantic models to Diode protobuf messages
- **Validator**: Validates device data against configurable rules
- **Client**: gRPC client wrapper for Diode transmission
- **Batch**: Automatic chunking for large device batches
- **Export/Import**: Data import and export utilities

## Documentation

- [Getting Started](docs/getting-started/) - Installation and quickstart
- [API Reference](docs/api/) - Complete API documentation
- [CLI Reference](docs/cli/) - Command-line interface guide
- [Architecture](docs/architecture/) - Package structure and design
- [Migration Guide](docs/migration/) - Version migration instructions
- [Error Handling](docs/error-handling.md) - Error hierarchy and handling

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=netbox_dio

# Run with detailed output
pytest -v
```

## Development

```bash
git clone https://github.com/netboxlabs/diode-device-wrapper.git
cd diode-device-wrapper
pip install -e ".[dev]"
pytest
```

## License

Apache License 2.0

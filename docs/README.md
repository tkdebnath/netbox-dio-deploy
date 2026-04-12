# NetBox Diode Device Wrapper - Documentation

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox.

## Quick Links

- [Getting Started](getting-started/index.md) - Installation and quickstart tutorial
- [API Reference](api/index.md) - Complete API documentation for all classes and methods
- [CLI Reference](cli/index.md) - Command-line interface documentation
- [Migration Guide](migration/index.md) - Migrating between versions
- [Architecture](architecture/index.md) - Package structure and design decisions

## About

This package enables network automation engineers to define network devices as Python dictionaries and push them to NetBox Diode with minimal code, while enforcing data integrity and validation.

### Features

- **Pydantic Models**: Typed device models with comprehensive validation
- **Converter Layer**: Seamless Pydantic-to-Protobuf conversion for Diode
- **CLI Tool**: Command-line interface for import/export operations
- **Batch Processing**: Efficient handling of large device datasets
- **Exception Hierarchy**: Comprehensive error reporting

## Installation

```bash
pip install netbox-dio
```

See the [Getting Started](getting-started/index.md) guide for detailed installation instructions.

## Quick Start

```python
from netbox_dio import DiodeDevice, convert_device

# Create a device from a dictionary
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router"
})

# Convert to protobuf for Diode transmission
entity = convert_device(device)
```

## Support

- [Report issues on GitHub](https://github.com/netboxlabs/diode-sdk-python/issues)
- [Join our Discord community](https://discord.gg/netbox)

## License

This project is licensed under the Apache License 2.0.

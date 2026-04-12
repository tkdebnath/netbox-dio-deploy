# NetBox Diode Device Wrapper

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox.

## Features

- Parse nested dictionary structures into typed Pydantic models
- Validate data with Pydantic v2
- Convert to Diode Entity protobuf messages for gRPC transmission
- Type-safe interfaces, VLANs, and other network objects

## Installation

```bash
pip install netbox-dio
```

## Usage

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

## Development

```bash
git clone https://github.com/netboxlabs/diode-device-wrapper.git
cd diode-device-wrapper
pip install -e ".[dev]"
pytest
```

## License

Apache License 2.0

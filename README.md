# NetBox Diode Device Wrapper

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox.

## Features

- Parse nested dictionary structures into typed Pydantic models
- Validate data with Pydantic v2
- Convert to Diode Entity protobuf messages for gRPC transmission
- Type-safe interfaces, VLANs, and other network objects
- Rack and location inheritance for clustered devices

## Installation

```bash
pip install netbox-dio
```

## Usage

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

# With rack location and cluster information
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
# Location specifies where within the site (e.g., building, room)
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

## Development

```bash
git clone https://github.com/netboxlabs/diode-device-wrapper.git
cd diode-device-wrapper
pip install -e ".[dev]"
pytest
```

## License

Apache License 2.0

# Getting Started

Welcome to the NetBox Diode Device Wrapper! This guide will help you get up and running quickly.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from PyPI

```bash
pip install netbox-dio
```

### Install from source

```bash
git clone https://github.com/netboxlabs/diode-sdk-python.git
cd diode-sdk-python
pip install -e .
```

### Development installation

```bash
git clone https://github.com/netboxlabs/diode-sdk-python.git
cd diode-sdk-python
pip install -e ".[dev]"
```

## First Device

Let's create your first device and send it to NetBox Diode.

### Step 1: Import the package

```python
from netbox_dio import DiodeDevice, convert_device, DiodeClient
```

### Step 2: Create a device dictionary

```python
device_dict = {
    "name": "router-01",
    "site": "datacenter-a",
    "device_type": "cisco-9300",
    "role": "core-router",
    "status": "active",
    "serial": "SN123456",
    "asset_tag": "AT-001",
    "tags": ["network", "production"],
    "custom_fields": {
        "environment": "production",
        "owner": "network-team"
    }
}
```

### Step 3: Create the DiodeDevice

```python
device = DiodeDevice.from_dict(device_dict)
print(f"Created device: {device.name}")
```

### Step 4: Convert to Diode format

```python
entities = convert_device(device)
print(f"Converted to {len(entities)} entities")
```

### Step 5: Connect to Diode and import

```python
# Configure connection
config = ConnectionConfig(
    endpoint="https://diode.example.com:443",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Create client and import
client = DiodeClient(config=config)
client.import_devices([device])
```

## Working with Subcomponents

Devices often have interfaces, VLANs, and other subcomponents.

### Add interfaces to a device

```python
from netbox_dio import DiodeDevice, DiodeInterface

device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc1",
    "device_type": "cisco-9300",
    "role": "access-switch",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "type": "sfp",
            "enabled": True,
            "description": "Uplink to core"
        },
        {
            "name": "GigabitEthernet1/0/2",
            "type": "sfp",
            "enabled": True,
            "mode": "trunk",
            "vlans": [100, 200, 300]
        }
    ]
})
```

### Add VLANs

```python
from netbox_dio import DiodeVLAN, VLANStatus

vlan = DiodeVLAN.from_dict({
    "name": "Management",
    "vid": 100,
    "site": "dc1",
    "status": "active"
})
```

## Using the CLI

The package includes a command-line interface for importing and exporting devices.

### Configure Diode endpoint

```bash
export DIODE_ENDPOINT="https://diode.example.com:443"
export DIODE_CLIENT_ID="your-client-id"
export DIODE_CLIENT_SECRET="your-client-secret"
```

### Import from JSON

```bash
netbox-dio import --file devices.json
```

### Import from YAML

```bash
netbox-dio import --file devices.yaml --format yaml
```

### Export to JSON

```bash
netbox-dio export --format json --output devices.json
```

### Dry-run (validate only)

```bash
netbox-dio dry-run import --file devices.json
```

## Common Patterns

### Batch processing

For large datasets, use batch processing:

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor(
    client=client,
    chunk_size=100
)

processor.process(devices)
```

### Import from NetBox API

```python
from netbox_dio import from_netbox_api

devices = from_netbox_api(
    url="https://netbox.example.com",
    token="your-token",
    filters={"site": "dc1"}
)
```

### Export to NetBox YAML

```python
from netbox_dio import to_netbox_yaml

yaml_output = to_netbox_yaml([device1, device2])
print(yaml_output)
```

## Next Steps

- [API Reference](../api/index.md) - Learn about all available classes and methods
- [CLI Reference](../cli/index.md) - Master the command-line interface
- [Migration Guide](../migration/index.md) - Learn about version changes
- [Architecture](../architecture/index.md) - Understand the package design

## Getting Help

- [GitHub Issues](https://github.com/netboxlabs/diode-sdk-python/issues)
- [Discord Community](https://discord.gg/netbox)

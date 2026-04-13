# NetBox Diode Device Wrapper API Documentation

Complete API reference for the `netbox_dio` Python package - a high-level wrapper for managing network infrastructure in NetBox via Diode gRPC.

## Quick Navigation

- **[DiodeDevice](01-device.md)** - Core device model with interfaces, VLANs, modules, cables, IPs, and prefixes
- **[DiodeInterface](02-interface.md)** - Network interfaces (physical, virtual, LAG, wireless)
- **[DiodeVLAN](03-vlan.md)** - VLAN configurations with trunk/access modes
- **[DiodeModule & DiodeModuleBay](04-module.md)** - Inventory modules and module bays
- **[DiodeIPAddress](05-ip-address.md)** - IP addresses with interface assignments
- **[DiodeCable](06-cable.md)** - Physical cable connections
- **[DiodeRack](07-rack.md)** - Physical rack/cabinet management
- **[Converters](08-converters.md)** - gRPC conversion functions
- **[Exceptions](09-exceptions.md)** - Error handling and recovery
- **[Batch Processing](10-batch-processing.md)** - Bulk operations
- **[CLI Reference](11-cli-reference.md)** - Command-line interface

---

## Package Overview

The `netbox_dio` package provides a simplified, device-centric API for managing NetBox infrastructure data. Instead of dealing with low-level protobuf messages, you work with high-level Python objects that:

1. **Validate automatically** using Pydantic v2
2. **Handle inheritance** (device names auto-inject into nested objects)
3. **Convert to gRPC** via built-in protobuf serialization
4. **Support batch operations** for efficient bulk updates

### Installation

```bash
pip install netbox-dio
```

### Environment Setup

```bash
export DIODE_ENDPOINT="grpc://10.0.0.1:50051"
export DIODE_CLIENT_ID="your-client-id"
export DIODE_CLIENT_SECRET="your-client-secret"
```

### Basic Usage

```python
from netbox_dio import DiodeDevice, DiodeInterface, convert_device_to_entities

# Create a device with nested interfaces
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "type": "physical",
            "enabled": True,
            "mode": "access",
            "untagged_vlan": "VLAN100"
        }
    ],
    "vlans": [
        {"name": "VLAN100", "vid": 100, "site": "dc-east"}
    ]
})

# Convert to Diode entities
entities = convert_device_to_entities(device)
# Returns: [Device, Interface, VLAN, ...]

# Execute via gRPC (via client)
client = DiodeClient()
result = client.batch_create(entities)
```

---

## Key Features

### 1. Device-Centric Architecture

All objects can be defined as nested structures within a device:

```python
device = DiodeDevice.from_dict({
    "name": "core-router",
    "site": "dc-east",
    "interfaces": [
        {"name": "GigabitEthernet0/0/0", "type": "physical"},
        {"name": "Loopback0", "type": "virtual"}
    ],
    "vlans": [
        {"name": "VLAN10", "vid": 10, "site": "dc-east"}
    ],
    "ip_addresses": [
        {"address": "10.0.0.1/32", "assigned_object_interface": "Loopback0"}
    ]
})
```

### 2. Automatic Field Inheritance

Nested objects automatically inherit parent references:

- **Modules** inherit `device` name from parent `DiodeDevice`
- **Interfaces** inherit `device` name from parent `DiodeDevice`
- **VLANs** inherit `site` from parent `DiodeDevice`
- **IPs** inherit context from assigned interface

### 3. Validation at Creation

Pydantic v2 validates all fields before gRPC submission:

```python
# Malformed VLAN VID raises ValidationError
vlan = DiodeVLAN.from_dict({
    "name": "VLAN100",
    "vid": 9999,  # Invalid! Max is 4094
    "site": "dc-east"
})
# ValidationError: VLAN ID must be between 1 and 4094
```

### 4. Bulk Batch Processing

Efficiently process multiple operations in single gRPC calls:

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor()

# Add multiple operations
for i in range(10):
    device = DiodeDevice.from_dict({...})
    processor.create(device)

results = processor.execute(client)
```

### 5. Dry-Run Mode

Validate changes without committing to NetBox:

```bash
netbox-dio device create device.json --dry-run
PYTHON: output_validation_passed=True
```

---

## Architecture

### Class Hierarchy

```
DiodeDevice
  ├── DiodeInterface (nested)
  ├── DiodeVLAN (nested)
  ├── DiodeModule (nested)
  ├── DiodeModuleBay (nested)
  ├── DiodeIPAddress (nested)
  ├── DiodePrefix (nested)
  └── DiodeCable (nested)

DiodeRack
  ├── device_positions (nested list)

Standalone models (no nesting):
  - DiodeInterface
  - DiodeVLAN
  - DiodeModule
  - DiodeIPAddress
  - DiodePrefix
  - DiodeCable
  - DiodeRack
```

### Conversion Flow

```
Python Dict → Pydantic Model → 
Model.to_protobuf() → gRPC Message → 
convert_*() Functions → Entity List → 
DiodeClient → gRPC Ingestion → NetBox
```

---

## Core Models

### DiodeDevice

**Required fields:** `name`, `site`, `device_type`, `role`

**Nested capabilities:**
- `interfaces` - List of DiodeInterface
- `vlans` - List of DiodeVLAN
- `modules` - List of DiodeModule (auto-inherits device)
- `module_bays` - List of DiodeModuleBay (auto-inherits device)
- `ip_addresses` - List of DiodeIPAddress
- `prefixes` - List of DiodePrefix
- `cables` - List of DiodeCable
- `rack_positions` - For switch stacks/clustered devices

### DiodeInterface

**Required fields:** `name`, `device`, `type`

**Key attributes:**
- `mode` - "access", "trunk", "bridge", "virtual"
- `vlans` - Trunk allowed VLANs
- `untagged_vlan` - Access port VLAN
- `qinq_svlan` - Q-in-Q outer VLAN

### DiodeVLAN

**Required fields:** `name`, `vid`, `site`

**Key attributes:**
- `status` - "active", "reserved", "deprecated"
- `role` - "access", "distribution", "core", "management"
- `group` - VLAN group name
- `qinq_svlan` - Q-in-Q service VLAN

### DiodeModule

**Required fields:** `module_type`

**Auto-inherited:** `device` (when inside DiodeDevice)

**Key attributes:**
- `slot` - Physical slot number
- `serial` - Module serial number
- `asset_tag` - Asset tracking tag

### DiodeModuleBay

**Required fields:** `slot`, `module`

**Auto-inherited:** `device` (when inside DiodeDevice)

**Purpose:** Represents planned/empty slot without module installed

---

## Converters

All top-level models have `to_protobuf()` method, plus convenience functions:

| Converter | Input | Output |
|-----------|-------|--------|
| `convert_device_to_entities` | DiodeDevice | List[Entity] |
| `convert_interface_to_protobuf` | DiodeInterface | Interface |
| `convert_vlan_to_protobuf` | DiodeVLAN | VLAN |
| `convert_ip_to_protobuf` | DiodeIPAddress | IPAddress |
| `convert_prefix_to_protobuf` | DiodePrefix | Prefix |
| `convert_module_to_protobuf` | DiodeModule | Module |
| `convert_module_bay_to_protobuf` | DiodeModuleBay | ModuleBay |
| `convert_cable_to_protobuf` | DiodeCable | Cable |
| `convert_rack_to_protobuf` | DiodeRack | Rack |

---

## Batch Processing

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor(
    validate_before_submit=True,
    continue_on_error=False,
    max_batch_size=100
)

# Add operations
for device in devices:
    processor.create(device)

# Or mixed operations
processor.update(existing_device)
processor.delete("old-device")

# Execute
results = processor.execute(client)

# Analyze
for result in results:
    if result.success:
        print(f"✓ {result.name}")
    else:
        print(f"✗ {result.name}: {result.error}")
```

---

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError

try:
    vlan = DiodeVLAN.from_dict({
        "name": "VLAN100",
        "vid": 9999,  # Invalid
        "site": "dc-east"
    })
except ValidationError as e:
    print(f"Invalid data: {e}")
```

### Connection Errors

```python
from netbox_dio import DiodeConnectionError

try:
    client.create_device(device)
except DiodeConnectionError as e:
    print(f"Cannot connect to Diode: {e}")
```

### Ingestion Errors

```python
from netbox_dio import DiodeIngestionError

try:
    client.create_device(device)
except DiodeIngestionError as e:
    print(f"Ingestion failed: {e.status_code} - {e.message}")
    if e.status_code == 409:
        print("Resource already exists")
```

---

## CLI Usage

```bash
# Create device
netbox-dio device create device.json

# Dry-run mode
netbox-dio device create device.json --dry-run

# Bulk operations
netbox-dio device batch devices.jsonl --progress

# Update device
netbox-dio device update switch-01 --status planned

# Delete
netbox-dio device delete switch-01

# Validate JSON
netbox-dio validate device.json
```

---

## FAQ

### Q: How do I handle site inheritance?

**A:** Most models have `site` field. When placed inside `DiodeDevice`, the device's site is automatically used:

```python
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",  # All VLANs inherit this site
    "vlans": [
        {"name": "VLAN100", "vid": 100}  # site="dc-east" auto-inherited
    ]
})
```

### Q: Can I use string enum values instead of Pydantic classes?

**A:** Yes, all enum fields accept both string values and enum classes:

```python
# Both work
DiodeInterface(type="physical", enabled=True)
DiodeInterface(type=InterfaceType.PHYSICAL, enabled=True)
```

### Q: How many entities can I create per batch?

**A:** Recommended batch size is 50-100 entities. The `BatchProcessor` has a default `max_batch_size=100` to prevent gRPC payload size issues.

### Q: What's the difference between `modules` and `module_bays`?

**A:**
- **modules**: Physical modules with serial numbers, asset tags (e.g., installed supervisor)
- **module_bays**: Planned slots (e.g., "slot 1 is for supervisor") without serial info

### Q: Can I create devices without a client?

**A:** Yes, for validation:

```python
device = DiodeDevice.from_dict({...})
entities = convert_device_to_entities(device)
# Check entities without gRPC call
```

---

## Migration Guide

### From diode-sdk-python

```python
# Old: Manual protobuf construction
device_proto = Device(
    name="switch-01",
    site="dc-east",
    role="access"
)

# New: Pydantic model
from netbox_dio import DiodeDevice
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})
device_proto = device.to_protobuf()
```

### From Direct Device Objects

```python
# Old: Separate objects
device = DiodeDevice(...)
interface = DiodeInterface(...)
vlan = DiodeVLAN(...)

# New: Nested structure
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "interfaces": [interface_dict],
    "vlans": [vlan_dict]
})
```

---

## Support and Resources

- **Documentation:** [docs/api/](./)
- **CLI Reference:** [docs/api/11-cli-reference.md](11-cli-reference.md)
- **GitHub Issues:** https://github.com/...
- **Diode SDK:** https://github.com/netboxlabs/diode-sdk-python

---

## Contributors

- **Architecture:** Device-centric wrapper design
- **Validation:** Pydantic v2 model validation
- **Batch Processing:** Efficient gRPC batching
- **CLI:** Command-line interface with dry-run support

---

*Document version: 1.0 | Last updated: 2026-04-13*

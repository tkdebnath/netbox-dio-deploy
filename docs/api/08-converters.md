# Converter Functions

High-level conversion functions that transform high-level NetBox objects into Diode SDK protobuf messages for gRPC ingestion.

## Table of Contents
- [Overview](#overview)
- [Device Converter](#device-converter)
- [Interface Converter](#interface-converter)
- [VLAN Converter](#vlan-converter)
- [IP Address Converter](#ip-address-converter)
- [Prefix Converter](#prefix-converter)
- [Module Converter](#module-converter)
- [Module Bay Converter](#module-bay-converter)
- [Cable Converter](#cable-converter)
- [Rack Converter](#rack-converter)

---

## Overview

Converters reconcile high-level SDK objects with NetBox Diode protobuf expect than:

```python
from netbox_dio import (
    convert_device_to_entities,
    convert_ip_to_protobuf,
    convert_prefix_to_protobuf,
    convert_vlan_to_protobuf,
    convert_interface_to_protobuf,
    convert_module_to_protobuf,
    convert_module_bay_to_protobuf,
    convert_cable_to_protobuf,
    convert_rack_to_protobuf
)
```

---

## Device Converter

### `convert_device_to_entities(device: DiodeDevice) -> list[Entity]`

**Purpose:** Converts a DiodeDevice and all nested objects into a list of Diode entities.

**Input:**
- Complete DiodeDevice object with optional nested interfaces, VLANs, modules, module_bays, cables, IP addresses, prefixs

**Output:**
- List of protobuf entities ready for gRPC: `[Device, Interface, VLAN, Module, etc.]`

```python
from netbox_dio import DiodeDevice, convert_device_to_entities

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
        {
            "name": "VLAN100",
            "vid": 100,
            "site": "dc-east"
        }
    ],
    "ip_addresses": [
        {
            "address": "192.168.1.1/24",
            "assigned_object_interface": "Vlan100"
        }
    ]
})

entities = convert_device_to_sites(device)
print(f"Created {len(entities)} entities")
# Output: Created 3 entities (1 device + 1 interface + 1 VLAN)
```

**Note:** Interfaces and VLANs contained within device are flattened and added as separate entities.

---

## Interface Converter

### `convert_interface_to_protobuf(interface: DiodeInterface, device: str) -> Interface`

**Purpose:** Converts a DiodeInterface to protobuf Interface message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `interface` | DiodeInterface | Interface object to convert |
| `device` | str | Parent device name (required for context) |

**Returns:**
- `Interface` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeInterface, DiodeDevice, convert_interface_to_protobuf

# Standalone interface conversion
interface = DiodeInterface.from_dict({
    "name": "GigabitEthernet1/0/1",
    "type": "physical",
    "enabled": True,
    "mode": "access",
    "untagged_vlan": "VLAN100",
    "description": "User access port"
})

proto = convert_interface_to_protobuf(interface, "switch-01")
print(proto)
# Interface(
#   name="GigabitEthernet1/0/1",
#   device="switch-01",
#   type="physical",
#   enabled=True,
#   mode="access",
#   untagged_vlan="VLAN100",
#   description="User access port",
#   ...
# )
```

**Device Inheritance:**
The `device` parameter is automatically set on all nested interfaces in DiodeDevice:

```python
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",  # device="switch-01" added automatically
            "type": "physical",
            "enabled": True
        }
    ]
})

# All interfaces in device now have device field set
for interface in device.interfaces:
    print(interface.device)
    # Output: "switch-01" (was automatically injected)
```

---

## VLAN Converter

### `convert_vlan_to_protobuf(vlan: DiodeVLAN, site: str) -> VLAN`

**Purpose:** Converts a DiodeVLAN to protobuf VLAN message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `vlan` | DiodeVLAN | VLAN object to convert |
| `site` | str | Site name (inherited if scope_site not set) |

**Returns:**
- `VLAN` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeVLAN, convert_vlan_to_protobuf

vlan = DiodeVLAN.from_dict({
    "name": "VLAN100",
    "vid": 100,
    "site": "dc-east",
    "status": "active",
    "role": "access",
    "description": "User VLAN"
})

proto = convert_vlan_to_protobuf(vlan, "dc-east")
print(proto)
# VLAN(
#   name="VLAN100",
#   vid=100,
#   scope_site="dc-east",
#   status="active",
#   role="access",
#   description="User VLAN",
#   ...
# )
```

**Site Inheritance:**
If `site` is not provided in the VLAN, it is inherited from the device:

```python
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "vlans": [
        {
            "name": "VLAN100",
            "vid": 100
            # site="dc-east" automatically inherited from device
        }
    ]
})

# Convert VLAN without explicit site
vlan = device.vlans[0]
proto = convert_vlan_to_protobuf(vlan, vlan.site or "dc-east")
```

---

## IP Address Converter

### `convert_ip_to_protobuf(ip: DiodeIPAddress, device: str, interface: Optional[str]) -> IPAddress`

**Purpose:** Converts a DiodeIPAddress to protobuf IPAddress message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip` | DiodeIPAddress | IP address object to convert |
| `device` | str | Parent device name (if interface provided) |
| `interface` | Optional[str] | Interface name this IP is assigned to |

**Returns:**
- `IPAddress` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeIPAddress, convert_ip_to_protobuf

ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "description": "VLAN gateway"
})

# Convert with interface assignment
proto = convert_ip_to_protobuf(
    ip,
    device="switch-01",
    interface="Vlan100"
)

print(proto)
# IPAddress(
#   address="192.168.1.1/24",
#   status="active",
#   description="VLAN gateway",
#   assigned_object_type="dcim.interface",
#   assigned_object_name="Vlan100",
#   ...
# )
```

**IP Address in Device Context:**

When IP is inside a device, it inherits context:

```python
from netbox_dio import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "interfaces": [
        {"name": "Vlan100", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "192.168.1.1/24",
            "assigned_object_interface": "Vlan100"
        }
    ]
})
```

---

## Prefix Converter

### `convert_prefix_to_protobuf(prefix: DiodePrefix, site: str) -> Prefix`

**Purpose:** Converts a DiodePrefix to protobuf Prefix message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | DiodePrefix | Prefix object to convert |
| `site` | str | Site name for prefix scope |

**Returns:**
- `Prefix` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodePrefix, convert_prefix_to_protobuf

prefix = DiodePrefix.from_dict({
    "prefix": "192.168.1.0/24",
    "site": "dc-east",
    "status": "active",
    "role": "network",
    "description": "User LAN"
})

proto = convert_prefix_to_protobuf(prefix, "dc-east")
print(proto)
# Prefix(
#   prefix="192.168.1.0/24",
#   scope_site="dc-east",
#   status="active",
#   role="network",
#   description="User LAN",
#   ...
# )
```

**Site Assignment Inheritance:**

The `site` field on the prefix is simplified - it maps to `scope_site`:

```python
prefix = DiodePrefix.from_dict({
    "prefix": "10.0.0.0/24",
    "site": "site-a",  # This becomes scope_site
    "status": "active"
})
# scope_site is now "site-a" (simplified interface)
```

---

## Module Converter

### `convert_module_to_protobuf(module: DiodeModule, device: str) -> Module`

**Purpose:** Converts a DiodeModule to protobuf Module message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `module` | DiodeModule | Module object to convert |
| `device` | str | Parent device name |

**Returns:**
- `Module` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeModule, convert_module_to_protobuf

module = DiodeModule.from_dict({
    "module_type": "c9500-48yx",
    "device": "switch-01",
    "slot": 3,
    "serial": "FCW2123A0QZ",
    "status": "active"
})

proto = convert_module_to_protobuf(module, "switch-01")
print(proto)
# Module(
#   module_type="c9500-48yx",
#   device="switch-01",
#   slot=3,
#   serial="FCW2123A0QZ",
#   status="active",
#   ...
# )
```

**Device Auto-Inheritance:**
When inside a device, the module doesn't need explicit `device` field:

```python
from netbox_dio import DiodeDevice, DiodeModule

device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "modules": [
        {
            "module_type": "c9500-48yx",
            "slot": 3,
            "serial": "FCW2123A0QZ"
            # device="switch-01" automatically inherited via validator
        }
    ]
})
```

---

## Module Bay Converter

### `convert_module_bay_to_protobuf(module_bay: DiodeModuleBay) -> ModuleBay`

**Purpose:** Converts a DiodeModuleBay to protobuf ModuleBay message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `module_bay` | DiodeModuleBay | Module bay object to convert |

**Returns:**
- `ModuleBay` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeModuleBay, convert_module_bay_to_protobuf

module_bay = DiodeModuleBay.from_dict({
    "device": "switch-01",
    "slot": 1,
    "module": "sup-140",
    "name": "Supervisor Slot"
})

proto = convert_module_bay_to_protobuf(module_bay)
print(proto)
# ModuleBay(
#   device="switch-01",
#   slot=1,
#   module_type="sup-140",
#   name="Supervisor Slot",
#   ...
# )
```

**Nested in Device:**
```python
from netbox_dio import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "chassis-01",
    "device_type": "cisco-c9500-chassis",
    "site": "dc-central",
    "module_bays": [
        {
            "slot": 1,
            "module": "sup-140",
            "device": "chassis-01"  # auto-inherited for module_bays
        }
    ]
})
```

---

## Cable Converter

### `convert_cable_to_protobuf(cable: DiodeCable) -> Cable`

**Purpose:** Converts a DiodeCable to protobuf Cable message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cable` | DiodeCable | Cable object to convert |

**Returns:**
- `Cable` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeCable, convert_cable_to_protobuf

cable = DiodeCable.from_dict({
    "type": "cat6",
    "status": "connected",
    "label": "Switch 01 to Switch 02",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "switch-02",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})

proto = convert_cable_to_prototob(c cable)
print(proto)
# Cable(
#   a_terminated_type="dcim.interface",
#   a_terminated_id=1,
#   b_terminated_type="dcim.interface",
#   b_terminated_id=2,
#   type="cat6",
#   status="connected",
#   label="Switch 01 to Switch 02",
#   ...
# )
```

---

## Rack Converter

### `convert_rack_to_protobuf(rack: DiodeRack) -> Rack`

**Purpose:** Converts a DiodeRack to protobuf Rack message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rack` | DiodeRack | Rack object to convert |

**Returns:**
- `Rack` protobuf message ready for Diode ingestion

```python
from netbox_dio import DiodeRack, convert_rack_to_protobuf

rack = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "device_positions": [
        {"device": "switch-01", "position": 5.0}
    ]
})

proto = convert_rack_to_protobuf(rack)
print(proto)
# Rack(
#   name="rack-01",
#   site="dc-east",
#   location="building-a",
#   u_height=42.0,
#   device_positions=[
#     {"device": "switch-01", "position": 5.0}
#   ]
# )
```

---

## Complete Device Conversion Flow

```python
from netbox_dio import DiodeDevice, convert_device_to_entities

# Define complete device with all components
device = DiodeDevice.from_dict({
    "name": "core-switch",
    "site": "dc-east",
    "location": "building-a",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "rack": "rack-01",
    "position": 10.0,
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "type": "physical",
            "enabled": True,
            "speed": 1000,
            "mode": "trunk",
            "untagged_vlan": "VLAN100",
            "vlans": [10, 20, 30, 100, 200]
        }
    ],
    "vlans": [
        {"name": "VLAN10", "vid": 10, "site": "dc-east"},
        {"name": "VLAN100", "vid": 100, "site": "dc-east"}
    ],
    "modules": [
        {"module_type": "sup-140", "slot": 1, "serial": "S1"},
        {"module_type": "fabric-3", "slot": 2, "serial": "F1"}
    ],
    "module_bays": [
        {"slot": 1, "module": "sup-140"},
        {"slot": 2, "module": "fabric-3"}
    ],
    "ip_addresses": [
        {
            "address": "10.0.0.1/32",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet1/0/1"
        }
    ],
    "cables": [
        {
            "type": "cat6",
            "status": "connected",
            "a_termination": {
                "device": "core-switch",
                "interface": {"name": "GigabitEthernet1/0/1"}
            },
            "b_termination": {
                "device": "distribution",
                "interface": {"name": "GigabitEthernet1/0/1"}
            }
        }
    ]
})

# Convert all to entities
entities = convert_device_to_entities(device)

print(f"Created {len(entities)} entities:")
for entity in entities:
    print(f"  - {type(entity).__name__}: {entity.name}")
# Output:
#   - Device: core-switch
#   - Interface: GigabitEthernet1/0/1
#   - VLAN: VLAN10
#   - VLAN: VLAN100
#   - Module: sup-140
#   - Module: fabric-3
#   - ModuleBay: slot 1
#   - ModuleBay: slot 2
#   - IPAddress: 10.0.0.1/32
#   - Cable: cat6
```

---

## Error Handling

### Missing Required Fields

```python
from netbox_dio import DiodeInterface

# Missing required 'device' field
try:
    interface = DiodeInterface.from_dict({
        "name": "Gi1/0/1",
        "type": "physical",
        "enabled": True
        # "device" is required!
    })
except ValidationError as e:
    print(f"Validation error: {e}")
    # ValidationError: 1 validation error for DiodeInterface
    # device
    #   Field required
```

### Invalid Interface Assignment

```python
from netbox_dio import DiodeIPAddress

# IP assigned to non-existent interface
ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "assigned_object_interface": "NonExistentInterface",
    "status": "active"
})
# Valid at validation time - device existence checked at gRPC commit time
```

---

## Converter Function Summary

| Function | Input Type | Output Type | Purpose |
|----------|------------|-------------|---------|
| `convert_device_to_entities` | DiodeDevice | list[Entity] | Converts device + all nested objects |
| `convert_interface_to_protobuf` | DiodeInterface + device | Interface | Converts interface to protobuf |
| `convert_vlan_to_protobuf` | DiodeVLAN + site | VLAN | Converts VLAN to protobuf |
| `convert_ip_to_protobuf` | DiodeIPAddress + context | IPAddress | Converts IP to protobuf |
| `convert_prefix_to_protobuf` | DiodePrefix + site | Prefix | Converts prefix to protobuf |
| `convert_module_to_protobuf` | DiodeModule | Module | Converts module to protobuf |
| `convert_module_bay_to_protobuf` | DiodeModuleBay | ModuleBay | Converts module bay to protobuf |
| `convert_cable_to_protobuf` | DiodeCable | Cable | Converts cable to protobuf |
| `convert_rack_to_protobuf` | DiodeRack | Rack | Converts rack to protobuf |

# DiodeDevice

The primary device model representing a network device in NetBox.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Device with Interfaces](#device-with-interfaces)
- [Device with VLANs](#device-with-vlans)
- [Device with Modules](#device-with-modules)
- [Device with IP Addresses](#device-with-ip-addresses)
- [Device with Prefixes](#device-with-prefixes)
- [Device with Cables](#device-with-cables)
- [Clustered/Switch Stack Devices](#clusteredswitch-stack-devices)
- [Device Attributes](#device-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeDevice

# Minimal device - only required fields
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router"
})

# Device with common fields
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "access-switch",
    "status": "active",
    "serial": "FCW2123A0QY",
    "asset_tag": "AT-001",
    "platform": "cisco-ios",
    "rack": "rack-01",
    "position": 10.0,
    "comments": "Primary access switch for building A"
})
```

---

## Device with Interfaces

```python
from netbox_dio import DiodeDevice, convert_device_to_entities

device = DiodeDevice.from_dict({
    "name": "core-router",
    "site": "dc-central",
    "device_type": "cisco-asr1001",
    "role": "core-router",
    "interfaces": [
        {
            "name": "GigabitEthernet0/0/0",
            "device": "core-router",
            "type": "physical",
            "enabled": True,
            "description": "Uplink to distribution",
            "speed": 1000,
            "duplex": "full",
            "vrf": "main"
        },
        {
            "name": "GigabitEthernet0/0/1",
            "device": "core-router",
            "type": "physical",
            "enabled": True,
            "description": "Backup uplink",
            "speed": 1000,
            "duplex": "full"
        }
    ]
})

# Convert to entities
entities = convert_device_to_entities(device)
# Returns: 1 Device entity + 2 Interface entities = 3 total
```

---

## Device with VLANs

```python
from netbox_dio import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "access-switch",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access-switch",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "device": "access-switch",
            "type": "physical",
            "enabled": True,
            "mode": "trunk",
            "untagged_vlan": "VLAN100"
        },
        {
            "name": "GigabitEthernet1/0/2",
            "device": "access-switch",
            "type": "physical",
            "enabled": True,
            "mode": "access",
            "untagged_vlan": "VLAN100"
        }
    ],
    "vlans": [
        {"name": "VLAN100", "vid": 100, "site": "dc-east"},
        {"name": "VLAN200", "vid": 200, "site": "dc-east"}
    ]
})
```

---

## Device with Modules

```python
from netbox_dio import DiodeDevice

# Chassis with modules - device is auto-inherited
chassis = DiodeDevice.from_dict({
    "name": "chassis-01",
    "site": "dc-central",
    "device_type": "cisco-c9500-chassis",
    "role": "core-chassis",
    "modules": [
        {"module_type": "sup-140", "slot": 1, "serial": "FCW2123A0QY", "status": "active"},
        {"module_type": "fabric-1", "slot": 2, "serial": "FCW2124A0QR", "status": "active"},
    ]
})

# Module bays with slot assignment - device is auto-inherited
chassis2 = DiodeDevice.from_dict({
    "name": "chassis-02",
    "site": "dc-central",
    "device_type": "cisco-c9500-chassis",
    "role": "core-chassis",
    "module_bays": [
        {"slot": 1, "module": "sup-140", "name": "Supervisor Slot"},
        {"slot": 2, "module": "fabric-1", "name": "Fabric Slot"},
    ]
})
```

---

## Device with IP Addresses

```python
from netbox_dio import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "dc-east",
    "device_type": "cisco-9300",
    "role": "core-router",
    "interfaces": [
        {"name": "Loopback0", "device": "router-01", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.0.0.1/32",
            "status": "active",
            "dns_name": "router01.example.com",
            "assigned_object_interface": "Loopback0"
        }
    ]
})
```

---

## Device with Prefixes

```python
from netbox_dio import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "boundary-router",
    "site": "dc-east",
    "device_type": "cisco-asr1002",
    "role": "boundary-router",
    "prefixes": [
        {
            "prefix": "192.168.1.0/24",
            "site": "dc-east",
            "status": "active",
            "role": "network",
            "description": "LAN subnet"
        },
        {
            "prefix": "10.0.0.0/8",
            "site": "dc-east",
            "is_pool": True,
            "description": "Private address space"
        }
    ]
})
```

---

## Device with Cables

```python
from netbox_dio import DiodeDevice, DiodeCable

device = DiodeDevice.from_dict({
    "name": "core-switch",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "core",
    "interfaces": [
        {"name": "GigabitEthernet1/0/1", "device": "core-switch", "type": "physical"},
        {"name": "GigabitEthernet1/0/2", "device": "core-switch", "type": "physical"}
    ],
    "cables": [
        {
            "type": "cat6a",
            "status": "connected",
            "a_termination": {
                "device": "core-switch",
                "interface": {"name": "GigabitEthernet1/0/1", "device": "core-switch", "type": "physical"}
            },
            "b_termination": {
                "device": "access-switch",
                "interface": {"name": "GigabitEthernet1/0/1", "device": "access-switch", "type": "physical"}
            }
        }
    ]
})
```

---

## Clustered/Switch Stack Devices

```python
from netbox_dio import DiodeDevice

# Stack of 6 switches represented as one logical device
stack = DiodeDevice.from_dict({
    "name": "core-switch-stack",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "core",
    "cluster": "stack-01",
    "rack": "rack-01",
    "position": 10.0,
    # Track all 6 members with rack positions
    "rack_positions": [
        {"rack": "rack-01", "position": 10.0},
        {"rack": "rack-01", "position": 12.0},
        {"rack": "rack-01", "position": 14.0},
        {"rack": "rack-01", "position": 16.0},
        {"rack": "rack-01", "position": 18.0},
        {"rack": "rack-01", "position": 20.0},
    ]
})
```

---

## Device Attributes

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Device name (1-64 characters) |
| `site` | str | Site name |
| `device_type` | str | Device type model name |
| `role` | str | Device role name |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `serial` | str | Serial number |
| `asset_tag` | str | Asset tag |
| `platform` | str | Device platform |
| `status` | str | Device status (active, offline, planned) |
| `rack` | str | Primary rack name |
| `position` | float | U position in rack |
| `location` | str | Location within site |
| `cluster` | str | Device cluster/group name |
| `rack_positions` | list[dict] | Rack positions for clustered devices |
| `interfaces` | list[DiodeInterface] | Interfaces on the device |
| `vlans` | list[DiodeVLAN] | VLANs on the device |
| `modules` | list[DiodeModule] | Modules on the device |
| `module_bays` | list[DiodeModuleBay] | Module bays on the device |
| `cables` | list[DiodeCable] | Cables connected to the device |
| `prefixes` | list[DiodePrefix] | Prefixes assigned to the device |
| `ip_addresses` | list[DiodeIPAddress] | IP addresses assigned to the device |

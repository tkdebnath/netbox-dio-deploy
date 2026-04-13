# DiodeModule and DiodeModuleBay

Represents inventory modules and module bays in rack chassis.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Module Inside Device](#module-inside-device)
- [Chassis with Multiple Modules](#chassis-with-multiple-modules)
- [Module Bays (Old API)](#module-bays-old-api)
- [Supervisor Module Example](#supervisor-module-example)
- [Fabric Module Example](#fabric-module-example)
- [Module Attributes](#module-attributes)
- [Module Bay Attributes](#module-bay-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeModule, ModuleStatus

# Minimal module - requires module_type
module = DiodeModule.from_dict({
    "module_type": "cisco-10g-sfp-plus"
})

# Complete module with all fields
module = DiodeModule.from_dict({
    "module_type": "cisco-10g-sfp-plus",
    "device": "switch-01",  # Required when standalone
    "slot": 1,
    "status": ModuleStatus.active,
    "serial": "FCW2123A0QY",
    "asset_tag": "M-001",
    "description": "SFP+ transceiver module",
    "tags": ["sfp", "10g"]
})
```

---

## Module Inside Device

When a DiodeModule is nested inside a DiodeDevice, the `device` field is **automatically inherited**. You do not need to specify it:

```python
from netbox_dio import DiodeDevice

# Device with - modules automatically inherit device name
device = DiodeDevice.from_dict({
    "name": "core-chassis",
    "site": "dc-central",
    "device_type": "cisco-c9500",
    "role": "core",
    "modules": [
        {
            "module_type": "sup-140",
            "slot": 1,
            "serial": "FCW2123A0QY",
            "status": "active"
        },
        {
            "module_type": "fabric-1",
            "slot": 2,
            "serial": "FCW2124A0QR",
            "status": "active"
        },
        {
            "module_type": "cisco-48port-gig",
            "slot": 3,
            "serial": "FCW2125A0QS",
            "asset_tag": "M-003",
            "status": "installed"
        }
    ]
})

# Each module automatically has device="core-chassis" after validation
# The convert_device_to_entities() will pick this up
```

**Why device is optional inside DiodeDevice:**
- Eliminates redundancy - you don't write the same device name 10 times
- Model validator (`inherit_device_name_to_modules`) automatically injects it
- Single source of truth - change device name once at top level

---

## Chassis with Multiple Modules

```python
from netbox_dio import DiodeDevice, ModuleStatus

# Cisco Catalyst 9500 chassis with supervisor and line cards
c9500 = DiodeDevice.from_dict({
    "name": "c9500-01",
    "site": "dc-east",
    "device_type": "cisco-c9500-chassis",
    "role": "core-switch",
    "modules": [
        # Supervisor engine in slot 1
        {
            "module_type": "sup-140",
            "slot": 1,
            "serial": "FCW2123A0QX",
            "status": ModuleStatus.active,
            "description": "Supervisor Engine 140"
        },
        # Fabric module in slot 2
        {
            "module_type": "fabric-3",
            "slot": 2,
            "serial": "FCW2123A0QY",
            "status": ModuleStatus.active,
            "description": "Switch Fabric Module 3"
        },
        # Line card - 48 port 10GbE
        {
            "module_type": "c9500-48yx",
            "slot": 3,
            "serial": "FCW2123A0QZ",
            "asset_tag": "M-003",
            "status": ModuleStatus.active,
            "description": "48 port 10GbE line card"
        },
        # Line card - 32 port 10GbE
        {
            "module_type": "c9500-32x",
            "slot": 4,
            "serial": "FCW2123A0RA",
            "status": ModuleStatus.active,
            "description": "32 port 10GbE line card"
        },
        # Power supply module
        {
            "module_type": "c9500-pwr-1100w",
            "slot": 5,
            "serial": "FCW2123A0RB",
            "asset_tag": "P-001",
            "status": ModuleStatus.installed,
            "description": "1100W power supply"
        }
    ]
})
```

---

## Module Bays (Old API)

Module bays represent physical slots in a chassis that accept modules. They use a different structure than standalone DiodeModule:

```python
from netbox_dio import DiodeDevice

# Using module_bays list instead of modules
device = DiodeDevice.from_dict({
    "name": "chassis-01",
    "site": "dc-central",
    "device_type": "cisco-c9500-chassis",
    "role": "core-chassis",
    "module_bays": [
        {
            "slot": 1,
            "module": "sup-140",
            "name": "Supervisor Slot",
            "description": "Slot for supervisor engine"
        },
        {
            "slot": 2,
            "module": "fabric-1",
            "name": "Fabric Slot",
            "description": "Slot for fabric module"
        },
        {
            "slot": 3,
            "module": "c9500-48yx",
            "description": "Line card slot 3"
        }
    ]
})
```

**ModuleBay vs Module difference:**

| Field | DiodeModule | DiodeModuleBay |
|-------|-------------|----------------|
| `module_type` | ✅ | ❌ (uses `module` + `slot`) |
| `device` | Optional (inherited) | Optional (inherited) |
| `slot` | ❌ | ✅ Required |
| `module` | ❌ | ✅ Required - type name |
| `serial` | ✅ | ❌ |
| `asset_tag` | ✅ | ❌ |

**When to use module_bays:**
- You're creating a chassis/planning module placements
- You want to indicate "slot 1 is for supervisor" without having a module installed yet
- Simple slot-to-module-type mapping

**When to use modules:**
- A module is physically present with serial number
- You need asset tracking
- Multiple instances in same slot (e.g., standby supervisor)

---

## Supervisor Module Example

```python
from netbox_dio import DiodeDevice, ModuleStatus

# Core switch with redundant supervisors
distribution = DiodeDevice.from_dict({
    "name": "dist-switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "distribution",
    "modules": [
        {
            "module_type": "sup-720",
            "slot": 1,
            "serial": "FCW2123A0QX",
            "asset_tag": "SUP-001",
            "status": ModuleStatus.active,
            "description": "Primary supervisor engine",
            "tags": ["supervisor", "active"]
        },
        {
            "module_type": "sup-720",
            "slot": 2,
            "serial": "FCW2123A0QY",
            "asset_tag": "SUP-002",
            "status": ModuleStatus.installed,
            "description": "Standby supervisor engine",
            "tags": ["supervisor", "standby"]
        }
    ]
})
```

---

## Fabric Module Example

```python
from netbox_dio import DiodeDevice

# Chassis with fabric modules for fabric-less architecture
cisco_fabric = DiodeDevice.from_dict({
    "name": "fabric-chassis",
    "site": "dc-central",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "modules": [
        {
            "module_type": "fabric-1",
            "slot": 2,
            "serial": "FCW2124A0QR",
            "status": "active",
            "description": "Switch Fabric Module 1"
        },
        {
            "module_type": "fabric-1",
            "slot": 3,
            "serial": "FCW2124A0QS",
            "status": "active",
            "description": "Switch Fabric Module 2"
        }
    ]
})
```

---

## Module Attributes

### DiodeModule Fields

**Required Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `module_type` | str | Module model/type name (e.g., "sup-140", "c9500-48yx") |

**Optional Fields (required when standalone):**
| Field | Type | Description |
|-------|------|-------------|
| `device` | str | Parent device name (auto-inherited when inside DiodeDevice) |
| `slot` | int | Physical slot number where module is installed |
| `serial` | str | Module serial number |
| `asset_tag` | str | Asset tracking tag |
| `status` | str | Module status |
| `description` | str | Module description |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Additional metadata |
| `owner` | str | Owner reference |
| `comments` | str | Module comments |
| `tags` | list[str] | Module tags |

### DiodeModuleBay Fields

| Field | Type | Description |
|-------|------|-------------|
| `device` | str | Parent device name (auto-inherited) |
| `slot` | int | Slot number identifier - Required! |
| `module` | str | Module type installed - Required! |
| `name` | str | Module bay name |
| `label` | str | Module bay label |
| `description` | str | Module bay description |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Metadata |
| `owner` | str | Owner |
| `tags` | list[str] | Tags |

---

## Valid Status Values

### DiodeModule Status

```python
from netbox_dio import ModuleStatus

# Using enum (recommended)
module = DiodeModule.from_dict({
    "module_type": "sup-140",
    "status": ModuleStatus.active  # or installed, deprecated, retired
})

# Using string (also works)
module = DiodeModule.from_dict({
    "module_type": "sup-140",
    "status": "active"
})

# Valid values:
# - "active" - Module is active and operational
# - "installed" - Module is installed but not active
# - "deprecated" - Module is deprecated
# - "retired" - Module has been retired
```

## CompleExmaples

### Standalone Module with Full Serialization
```python
from netbox_dio import DiodeModule
from netboxlabs.diode.sdk.ingester import Module

# Create module object
module = DiodeModule.from_dict({
    "module_type": "c9500-48yx",
    "device": "switch-01",
    "slot": 3,
    "serial": "FCW2123A0QZ",
    "asset_tag": "M-001",
    "status": "active",
    "description": "48 port 10GbE line card",
    "tags": ["linecard", "10g"]
})

# Convert to protobuf for gRPC
proto_module = module.to_protobuf()
print(proto_module)
# Module(
#   module_type="c9500-48yx",
#   device="switch-01",
#   slot=3,
#   serial="FCW2123A0QZ",
#   asset_tag="M-001",
#   status="active",
#   description="48 port 10GbE line card",
#   tags=['linecard', '10g']
# )
```

### Rack Planning with Module Bays
```python
from netbox_dio import DiodeDevice

# Plan module bays before installing modules
planned_chassis = DiodeDevice.from_dict({
    "name": "planned-c9500",
    "site": "dc-west",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "module_bays": [
        {"slot": 1, "module": "sup-140", "description": "Supervisor slot"},
        {"slot": 2, "module": "fabric-3", "description": "Fabric slot"},
        {"slot": 3, "module": "c9500-48yx", "description": "Line card slot"},
        {"slot": 4, "module": "c9500-48yx", "description": "Line card slot"},
        {"slot": 5, "module": "c9500-pwr-1100w", "description": "Power supply"}
    ]
})
```

### Mid-Rollout Module Addition
```python
from netbox_dio import DiodeDevice, DiodeModule

# Device already exists - add module via converter
device = DiodeDevice.from_dict({
    "name": "existing-switch",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "modules": [
        {
            "module_type": "c9200-24p",
            "slot": 1,
            "serial": "FCW2123A0QA",
            "status": "active"
        }
    ]
})

# Add new module to existing device
new_module = DiodeModule.from_dict({
    "module_type": "c9200-8x",
    "device": "existing-switch",  # Auto-inherited, but explicit is fine
    "slot": 2,
    "serial": "FCW2123A0QB",
    "status": "active"
})
```

### Module with Custom Fields
```python
from netbox_dio import DiodeModule

# Module with NetBox custom fields
module = DiodeModule.from_dict({
    "module_type": "sup-140",
    "slot": 1,
    "serial": "FCW2123A0QX",
    "custom_fields": {
        "department": "network",
        "cost_center": "IT-001",
        "warranty_expiry": "2028-12-31",
        "vendor": "cisco"
    }
})
```

### Failing Module Status Transition
```python
from netbox_dio import DiodeModule, ModuleStatus

# Deprecated module
deprecated_module = DiodeModule.from_dict({
    "module_type": "sup-6",
    "slot": 1,
    "status": ModuleStatus.deprecated,
    "description": "Legacy supervisor - plan replacement",
    "comments": "Replacement scheduled for Q2 2026"
})

# Retired module
retired_module = DiodeModule.from_dict({
    "module_type": "cisco-48g",
    "slot": 3,
    "status": ModuleStatus.retired,
    "description": "Retired - removed from inventory"
})
```

---

## Inheritance Examples

### Site Inheritance
```python
from netbox_dio import DiodeDevice

# Device has site - all modules inherit it automatically
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9500",
    "role": "core",
    "modules": [
        # No site needed - inherits from parent device
        {"module_type": "sup-140", "slot": 1}
    ]
})
```

### Location Inheritance
```python
from netbox_dio import DiodeDevice

# With location field
device = DiodeDevice.from_dict({
    "name": "chassis-01",
    "site": "dc-central",
    "location": "building-a-floor-2",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "modules": [
        # Inherits site AND location from parent
        {"module_type": "fabric-3", "slot": 2}
    ]
})
```

---

## Common Patterns

### Supervisor + Line Cards
```python
from netbox_dio import DiodeDevice

core_switch = DiodeDevice.from_dict({
    "name": "core-c9500",
    "site": "dc-central",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "modules": [
        # Supervisor
        {"module_type": "sup-140", "slot": 1, "serial": "S1"},
        # Fabric
        {"module_type": "fabric-3", "slot": 2, "serial": "F1"},
        # Line cards
        {"module_type": "c9500-48yx", "slot": 3, "serial": "LC1"},
        {"module_type": "c9500-48yx", "slot": 4, "serial": "LC2"},
        # Power supplies
        {"module_type": "c9500-pwr-1100w", "slot": 5, "asset_tag": "PS1"},
        {"module_type": "c9500-pwr-1100w", "slot": 6, "asset_tag": "PS2"}
    ]
})
```

### Access Switch Single Module
```python
from netbox_dio import DiodeDevice

access_switch = DiodeDevice.from_dict({
    "name": "access-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "modules": [
        {"module_type": "c9200-24p", "slot": 1}
    ]
})
```

### Mixed Module Bay and Module
```python
from netbox_dio import DiodeDevice

planned_device = DiodeDevice.from_dict({
    "name": "planned-chassis",
    "site": "dc-west",
    "device_type": "cisco-c9500-chassis",
    "role": "core",
    "module_bays": [
        {"slot": 1, "module": "sup-140"},  # Planned but not installed
        {"slot": 2, "module": "fabric-1"}
    ],
    "modules": [
        # Already installed somewhere else
        {"module_type": "c9500-48yx", "device": "different-chassis", "slot": 3}
    ]
})
```

# DiodeCable

Represents a physical cable connection between network devices or interfaces in NetBox.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Cable Between Two Devices](#cable-between-two-devices)
- [Cable with Termination Objects](#cable-with-termination-objects)
- [Device-Agnostic Cable](#device-agnostic-cable)
- [Cable Attributes](#cable-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeCable, CableType

# Minimal cable - requires type and both terminations
cable = DiodeCable.from_dict({
    "type": "cat6",
    "status": "connected",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "switch-02",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})

# Complete cable with all fields
cable = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "a_termination": {
        "device": "core-switch",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "distribution-switch",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "label": "Core-Dist Fiber Uplink",
    "length": 150.5,
    "length_unit": "m",
    "description": "Primary uplink fiber between core and distribution",
    "tags": ["fiber", "uplink", "10g"]
})
```

---

## Cable Between Two Devices

```python
from netbox_dio import DiodeCable, CableStatus

# Access switch uplink to distribution
access_to_dist = DiodeCable.from_dict({
    "type": "cat6a",
    "status": CableStatus.connected,
    "a_termination": {
        "device": "access-switch-01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "distribution-switch",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "label": "Access-01 to Distribution Uplink",
    "description": "Cat6a uplink for 1G connection"
})

# Core router to firewall
core_to_fw = DiodeCable.from_dict({
    "type": "fiber-multimode",
    "status": CableStatus.connected,
    "a_termination": {
        "device": "core-router",
        "interface": {"name": "GigabitEthernet0/0/0"}
    },
    "b_termination": {
        "device": "firewall-01",
        "interface": {"name": "GigabitEthernet0/0/1"}
    },
    "label": "Core to Firewall",
    "description": "10G fiber uplink to firewall"
})
```

---

## Device-Agnostic Cable (Generic Objects)

When connecting to non-device objects (patch panels, cabinet panels, etc.):

```python
from netbox_dio import DiodeCable

# Cable to patch panel
patch_panel_cable = DiodeCable.from_dict({
    "type": "cat6",
    "status": "connected",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "type": "dcim.patchpanel",
        "name": "PDP-01",
        "port": 1
    },
    "label": "To Patch Panel",
    "description": "Connection to wall jack"
})

# Server to patch panel
server_cable = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "a_termination": {
        "device": "server-rack-01",
        "interface": {"name": "eth0"}
    },
    "b_termination": {
        "type": "dcim.patchpanel",
        "name": "PDP-02",
        "port": 24
    }
})

# Passive device connection (no device)
passive_cable = DiodeCable.from_dict({
    "type": "fiber",
    "status": "connected",
    "a_termination": {
        "type": "dcim.device_bay",
        "name": " bay-1"
    },
    "b_termination": {
        "type": "virtual"
        "name": "interface-1
    }
})
```

---

## Cable Properties Reference

### Cable Type Values

| Type | Description |
|------|-------------|
| "cat5e" | Category 5e Ethernet cable |
| "cat6" | Category 6 Ethernet cable |
| "cat6a" | Category 6a Ethernet cable |
| "cat7" | Category 7 Ethernet cable |
| "cat8" | Category 8 Ethernet cable |
| "fiber-singlemode" | Single-mode fiber optic |
| "fiber-multimode" | Multimode fiber optic |
| "coaxial" | Coaxial cable |
| "copper-pair" | Copper pair telephone |
| "other" | Other/unspecified type |

### Cable Status Values

| Status | Description |
|--------|-------------|
| "connected" | Cable is actively connected |
| "planned" | Cable is planned but not installed |
| "deprovisioned" | Cable removed from service |
| "testing" | Cable under testing |

### Length and Unit

```python
# Cable with length
cable_length = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "a_termination": {"device": "switch-01", "interface": {"name": "Gi1/0/1"}},
    "b_termination": {"device": "switch-02", "interface": {"name": "Gi1/0/1"}},
    "length": 50.0,
    "length_unit": "m",
    "description": "50m Cat6a run"
})

# Cable without explicit length (inferred from label/description)
cable_no_length = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "a_termination": {"device": "router-01", "interface": {"name": "TenG1/0/0"}},
    "b_termination": {"device": "fw-01", "interface": {"name": "TenG1/0/0"}},
    "length": 2.5,
    "length_unit": "km",
    "description": "2.5km fiber link"
})
```

---

## Common Cable Scenarios

### Intra-Rack Cabling

```python
from netbox_dio import DiodeCable

# Switch to patch panel in same rack
intra_rack = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "label": "Rack A-12 Switch Patch",
    "a_termination": {
        "device": "switch-rack-a",
        "interface": {"name": "GigabitEthernet1/0/48"}
    },
    "b_termination": {
        "type": "dcim.patchpanel",
        "name": "patch-panel-rack-a",
        "port": 48
    }
})
```

### Inter-Rack Cabling

```python
from netbox_dio import DiodeCable

# Cross-building fiber connection
inter_rack = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "label": "Building A to Building B Fiber",
    "a_termination": {
        "device": "core-building-a",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "core-building-b",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "length": 1200.0,
    "length_unit": "m",
    "description": "1.2km fiber inter-building link"
})
```

### Console Cabling

```python
from netbox_dio import DiodeCable

# Console cable to management switch
console_cable = DiodeCable.from_dict({
    "type": "console",
    "status": "connected",
    "label": "Console Port 1",
    "a_termination": {
        "device": "router-01",
        "interface": {"name": "Consoleport0/0/0"}
    },
    "b_termination": {
        "device": "console-server",
        "interface": {"name": "GigabitEthernet0/1"}
    },
    "description": "Out-of-band management console"
})
```

---

## Cable Termination Fields

### Supported Termination Types

| Type | Required Fields |
|------|-----------------|
| Interface | `device`, `interface` |
| Front Port | `device`, `front_port` |
| Rear Port | `device`, `rear_port` |
| Virtual Interface | `device`, `virtual_chassis` |
| Device Bay | `device`, `device_bay` |

### Interface Termination Example

```python
from netbox_dio import DiodeCable

# Standard interface termination
interface_term = DiodeCable.from_dict({
    "type": "cat6",
    "status": "connected",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "switch-02",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})
```

### Front/Rear Port Termination

```python
from netbox_dio import DiodeCable

# Front port termination (wall jack side)
front_port_term = DiodeCable.from_dict({
    "type": "patch-cord",
    "status": "connected",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "patch-panel-01",
        "front_port": {"name": "Port 1"}
    }
})

# Rear port termination (patch panel side)
rear_port_term = DiodeCable.from_dict({
    "type": "patch-cord",
    "status": "connected",
    "a_termination": {
        "device": "patch-panel-01",
        "rear_port": {"name": "Port 1"}
    },
    "b_termination": {
        "device": "another-switch",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})
```

### Virtual Interface Termination

```python
from netbox_dio import DiodeCable

# Virtual chassis member
virtual_chassis = DiodeCable.from_dict({
    "type": "vc-cable",
    "status": "connected",
    "a_termination": {
        "device": "vswitch-main",
        "interface": {"name": "et0"}
    },
    "b_termination": {
        "device": "vswitch-member",
        "interface": {"name": "et0"}
    }
})
```

---

## Cable Attributes

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | str | Cable type (cat5e, cat6, fiber-singlemode, etc.) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | Cable status (connected, planned, deprovisioned, testing) |
| `a_termination` | dict | Termination object at end A |
| `b_termination` | dict | Termination object at end B |
| `label` | str | Cable label/tag |
| `length` | float | Length of cable |
| `length_unit` | str | Unit for length (m, km, ft, in) |
| `description` | str | Cable description |
| `tags` | list[str] | Cable tags |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Additional metadata |
| `comments` | str | Cable comments |

### Termination Object Fields

#### Interface Termination
| Field | Type | Description |
|-------|------|-------------|
| `device` | str | Parent device name |
| `interface` | dict | Interface object with `name` field |
| `interface.type` | str | Interface name (e.g., "GigabitEthernet1/0/1") |

#### Patch Panel Termination
| Field | Type | Description |
|-------|------|-------------|
| `device` | str | Device name (patch panel) |
| `front_port` | dict | Front port object |
| `rear_port` | dict | Rear port object |

#### Generic Object Termination
| Field | Type | Description |
|-------|------|-------------|
| `type` | str | Object type (e.g., "dcim.patchpanel") |
| `name` | str | Object name |
| `instance` | int | Port/instance number |

---

## Cable with Device

```python
from netbox_dio import DiodeDevice, DiodeCable

# Device with cables defined internally
device_with_cables = DiodeDevice.from_dict({
    "name": "access-switch",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "interfaces": [
        {"name": "GigabitEthernet1/0/1", "type": "physical"},
        {"name": "GigabitEthernet1/0/24", "type": "physical"}
    ],
    "cables": [
        {
            "type": "cat6a",
            "status": "connected",
            "label": "Upstream to Distribution",
            "a_termination": {
                "device": "distribution-switch-01",
                "interface": {"name": "GigabitEthernet1/0/1"}
            },
            "b_termination": {
                "device": "access-switch",
                "interface": {"name": "GigabitEthernet1/0/24"}
            }
        }
    ]
})
```

## Multi-Device Cable Chain

```python
from netbox_dio import DiodeCable

# Cable chain: Access -> Distribution -> Core
access_to_dist = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "label": "Access to Distribution",
    "a_termination": {
        "device": "access-switch-01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "distribution-switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})

dist_to_core = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "label": "Distribution to Core",
    "a_termination": {
        "device": "distribution-switch-01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "core-switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    }
})

core_to_firewall = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "label": "Core to Firewall",
    "a_termination": {
        "device": "core-switch-01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "firewall-01",
        "interface": {"name": "GigabitEthernet0/0/1"}
    }
})
```

---

## Cable Status Flow

```python
from netbox_dio import DiodeCable, CableStatus

# Planned cable (installation scheduled)
planned = DiodeCable.from_dict({
    "type": "cat6a",
    "status": CableStatus.planned,
    "a_termination": {
        "device": "switch-placeholder",
        "interface": {"name": "Gi1/0/1"}
    },
    "b_termination": {
        "device": "patch-panel-placeholder",
        "port": 1
    },
    "description": "Cable planned for next maintenance window"
})

# Connected cable (active)
connected = DiodeCable.from_dict({
    "type": "cat6a",
    "status": CableStatus.connected,
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "Gi1/0/1"}
    },
    "b_termination": {
        "device": "patch-panel-01",
        "port": 1
    }
})

# Testing cable (under validation)
testing = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": CableStatus.testing,
    "a_termination": {
        "device": "router-01",
        "interface": {"name": "Te1/0/1"}
    },
    "b_termination": {
        "device": "router-02",
        "interface": {"name": "Te1/0/1"}
    },
    "description": "Link under performance testing"
})

# Deprovisioned cable (removed from service)
deprovisioned = DiodeCable.from_dict({
    "type": "cat5e",
    "status": CableStatus.deprovisioned,
    "a_termination": {
        "device": "switch-old",
        "interface": {"name": "Gi1/0/1"}
    },
    "b_termination": {
        "device": "switch-old",
        "interface": {"name": "Gi1/0/2"}
    },
    "description": "Decommissioned cable"
})
```

---

## Cable Labeling Best Practices

```python
from netbox_dio import DiodeCable

# Descriptive label with device and interface info
clear_label = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "label": "SW01-Gi1/0/24 to PP01-P1",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "patch-panel-01",
        "rear_port": {"name": "Port 1"}
    },
    "description": "UST-01 to wall jack in conference room A"
})

# Short label for internal parity
short_label = DiodeCable.from_dict({
    "type": "fiber",
    "status": "connected",
    "label": "F1",
    "a_termination": {
        "device": "core-01",
        "interface": {"name": "TenG1/0/1"}
    },
    "b_termination": {
        "device": "core-02",
        "interface": {"name": "TenG1/0/1"}
    }
})

# Long-form label for documentation
long_label = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "label": "ACCESS-SW01 Gi1/0/24 -> DIST-SW01 Gi1/0/1 Trunk Uplink",
    "a_termination": {
        "device": "access-sw01",
        "interface": {"name": "GigabitEthernet1/0/24"}
    },
    "b_termination": {
        "device": "distribution-sw01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "description": "Primary 1G trunk uplink for VLANs 10, 20, 30, 100"
})
```

---

## Common Cable Type Patterns

### Copper Ethernet Cables
```python
from netbox_dio import DiodeCable

# Patch cable (device to patch panel)
patch_cable = DiodeCable.from_dict({
    "type": "cat5e",
    "status": "connected",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "GigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "patch-panel-01",
        "front_port": {"name": "Port 1"}
    }
})

# Vertical run cable (patch panel to rack)
vertical_cable = DiodeCable.from_dict({
    "type": "cat6",
    "status": "connected",
    "a_termination": {
        "device": "patch-panel-01",
        "rear_port": {"name": "Port 1"}
    },
    "b_termination": {
        "device": "patch-panel-02",
        "front_port": {"name": "Port 24"}
    }
})

# High speed run
long_run = DiodeCable.from_dict({
    "type": "cat6a",
    "status": "connected",
    "length": 85.5,
    "length_unit": "m",
    "a_termination": {
        "device": "core-rack-switch",
        "interface": {"name": "TenGig1/0/1"}
    },
    "b_termination": {
        "device": "dist-rack-switch",
        "interface": {"name": "TenGig1/0/1"}
    }
})
```

### Fiber Optic Cables
```python
from netbox_dio import DiodeCable

# Short patch fiber
fiber_patch = DiodeCable.from_dict({
    "type": "fiber-multimode",
    "status": "connected",
    "length": 2.0,
    "length_unit": "m",
    "a_termination": {
        "device": "switch-01",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "patch-panel-fiber",
        "port": 1
    }
})

# Long distance singlemode
long_haul = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "length": 5.2,
    "length_unit": "km",
    "label": "Building A to Building B",
    "a_termination": {
        "device": "core-building-a",
        "interface": {"name": "FortyGigE1/0/1"}
    },
    "b_termination": {
        "device": "core-building-b",
        "interface": {"name": "FortyGigE1/0/1"}
    }
})
```

### Console and Specialized Cables
```python
from netbox_dio import DiodeCable

# RJ45 serial console
serial_console = DiodeCable.from_dict({
    "type": "rj45",
    "status": "connected",
    "a_termination": {
        "device": "router-01",
        "interface": {"name": "Consoleport0/0/0"}
    },
    "b_termination": {
        "device": "console-server",
        "interface": {"name": "GigabitEthernet0/1"}
    },
    "description": "Out-of-band management console connection"
})

# SFP direct attach cable (DAC)
dac_cable = DiodeCable.from_dict({
    "type": "dac",
    "status": "connected",
    "label": "Switch Stack DAC",
    "a_termination": {
        "device": "stack-member-1",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    },
    "b_termination": {
        "device": "stack-member-2",
        "interface": {"name": "TenGigabitEthernet1/0/1"}
    }
})
```

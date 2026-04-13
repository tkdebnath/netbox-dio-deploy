# DiodeRack

Represents a physical rack or cabinet in NetBox for organizing devices.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Rack with Location](#rack-with-location)
- [Rack with Device Positions](#rack-with-device-positions)
- [Rack Inside Device](#rack-inside-device)
- [Rack Attributes](#rack-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeRack, RackType, RackWidth

# Minimal rack - requires name and site
rack = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "dc-east"
})

# Complete rack with details
rack = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "dc-east",
    "location": "building-a",
    "rack": "Row A, Rack 01",
    "width": RackWidth.standard_19,
    "u_height": 42.0,
    "type": RackType.cabinet,
    "serial": "R001",
    "asset_tag": "RACK-001",
    "status": "active",
    "role": "primary",
    "comment": "Primary rack for building A"
})
```

---

## Rack with Location

```python
from netbox_dio import DiodeRack

# Rack in specific location within site
racks_with_location = [
    {
        "name": "rack-building-a",
        "site": "dc-east",
        "location": "building-a",
        "rack": "Main Data Center - Building A",
        "u_height": 42.0,
        "type": "cabinet"
    },
    {
        "name": "rack-building-b",
        "site": "dc-east",
        "location": "building-b",
        "rack": "Secondary Building - Building B",
        "u_height": 42.0,
        "type": "cabinet"
    },
    {
        "name": "rack-closet-1f",
        "site": "dc-west",
        "location": "first-floor-closet",
        "rack": "Network Closet 1F",
        "u_height": 24.0,
        "type": "wallmount"
    },
    {
        "name": "rack-closet-2f",
        "site": "dc-west",
        "location": "second-floor-closet",
        "rack": "Network Closet 2F",
        "u_height": 24.0,
        "type": "wallmount"
    }
]
```

---

## Rack with Device Positions

```python
from netbox_dio import DiodeRack

# Rack with device positions array (multiple devices in rack)
rack_with_positions = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "device_positions": [
        {"device": "core-switch", "position": 1.0},
        {"device": "core-switch", "position": 2.0},
        {"device": "dist-switch-01", "position": 5.0},
        {"device": "dist-switch-02", "position": 7.0},
        {"device": "patch-panel-top", "position": 10.0},
        {"device": "patch-panel-bottom", "position": 12.0},
        {"device": "pdus", "position": 15.0},
        {"device": "pdu-2", "position": 16.0},
    ]
})

# Switch as chassis
rack_chassis = DiodeRack.from_dict({
    "name": "rack-chassis",
    "site": "dc-central",
    "location": "main-data-center",
    "u_height": 42.0,
    "device_positions": [
        {"device": "c9500-chassis", "position": 5.0},
        {"device": "c9500-chassis", "position": 6.0},
        {"device": "c9500-chassis", "position": 7.0},
    ]
})
```

---

## Rack Inside Device

```python
from netbox_dio import DiodeDevice, DiodeRack

# Device with rack reference
device_with_rack = DiodeDevice.from_dict({
    "name": "access-switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access-switch",
    "rack": "rack-01",
    "position": 10.0,
    "location": "building-a"
})

# Rack positioned within site
rack_in_site = Rack(
    name="rack-01",
    site="dc-east",
    location="building-a",
    u_height=42.0,
    device_positions=[
        {"device": "core-switch", "position": 5.0},
        {"device": "patch-panel", "position": 1.0}
    ]
)
```

---

## Rack Attributes

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Rack name (unique within site) |
| `site` | str | Site where rack is located |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `rack` | str | Rack identifier/label (e.g., "Row A, Rack 01") |
| `location` | str | Location within site |
| `facility_id` | str | Facility identifier |
| `width` | str | Rack width in U |
| `u_height` | float | Height in rack units |
| `tyner` | str | Rack type |
| `serial` | str | Rack serial number |
| `asset_tag` | str | Asset tracking tag |
| `status` | str | Rack status (available, employed, planned, rejected) |
| `role` | str | Rack role (edge, core, distribution, accessory) |
| `descr` | str | Rack description |
| `comments` | str | Rack comments |
| `tags` | list[str] | Rack tags |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Additional metadata |
| `owner` | str | Owner reference |
| `device_positions` | list[dict] | Device positions in rack |

### `device_positions` Field

| Field | Type | Description |
|-------|------|-------------|
| `device` | str | Device name |
| `position` | float | U position (can be decimal) |
| `absorption` | float | Rack absorption value |
| `weight` | float | Device weight |
| `weight_unit` | str | Weight unit (kg, lb) |

---

## Valid Rack Properties

### Rack Type Values

```python
from netbox_dio import RackType

rack_types = [
    RackType.cabinet,      # Full-height cabinet
    RackType.ensuite,      # Enclosed suite
    RackType.confirm,      # Confirmed cabinet
    RackType.open_frame,   # Open frame
    RackType.wallmount,    # Wall-mounted
    RackType.other         # Other/unspecified
]

# Examples
cabinet_rack = DiodeRack.from_dict({
    "name": "cabinet-01",
    "site": "dc-east",
    "type": RackType.cabinet,
    "u_height": 42.0
})

wallmount_rack = DiodeRack.from_dict({
    "name": "wallmount-closet",
    "site": "dc-west",
    "type": RackType.wallmount,
    "u_height": 12.0
})
```

### Rack Width Values

```python
from netbox_dio import RackWidth

rack_widths = [
    RackWidth.standard_19,  # Standard 19-inch rack
    RackWidth.standard_23,  # Standard 23-inch rack
    RackWidth.ood_23,       # Out of data 23-inch rack
]

# Examples
standard_19 = DiodeRack.from_dict({
    "name": "rack-standard",
    "site": "dc-east",
    "width": RackWidth.standard_19,
    "u_height": 42.0
})
```

### Rack Status Values

| Status | Description |
|--------|-------------|
| "available" | Rack is available for use |
| "employed" | Rack is fully populated |
| "planned" | Rack is planned but not installed |
| "rejected" | Rack was rejected by user |

```python
from netbox_dio import DiodeRack

available = DiodeRack.from_dict({
    "name": "rack-available",
    "site": "dc-east",
    "status": "available"
})

employed = DiodeRack.from_dict({
    "name": "rack-occupied",
    "site": "dc-east",
    "status": "employed",
    "device_positions": [
        {"device": "switch-01", "position": 1.0},
        {"device": "switch-02", "position": 2.0}
    ]
})

planned = DiodeRack.from_dict({
    "name": "rack-planned",
    "site": "dc-east",
    "status": "planned",
    "description": "New rack for expansion"
})

rejected = DiodeRack.from_dict({
    "name": "rack-rejected",
    "site": "dc-east",
    "status": "rejected",
    "description": "Damaged during shipment"
})
```

### Rack Role Values

| Role | Description |
|------|-------------|
| "edge" | Edge rack (access/distribution) |
| "core" | Core rack (core switches/routers) |
| "distribution" | Distribution rack |
| "access" | Access rack |
| "mixed" | Mixed use |

```python
from netbox_dio import DiodeRack

core_rack = DiodeRack.from_dict({
    "name": "core-rack",
    "site": "dc-central",
    "role": "core",
    "type": RackType.cabinet,
    "u_height": 42.0
})

access_rack = DiodeRack.from_dict({
    "name": "access-rack-a",
    "site": "dc-east",
    "role": "edge",
    "type": RackType.cabinet,
    "u_height": 42.0
})
```

---

## Rack Height Examples

```python
from netbox_dio import DiodeRack

# Standard 42U cabinet
standard_42u = DiodeRack.from_dict({
    "name": "main-rack",
    "site": "dc-east",
    "u_height": 42.0,
    "type": "cabinet",
    "width": 19
})

# 24U rack
small_24u = DiodeRack.from_dict({
    "name": "closet-rack",
    "site": "dc-west",
    "u_height": 24.0,
    "type": "cabinet",
    "width": 19
})

# 12U wallmount wall
wallmount_12u = DiodeRack.from_dict({
    "name": "wallrack-closet",
    "site": "dc-west",
    "u_height": 12.0,
    "type": "wallmount",
    "width": 19
})

# 8U wallmount for small devices
wallmount_8u = DiodeRack.from_dict({
    "name": "wallmount-terial",
    "site": "dc-west",
    "u_height": 8.0,
    "type": "wallmount",
    "width": 19
})
```

---

## Rack Position Management

```python
from netbox_dio import DiodeRack

# Rack with detailed device positioning
detailed_positions = DiodeRack.from_dict({
    "name": "dense-rack",
    "site": "dc-central",
    "location": "main-data-center",
    "rack": "Main Data Center Row A",
    "u_height": 42.0,
    "device_positions": [
        {"device": "core-switch-01", "position": 1.0},
        {"device": "core-switch-01", "position": 2.0},
        {"device": "core-switch-02", "position": 3.0},
        {"device": "core-switch-02", "position": 4.0},
        {"device": "dist-switch-01", "position": 5.0},
        {"device": "dist-switch-01", "position": 7.0},
        {"device": "patch-panel-01", "position": 8.0},
        {"device": "patch-panel-02", "position": 10.0},
        {"device": "pdu-01", "position": 12.0},
        {"device": "pdu-02", "position": 14.0},
        {"device": "storage-01", "position": 15.0},
    ]
})

# Rack with fractional positions
fractional_positions = DiodeRack.from_dict({
    "name": "configuration-rack",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 48.0,
    "device_positions": [
        {"device": "top-equipment", "position": 48.0},
        {"device": "mid-equipment", "position": 24.0},
        {"device": "bottom-equipment", "position": 1.0}
    ]
})
```

---

## Site and Location Inheritance

```python
from netbox_dio import DiodeRack

# Rack inherits site from context
rack = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "site-a",  # Site where rack is located
    "device_positions": [
        # Each device position inherits site from rack
        {"device": "device-01", "position": 1.0}
    ]
})

# Rack with location
rack_with_location = DiodeRack.from_dict({
    "name": "rack-02",
    "site": "site-a",
    "location": "building-a-floor-2",
    "device_positions": [
        {"device": "switch-02", "position": 5.0}
    ]
})
```

---

## Rack with Cabling

```python
from netbox_dio import DiodeRack, DiodeCable

# Rack with cable terminations
rack_with_cables = DiodeRack.from_dict({
    "name": "core-rack",
    "site": "dc-central",
    "location": "main-data-center",
    "u_height": 42.0,
    "device_positions": [
        {"device": "cx-core-01", "position": 1.0},
        {"device": "cx-core-02", "position": 3.0}
    ]
})

# Cable connections between racks
inter_rack_cable = DiodeCable.from_dict({
    "type": "fiber-singlemode",
    "status": "connected",
    "a_termination": {
        "device": "cx-core-01",
        "interface": {"name": "TenGig1/0/1"}
    },
    "b_termination": {
        "device": "cx-core-02",
        "interface": {"name": "TenGig1/0/1"}
    },
    "length": 1.0, "length_unit": "m",
    "description": "Stack cable between core racks"
})
```

---

## Common Rack Scenarios

### Edge Building Rack
```python
from netbox_dio import DiodeRack

building_rack = DiodeRack.from_dict({
    "name": "building-a-rack",
    "site": "site-east",
    "location": "building-a-1st-floor",
    "rack": "Main Equipment Cabinet",
    "u_height": 42.0,
    "type": "cabinet",
    "status": "employed",
    "role": "edge",
    "device_positions": [
        {"device": "edge-switch-01", "position": 5.0},
        {"device": "edge-switch-02", "position": 7.0},
        {"device": "patch-panel-top", "position": 2.0},
        {"device": "patch-panel-bottom", "position": 3.0},
        {"device": "pdu-01", "position": 38.0},
        {"device": "pdu-02", "position": 39.0},
    ],
    "tags": ["edge", "building-a"]
})
```

### Outdated Storage Rack Replacement
```python
from netbox_dio import DiodeRack

building_b_rack = DiodeRack.from_dict({
    "name": "building-b-rack",
    "site": "site-east",
    "location": "building-b",
    "u_height": 24.0,
    "type": "cabinet",
    "status": "planned",
    "role": "access",
    "description": "To be replaced with 42U rack in 2026"
})
```

### Storage Rack for Legacy Equipment
```python
from netbox_dio import DiodeRack

# Rack for older hardware
legacy_rack = DiodeRack.from_dict({
    "name": "legacy-server-rack",
    "site": "site-central",
    "location": "data-center-b",
    "u_height": 48.0,
    "type": "cabinet",
    "status": "employed",
    "role": "mixed",
    "description": "Legacy equipment rack - under review for decommission",
    "facility_id": "FT-001"
})
```

---

## Rack Properties Reference

### Rack Width Values

```python
# Standatd 19-inch
width_19 = "19"

# Standard 23-inch
width_23 = "23"

# Out of D23-inch (for LCD/monitor mounts)
width_ood_23 = "out23"

(rack width in rack units)
```

### Rack Type Class Constants

```python
from netbox_dio import RackType

print(RackType.cabinet)    # "cabinet"
print(RackType.ensuite)    # "enclosed"
print(RackType.ood)        # "open"
print(RackType.frame)      # "frame"
print(RackType.wallmount)  # "wallmount"
print(RackType.other)      # "other"
```

### Rack Serialization

```python
from netbox_dio import DiodeRack
from netboxlabs.diode.sdk.ingester import Rack

rack = DiodeRack.from_dict({
    "name": "rack-01",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "width": 19,
    "status": "employed",
    "role": "distribution",
    "device_positions": [
        {"device": "switch-01", "position": 5.0},
        {"device": "switch-02", "position": 7.0}
    ]
})

# Convert to protobuf
proto_rack = rack.to_protobuf()
print(proto_rack)

# Output:
# Rack(
#   name="rack-01",
#   facility_id="",
#   asset_tag=None,
#   site="dc-east",
#   location="building-a",
#   rack="rack-01",
#   width=19,
#   u_height=42.0,
#   type="cabinet",
#   status="employed",
#   role="distribution",
#   device_positions=[
#     {"device": "switch-01", "position": 5.0},
#     {"device": "switch-02", "position": 7.0}
#   ]
# )
```

---

## Rack Templates and Custom Fields

```python
from netbox_dio import DiodeRack

# Rack with custom fields
custom_rack = DiodeRack.from_dict({
    "name": "custom-rack-01",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "custom_fields": {
        "date_installed": "2024-01-15",
        "maintenance_contact": "IT-Operations",
        "recovery_point": "2025-12-31",
        "vendor": ""
    }
})

# Rack with prefetch settings
preflight_rack = DiodeRack.from_dict({
    "name": "preflight-rack",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "status": "planned",
    "description": "Rack to be installed in Q2 2026"
})
```

---

## Rack Device Position Helpers

```python
from netbox_dio import DiodeRack

# Rack with empty device_positions (placeholder)
placeholder_rack = DiodeRack.from_dict({
    "name": "new-rack-placeholder",
    "site": "dc-east",
    "location": "building-a",
    "u_height": 42.0,
    "status": "planned",
    "device_positions": []
})

# Rack with per-device position tracking
tracked_rack = DiodeRack.from_dict({
    "name": "tracked-rack-a",
    "site": "dc-central",
    "u_height": 42.0,
    "device_positions": [
        {"device": "core-01", "position": 1.0, "weight": 15.5, "weight_unit": "kg"},
        {"device": "core-02", "position": 3.0, "weight": 15.5, "weight_unit": "kg"},
        {"device": "dist-01", "position": 5.0, "weight": 8.2, "weight_unit": "kg"},
    ]
})
```

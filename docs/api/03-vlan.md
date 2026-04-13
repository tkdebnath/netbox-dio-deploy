# DiodeVLAN

Represents a VLAN configuration in NetBox.

## Table of Contents
- [Basic Usage](#basic-usage)
- [VLAN in Site Context](#vlan-in-site-context)
- [VLAN with Role and Status](#vlan-with-role-and-status)
- [VLAN in Device Context](#vlan-in-device-context)
- [Native VLAN on Trunk](#native-vlan-on-trunk)
- [Q-in-Q VLAN](#q-in-q-vlan)
- [VLAN Attributes](#vlan-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeVLAN, VLANStatus, VLANRole, VLANGroup

# Minimal VLAN - requires name, vid, and site
vlan = DiodeVLAN.from_dict({
    "name": "VLAN100",
    "vid": 100,
    "site": "dc-east"
})

# Complete VLAN with all common fields
vlan = DiodeVLAN.from_dict({
    "name": "VLAN200",
    "vid": 200,
    "site": "dc-east",
    "description": "Data VLAN for floor 2",
    "status": VLANStatus.ACTIVE,
    "role": VLANRole.ACCESS,
    "tags": ["production", "floor2"]
})
```

---

## VLAN in Site Context

```python
from netbox_dio import DiodeVLAN

# VLAN scoped to a site
data_vlan = DiodeVLAN.from_dict({
    "name": "DATA",
    "vid": 1000,
    "site": "dc-east",
    "description": "Data VLAN",
    "status": "active",
    "role": "access"
})

# VLAN in different site with same VID
data_vlan_copy = DiodeVLAN.from_dict({
    "name": "DATA-WEST",
    "vid": 1000,  # Same VID, different site
    "site": "dc-west",
    "description": "Data VLAN - West coast"
})
```

---

## VLAN with Role and Status

```python
from netbox_dio import DiodeVLAN, VLANStatus, VLANRole

# Core aggregation VLAN
core_vlan = DiodeVLAN.from_dict({
    "name": "CORE-100",
    "vid": 100,
    "site": "dc-central",
    "status": VLANStatus.ACTIVE,
    "role": VLANRole.CORE,
    "description": "Core network VLAN"
})

# Reserve VLAN for special use
reserved_vlan = DiodeVLAN.from_dict({
    "name": "RESERVED-10",
    "vid": 10,
    "site": "dc-central",
    "status": VLANStatus.RESERVED,
    "role": VLANRole.OTHER,
    "description": "Reserved for future use"
})

# Deprecated VLAN
deprecated_vlan = DiodeVLAN.from_dict({
    "name": "OLD-VLAN",
    "vid": 999,
    "site": "dc-central",
    "status": VLANStatus.DEPRECATED,
    "role": VLANRole.OTHER,
    "description": "Migrate to new VLAN"
})
```

---

## VLAN in Device Context

```python
from netbox_dio import DiodeDevice, DiodeVLAN

device = DiodeDevice.from_dict({
    "name": "access-switch",
    "site": "dc-east",
    "device_type": "cisco-c2960",
    "role": "access-switch",
    "interfaces": [
        # Single VLAN access port
        {
            "name": "GigabitEthernet1/0/1",
            "type": "physical",
            "enabled": True,
            "mode": "access",
            "untagged_vlan": "VLAN10"
        },
        # Trunk port with native VLAN
        {
            "name": "GigabitEthernet1/0/24",
            "type": "physical",
            "enabled": True,
            "mode": "trunk",
            "untagged_vlan": "VLAN99",  # Native VLAN
            "vlans": [10, 20, 30]
        }
    ],
    "vlans": [
        {"name": "VLAN10", "vid": 10, "site": "dc-east", "description": "Users"},
        {"name": "VLAN99", "vid": 99, "site": "dc-east", "description": "Native/trunk"}
    ]
})
```

---

## Native VLAN on Trunk

```python
from netbox_dio import DiodeDevice

# Access switch with native VLAN configuration
switch = DiodeDevice.from_dict({
    "name": "access-switch-01",
    "site": "dc-east",
    "device_type": "cisco-c2960",
    "role": "access-switch",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/24",  # Uplink port
            "type": "physical",
            "enabled": True,
            "mode": "trunk",
            "untagged_vlan": "VLAN99",  # Native/management VLAN
            "description": "Uplink to distribution"
        }
    ],
    "vlans": [
        {
            "name": "VLAN99",
            "vid": 99,
            "site": "dc-east",
            "status": "active",
            "role": "management",
            "description": "Native VLAN for trunks"
        }
    ]
})
```

---

## Q-in-Q VLAN

```python
from netbox_dio import DiodeInterface, DiodeVLAN

# Interface with Q-in-Q configuration
qinq_interface = DiodeInterface.from_dict({
    "name": "GigabitEthernet0/0/1",
    "device": "service-provider-edge",
    "type": "physical",
    "qinq_svlan": "SVLAN100",  # Service provider outer VLAN
    "untagged_vlan": "VLAN101",
    "description": "Q-in-Q customer edge"
})

# Customer VLAN
customer_vlan = DiodeVLAN.from_dict({
    "name": "CUST-VLAN100",
    "vid": 100,
    "site": "dc-edge",
    "qinq_svlan": 10,  # Outer SVLAN
    "description": "Customer 100"
})
```

---

## VLANGroups

```python
from netbox_dio import DiodeVLAN, VLANGroup

# VLAN with group assignment
group_vlan = DiodeVLAN.from_dict({
    "name": "BUILDING-A",
    "vid": 1000,
    "site": "dc-east",
    "group": "BUILDING-A-VLANs",
    "description": "VLAN in Building A group"
})
```

---

## Create Multiple VLANs for Device

```python
from netbox_dio import DiodeDevice, DiodeVLAN, VLANStatus, VLANRole

switch = DiodeDevice.from_dict({
    "name": "distribution-switch",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "distribution",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "type": "physical",
            "enabled": True,
            "mode": "trunk",
            "untagged_vlan": "VLAN100",
            "vlans": [10, 20, 30, 40, 100]
        }
    ],
    "vlans": [
        # User VLANs
        {"name": "VLAN10", "vid": 10, "site": "dc-east", "role": VLANRole.ACCESS, "status": VLANStatus.ACTIVE, "description": "User VLAN A"},
        {"name": "VLAN20", "vid": 20, "site": "dc-east", "role": VLANRole.ACCESS, "status": VLANStatus.ACTIVE, "description": "User VLAN B"},
        {"name": "VLAN30", "vid": 30, "site": "dc-east", "role": VLANRole.ACCESS, "status": VLANStatus.ACTIVE, "description": "User VLAN C"},
        {"name": "VLAN40", "vid": 40, "site": "dc-east", "role": VLANRole.ACCESS, "status": VLANStatus.ACTIVE, "description": "User VLAN D"},
        # Management VLAN
        {"name": "VLAN100", "vid": 100, "site": "dc-east", "role": VLANRole.MANAGEMENT, "status": VLANStatus.ACTIVE, "description": "Management VLAN"},
    ]
})
```

---

## VLAN Attributes

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | str | VLAN name |
| `vid` | int | VLAN ID (1-4094) |
| `site` | str | Site where VLAN is defined |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `vid` | int | VLAN ID (1-4094) |
| `site` | str | Site where VLAN is defined |
| `vid` | int | VLAN ID (1-4094) |
| `description` | str | VLAN description |
| `status` | str | VLAN status (active, reserved, deprecated) |
| `role` | str | VLAN role (access, distribution, core, management, other) |
| `group` | str | VLAN group name |
| `tenant` | str | Tenant owning the VLAN |
| `qinq_role` | str | Q-in-Q role |
| `qinq_svlan` | int | Q-in-Q outer VLAN ID |
| `comments` | str | VLAN comments |
| `tags` | list[str] | VLAN tags |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Additional metadata |
| `owner` | str | Owner reference |

### Valid Values

**Status:**
- `active` - VLAN is active
- `reserved` - VLAN is reserved
- `deprecated` - VLAN is deprecated

**Role:**
- `access` - Access VLAN
- `distribution` - Distribution VLAN
- `core` - Core network VLAN
- `management` - Management VLAN
- `voice` - Voice VLAN
- `data` - Data VLAN
- `other` - Other role

### VID (VLAN ID) Rules

| VID Range | Purpose |
|-----------|---------|
| 1 | Default VLAN (cannot be deleted or modified) |
| 2-1001 | Normal range VLANs |
| 1002-1005 | Reserved for legacy protocols |
| 1006-4094 | Extended range VLANs |

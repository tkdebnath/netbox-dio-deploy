# DiodeInterface

Represents a network interface on a device.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Interface Types](#interface-types)
- [Trunk Interface](#trunk-interface)
- [Access Interface](#access-interface)
- [Virtual Interface](#virtual-interface)
- [Wireless Interface](#wireless-interface)
- [LAG Interface](#lag-interface)
- [Interface Attributes](#interface-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeInterface, InterfaceType, InterfaceMode

# Simple physical interface
interface = DiodeInterface(
    name="GigabitEthernet1/0/1",
    device="switch-01",
    type="physical",
    enabled=True,
    description="Uplink connection"
)

# Create from dictionary
interface = DiodeInterface.from_dict({
    "name": "GigabitEthernet1/0/1",
    "device": "switch-01",
    "type": "physical",
    "enabled": True
})
```

---

## Interface Types

### Recommended Types

```python
from netbox_dio import InterfaceType

# All available interface types
interface_types = [
    InterfaceType.PHYSICAL,   # Physical port
    InterfaceType.VIRTUAL,    # Virtual interface (loopback, vlan)
    InterfaceType.LAG,        # Link Aggregation Group
    InterfaceType.WIRELESS,   # Wireless interface
    InterfaceType.OTHER     # Other/unspecified
]
```

### Type Cautions - avoid using "physical"

```python
# Recommended - use lowercase enum or SDK-compliant values
interface = DiodeInterface(
    name="GigabitEthernet1/0/1",
    device="switch-01",
    type=InterfaceType.PHYSICAL,  # Preferred
    enabled=True
)

# Also works - lowercase string
interface = DiodeInterface(
    name="GigabitEthernet1/0/1",
    device="switch-01",
    type="physical",  # Fallback - use enum preferred
    enabled=True
)
```

---

## Trunk Interface

```python
from netbox_dio import DiodeInterface, InterfaceMode

# Trunk interface carrying multiple VLANs
trunk = DiodeInterface.from_dict({
    "name": "GigabitEthernet1/0/24",
    "device": "switch-01",
    "type": "physical",
    "enabled": True,
    "mode": "trunk",
    "description": "Uplink to distribution switch",
    "vlans": [100, 200, 300]
})
```

---

## Access Interface

```python
from netbox_dio import DiodeInterface, InterfaceMode

# Access interface - single VLAN
access = DiodeInterface.from_dict({
    "name": "GigabitEthernet1/0/1",
    "device": "switch-01",
    "type": "physical",
    "enabled": True,
    "mode": "access",
    "untagged_vlan": "VLAN100",  # Native VLAN
    "description": "User PC connection"
})
```

---

## Virtual Interface

```python
from netbox_dio import DiodeInterface

# Loopback interface (commonly used for management/IP)
loopback = DiodeInterface.from_dict({
    "name": "Loopback0",
    "device": "router-01",
    "type": "virtual",
    "enabled": True,
    "description": "Loopback interface for router"
})

# VLAN interface (SVI)
vlan_interface = DiodeInterface.from_dict({
    "name": "Vlan100",
    "device": "switch-01",
    "type": "virtual",
    "enabled": True,
    "description": "SVI for VLAN 100"
})
```

---

## Wireless Interface

```python
from netbox_dio import DiodeInterface

# Wireless interface with radio parameters
wireless = DiodeInterface.from_dict({
    "name": "Wlan0",
    "device": "ap-01",
    "type": "wireless",
    "enabled": True,
    "rf_role": "client",
    "rf_channel": "36",
    "rf_channel_frequency": 5180,
    "rf_channel_width": 20,
    "tx_power": 20,
    "description": "Wireless LAN interface"
})
```

---

## LAG (Link Aggregation Group) Interface

```python
from netbox_dio import DiodeInterface

# LAG interface - bond multiple physical interfaces
lag = DiodeInterface.from_dict({
    "name": "Port-Channel1",
    "device": "switch-01",
    "type": "lag",
    "enabled": True,
    "description": "LACP bundle to upstream",
    "lag": "members-bundle"
})
```

---

## Complete Device with Multiple Interfaces

```python
from netbox_dio import DiodeDevice, convert_device_to_entities

device = DiodeDevice.from_dict({
    "name": "distribution-switch",
    "site": "dc-east",
    "device_type": "cisco-c9300",
    "role": "distribution",
    "interfaces": [
        # Uplink - trunk mode
        {
            "name": "GigabitEthernet1/0/1",
            "device": "distribution-switch",
            "type": "physical",
            "enabled": True,
            "speed": 1000,
            "duplex": "full",
            "mode": "trunk",
            "vlans": [10, 20, 30, 100, 200],
            "description": "Core uplink"
        },
        # Backup uplink
        {
            "name": "GigabitEthernet1/0/2",
            "device": "distribution-switch",
            "type": "physical",
            "enabled": True,
            "speed": 1000,
            "mode": "access",
            "untagged_vlan": "VLAN100",
            "description": "Management backup"
        },
        # Access port - single VLAN
        {
            "name": "GigabitEthernet1/0/24",
            "device": "distribution-switch",
            "type": "physical",
            "enabled": True,
            "speed": 100,
            "mode": "access",
            "untagged_vlan": "VLAN20",
            "description": "Access switch connection"
        },
        # Loopback
        {
            "name": "Loopback0",
            "device": "distribution-switch",
            "type": "virtual",
            "enabled": True,
            "description": "Management loopback"
        }
    ]
})

# Convert - should produce entities
entities = convert_device_to_entities(device)
print(f"Created {len(entities)} entities")
# Output: Created 5 entities (1 device + 4 interfaces)
```

---

## Interface Attributes

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Interface name (e.g., "GigabitEthernet1/0/1") |
| `device` | str | Parent device name |
| `type` | str | Interface type (physical, virtual, lag, wireless, other) |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `label` | str | Interface label |
| `enabled` | bool | Is interface enabled |
| `parent` | str | Parent interface name |
| `bridge` | str | Bridge interface name |
| `lag` | str | LAG interface name |
| `mtu` | int | Maximum transmission unit |
| `primary_mac_address` | str | Primary MAC address |
| `speed` | int | Speed in Mbps |
| `duplex` | str | Duplex mode (auto, full, half) |
| `wwn` | str | World Wide Name (Fibre Channel) |
| `mgmt_only` | bool | Management-only interface |
| `description` | str | Interface description |
| `mode` | str | Mode (access, trunk, bridge, virtual) |
| `rf_role` | str | RF role (wireless) |
| `rf_channel` | str | RF channel (wireless) |
| `poe_mode` | str | PoE mode |
| `poe_type` | str | PoE type |
| `untagged_vlan` | str | Native VLAN name |
| `qinq_svlan` | str | Q-in-Q SVLAN |
| `vlan_translation_policy` | str | VLAN translation policy |
| `mark_connected` | bool | Mark as connected |
| `vrf` | str | VRF name |
| `tags` | list[str] | Interface tags |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Metadata |
| `owner` | str | Owner |
| `wireless_lans` | list[str] | Wireless LAN names (for wireless interfaces) |
| `vdcs` | list[str] | Virtual Device Context names |

### Valid Enum Values

**Type:**
- `physical` - Physical port (Ethernet, SFP)
- `virtual` - Virtual interface (Loopback, VLAN)
- `lag` - Link Aggregation Group (Port-Channel)
- `wireless` - Wireless interface (WLAN)
- `other` - Other/unspecified

**Mode:**
- `access` - Access port (single VLAN)
- `trunk` - Trunk port (multiple VLANs)
- `bridge` - Bridged port
- `virtual` - Virtual port

**Duplex:**
- `auto` - Auto-negotiate duplex
- `full` - Full duplex
- `half` - Half duplex

**Status:**
- `active` - Up and operational
- `down` - Administratively down
- `testing` - In testing mode
- `unknown` - Status unknown
- `dormant` - Waiting for external event
- `not-present` - Module absent
- `lower-layer-down` - Lower layer down

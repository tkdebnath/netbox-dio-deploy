# DiodeIPAddress

Represents an IP address assigned to an interface or device in NetBox.

## Table of Contents
- [Basic Usage](#basic-usage)
- [IP Address on Loopback Interface](#ip-address-on-loopback-interface)
- [IP Address on Physical Interface](#ip-address-on-physical-interface)
- [IP Address on VLAN Interface](#ip-address-on-vlan-interface)
- [IPv6 Address Configuration](#ipv6-address-configuration)
- [Multiple IPs on Device](#multiple-ips-on-device)
- [IP Address Attributes](#ip-address-attributes)

---

## Basic Usage

```python
from netbox_dio import DiodeIPAddress

# Minimal IP - requires address and assigned interface
ip = DiodeIPAddress.from_dict({
    "address": "10.0.0.1/32",
    "assigned_object_interface": "Loopback0"
})

# Complete IP address configuration
ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "role": "primary",
    "description": "Main VLAN interface",
    "assigned_object_interface": "Vlan100"
})
```

---

## IP Address on Loopback Interface

Loopback interfaces are virtual interfaces commonly used for management IPs:

```python
from netbox_dio import DiodeIPAddress

# Management IP on loopback
router_ip = DiodeIPAddress.from_dict({
    "address": "10.0.0.1/32",
    "status": "active",
    "role": "secondary",
    "dns_name": "router01.example.com",
    "assigned_object_interface": "Loopback0"
})

# Dual loopback IPs
loopback_ips = [
    {
        "address": "10.0.0.1/32",
        "status": "active",
        "dns_name": "router01-primary.example.com",
        "assigned_object_interface": "Loopback0"
    },
    {
        "address": "10.0.0.2/32",
        "status": "active",
        "dns_name": "router01-backup.example.com",
        "assigned_object_interface": "Loopback1"
    }
]
```

---

## IP Address on Physical Interface

Physical interface IPs are typically used for point-to-point links:

```python
from netbox_dio import DiodeIPAddress

# Point-to-point link IP
wan_ip = DiodeIPAddress.from_dict({
    "address": "192.0.2.1/30",
    "status": "active",
    "role": "primary",
    "assigned_object_interface": "GigabitEthernet0/0/0"
})

# Another P2P link
lan_ip = DiodeIPAddress.from_dict({
    "address": "10.10.10.0/30",
    "status": "active",
    "assigned_object_interface": "GigabitEthernet0/0/1"
})
```

---

## IP Address on VLAN Interface

SVI (Switched Virtual Interface) IPs are management IP for VLANs:

```python
from netbox_dio import DiodeIPAddress

# Layer 3 SVI IP
vlan_svi_ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "role": "primary",
    "description": "Default gateway for VLAN 100",
    "assigned_object_interface": "Vlan100"
})

# Voice VLAN SVI
voice_svi_ip = DiodeIPAddress.from_dict({
    "address": "172.16.100.1/24",
    "status": "active",
    "role": "secondary",
    "description": "Voice VLAN gateway",
    "assigned_object_interface": "Vlan200"
})
```

---

## IPv6 Address Configuration

```python
from netbox_dio import DiodeIPAddress

# IPv6 loopback address
ipv6_loopback = DiodeIPAddress.from_dict({
    "address": "2001:db8::1/128",
    "status": "active",
    "description": "Management IPv6 address",
    "assigned_object_interface": "Loopback0"
})

# IPv6 on link
ipv6_link = DiodeIPAddress.from_dict({
    "address": "2001:db8:1000::1/64",
    "status": "active",
    "role": "primary",
    "dns_name": "router-ipv6.example.com",
    "assigned_object_interface": "GigabitEthernet0/0/0"
})

# Dual-stack configuration
dual_stack_v6 = DiodeIPAddress.from_dict({
    "address": "fd00::1/64",
    "status": "active",
    "role": "secondary",
    "assigned_object_interface": "Vlan100",
    "description": "Internal IPv6 subnet"
})
```

---

## VRF (Virtual Routing and Forwarding)

```python
from netbox_dio import DiodeIPAddress

# IP address in separate VRF
vpn_ip = DiodeIPAddress.from_dict({
    "address": "10.100.50.1/24",
    "status": "active",
    "vrf": "customer-vpn",
    "description": "Customer VPN gateway",
    "assigned_object_interface": "GigabitEthernet0/1/0"
})

# Management VRF
mgmt_vrf_ip = DiodeIPAddress.from_dict({
    "address": "172.16.0.1/24",
    "status": "active",
    "vrf": "management",
    "assigned_object_interface": "Loopback0",
    "description": "Management VRF loopback"
})
```

---

## IP Addresses Inside Device

```python
from netbox_dio import DiodeDevice

# Router with multiple IP addresses
router = DiodeDevice.from_dict({
    "name": "edge-router",
    "site": "dc-east",
    "device_type": "cisco-asr1001",
    "role": "edge",
    "interfaces": [
        {"name": "GigabitEthernet0/0/0", "type": "physical"},
        {"name": "GigabitEthernet0/0/1", "type": "physical"},
        {"name": "Loopback0", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.0.0.1/30",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet0/0/0",
            "vrf": "main"
        },
        {
            "address": "10.0.0.5/30",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet0/0/1",
            "vrf": "main"
        },
        {
            "address": "10.0.0.100/32",
            "status": "active",
            "dns_name": "router-mgmt.example.com",
            "assigned_object_interface": "Loopback0",
            "vrf": "management"
        }
    ]
})
```

---

## IP Address Attributes

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `address` | str | IP address in CIDR notation (e.g., "192.168.1.1/24") |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | str | IP address status (active, reserved, dhcp, approved, deprecated) |
| `role` | str | IP address role (primary, secondary) |
| `dns_name` | str | DNS hostname for reverse DNS lookups |
| `description` | str | IP address description |
| `vrf` | str | VRF name if applicable |
| `assigned_object_interface` | str | Interface name this IP is assigned to |
| `assigned_object_device` | str | Device name (if no interface) |
| `tags` | list[str] | IP address tags |
| `custom_fields` | dict | Custom field values |
| `metadata` | dict | Additional metadata |
| `comments` | str | IP address comments |
| `assignments_object_type` | str | Type of assigned object |

---

## Valid Status Values

```python
from netbox_dio import DiodeIPAddress

status_options = ["active", "reserved", "dhcp", "approved", "deprecated"]

# Example status configurations
reserved_ip = DiodeIPAddress.from_dict({
    "address": "192.168.255.1/24",
    "status": "reserved",
    "description": "Reserved for future use"
})

dhcp_ip = DiodeIPAddress.from_dict({
    "address": "10.10.10.1/24",
    "status": "dhcp",
    "description": "DHCP scope address"
})

approved_ip = DiodeIPAddress.from_dict({
    "address": "10.20.30.1/24",
    "status": "approved",
    "description": "Pending deployment approval"
})

deprecated_ip = DiodeIPAddress.from_dict({
    "address": "172.16.0.1/16",
    "status": "deprecated",
    "description": "Logging out of network"
})
```

---

## Valid Roles

```python
# Primary role - main IP for device/interface
primary_ip = DiodeIPAddress.from_dict({
    "address": "10.0.0.1/32",
    "role": "primary",
    "status": "active",
    "assigned_object_interface": "Loopback0"
})

# Secondary role - backup or additional IP
secondary_ip = DiodeIPAddress.from_dict({
    "address": "10.0.1.1/32",
    "role": "secondary",
    "status": "active",
    "assigned_object_interface": "Loopback0"
})

# No role - single IP
single_ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "assigned_object_interface": "GigabitEthernet0/0/0"
})
```

---

## DNS Name Configuration

```python
from netbox_dio import DiodeIPAddress

# With DNS name for reverse lookup
dns_enabled_ip = DiodeIPAddress.from_dict({
    "address": "10.20.30.40/32",
    "status": "active",
    "dns_name": "server01.example.com",
    "assigned_object_interface": "Loopback0"
})

# With DNS name on IPv6
ipv6_dns_ip = DiodeIPAddress.from_dict({
    "address": "2001:db8:85a3::8a2e:370:7334/128",
    "status": "active",
    "dns_name": "ipv6-server.example.com",
    "assigned_object_interface": "Loopback1"
})

# No DNS - plain IP
plain_ip = DiodeIPAddress.from_dict({
    "address": "192.168.100.1/24",
    "status": "active",
    "assigned_object_interface": "Vlan100"
})
```

---

## Address Prefix Matching

IP addresses should match their expected prefix based on CIDR:

```python
from netbox_dio import DiodeIPAddress

# /32 - host address (loopback)
host_ip = DiodeIPAddress.from_dict({
    "address": "10.0.0.1/32",
    "status": "active",
    "assigned_object_interface": "Loopback0"
})

# /30 - point-to-point link
p2p_ip = DiodeIPAddress.from_dict({
    "address": "192.0.2.0/30",
    "status": "active",
    "assigned_object_interface": "GigabitEthernet0/0/0"
})

# /24 - LAN subnet gateway
lan_ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "assigned_object_interface": "Vlan100"
})

# /16 - large network
big_ip = DiodeIPAddress.from_dict({
    "address": "172.16.0.1/16",
    "status": "active",
    "assigned_object_interface": "Vlan1"
})

# /64 - IPv6 LAN
ipv6_lan = DiodeIPAddress.from_dict({
    "address": "2001:db8:1000::1/64",
    "status": "active",
    "assigned_object_interface": "Vlan200"
})
```

---

## Device Inheritance Patterns

### IP Address with Device Context

```python
from netbox_dio import DiodeDevice

device_with_ip = DiodeDevice.from_dict({
    "name": "mgmt-switch",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "management",
    "interfaces": [
        {"name": "Loopback0", "type": "virtual"},
        {"name": "Vlan100", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.100.1.10/32",
            "status": "active",
            "dns_name": "mgmt-switch.example.com",
            "assigned_object_interface": "Loopback0",
            "description": "Management IP"
        },
        {
            "address": "192.168.100.1/24",
            "status": "active",
            "assigned_object_interface": "Vlan100",
            "description": "VLAN 100 gateway"
        }
    ]
})
```

### Multi-Site Device Configuration

```python
from netbox_dio import DiodeDevice

# Examples where IP inherits site from device
site_a = DiodeDevice.from_dict({
    "name": "router-site-a",
    "site": "site-a",
    "location": "building-a",
    "device_type": "cisco-4331",
    "role": "edge",
    "interfaces": [
        {"name": "Loopback0", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.1.0.1/32",
            "status": "active",
            "vrf": "main",
            "assigned_object_interface": "Loopback0"
            # site automatically set to "site-a" through device
        }
    ]
})

site_b = DiodeDevice.from_dict({
    "name": "router-site-b",
    "site": "site-b",
    "location": "building-b",
    "device_type": "cisco-4331",
    "role": "edge",
    "interfaces": [
        {"name": "Loopback0", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.2.0.1/32",
            "status": "active",
            "vrf": "main",
            "assigned_object_interface": "Loopback0"
            # site automatically set to "site-b" through device
        }
    ]
})
```

---

## VRF and Site Inheritance

```python
from netbox_dio import DiodeIPAddress

# Explicit VRF configuration
vrf_ip = DiodeIPAddress.from_dict({
    "address": "10.10.10.1/24",
    "status": "active",
    "role": "primary",
    "vrf": "customer-vpn",
    "description": "Customer VPN gateway",
    "assigned_object_interface": "GigabitEthernet0/1/0"
})

# Management VRF
mgmt_ip = DiodeIPAddress.from_dict({
    "address": "172.16.0.1/24",
    "status": "active",
    "vrf": "management",
    "assigned_object_interface": "Loopback0"
})

# No VRF (default VRF)
default_ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "description": "Standard LAN gateway",
    "assigned_object_interface": "Vlan100"
})
```

---

## Common Configuration Patterns

### Hub-and-Spoke Router

```python
from netbox_dio import DiodeDevice, DiodeIPAddress

hub_router = DiodeDevice.from_dict({
    "name": "hub-router",
    "site": "dc-central",
    "device_type": "cisco-asr1002",
    "role": "hub-router",
    "interfaces": [
        {"name": "GigabitEthernet0/0/0", "type": "physical"},
        {"name": "GigabitEthernet0/0/1", "type": "physical"},
        {"name": "GigabitEthernet0/0/2", "type": "physical"},
        {"name": "Loopback0", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.0.0.2/30",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet0/0/0"
        },
        {
            "address": "10.0.0.6/30",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet0/0/1"
        },
        {
            "address": "10.0.0.10/30",
            "status": "active",
            "assigned_object_interface": "GigabitEthernet0/0/2"
        },
        {
            "address": "10.0.0.1/32",
            "status": "active",
            "dns_name": "hub-router.example.com",
            "assigned_object_interface": "Loopback0"
        }
    ]
})
```

### Management Network Setup

```python
from netbox_dio import DiodeDevice

mgmt_device = DiodeDevice.from_dict({
    "name": "access-switch",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access-switch",
    "interfaces": [
        {"name": "GigabitEthernet1/0/24", "type": "physical"},
        {"name": "Vlan99", "type": "virtual"}
    ],
    "ip_addresses": [
        {
            "address": "10.10.10.20/24",
            "status": "active",
            "dns_name": "switch-mgmt.example.com",
            "assigned_object_interface": "Vlan99",
            "vrf": "management"
        }
    ]
})
```

---

## Error Handling Examples

### Invalid IP Format
```python
# This will raise validation error
try:
    DiodeIPAddress.from_dict({
        "address": "invalid-ip",  # ERROR: not valid CIDR
        "status": "active"
    })
except ValidationError as e:
    print(f"Validation error: {e}")
    # Validation error: 1 validation error for DiodeIPAddress
    # address
    #   Invalid CIDR format: invalid-ip (line X)
```

### Missing Interface Association
```python
# IP address without assigned interface
# This is valid - IP can exist without interface assignment
standalone_ip = DiodeIPAddress.from_dict({
    "address": "10.20.30.40/24",
    "status": "active",
    "role": "reserved"
    # No assigned_object_interface - valid
})
```

### VRF Not Found
```python
from netbox_dio import DiodeIPAddress

# Assuming VRF doesn't exist in NetBox
ip_with_vrf = DiodeIPAddress.from_dict({
    "address": "10.100.50.1/24",
    "status": "active",
    "vrf": "nonexistent-vrf",  # This will cause 404 error at commit time
    "assigned_object_interface": "Loopback0"
})
```

---

## Serialization Test

```python
from netbox_dio import DiodeIPAddress
from netboxlabs.diode.sdk.ingester import IPAddress

# Create IP address
ip = DiodeIPAddress.from_dict({
    "address": "192.168.1.1/24",
    "status": "active",
    "role": "primary",
    "dns_name": "gateway.example.com",
    "description": "Default gateway for VLAN 100",
    "vrf": "main",
    "assigned_object_interface": "Vlan100"
})

# Convert to protobuf
proto_ip = ip.to_protobuf()
print(proto_ip)

# Output:
# IPAddress(
#   address="192.168.1.1/24",
#   status="active",
#   role="primary",
#   dns_name="gateway.example.com",
#   description="Default gateway for VLAN 100",
#   scope_site="site-name",
#   vrf="main",
#   assigned_object_type="dcim.interface",
#   parent="192.168.1.0/24"
# )
```

---

## Attributes Reference

### IPAddress Protobuf Fields

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | IP address with CIDR notation |
| `status` | string | IP address status |
| `role` | string | IP address role |
| `dns_name` | string | DNS hostname |
| `description` | string | Description text |
| `scope_site` | string | Site where IP is assigned |
| `vrf` | string | VRF name |
| `tags` | repeated string | IP address tags |
| `custom_fields` | map | Custom field key-value pairs |
| `metadata` | map | Additional metadata |
| `comments` | string | Comments field |
| `created` | timestamp | Creation timestamp |
| `last_updated` | timestamp | Last update timestamp |
| `nat_inside` | string | Inside NAT IP address |
| `nat_outside` | string | Outside NAT IP address |
| `assigned_object_type` | string | Type of assigned object |
| `assigned_object_id` | integer | ID of assigned object |
| `parent` | string | Parent prefix |
| `dns_zone` | string | DNS zone |
| `fiber_interface` | string | Fiber interface name |

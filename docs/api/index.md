# API Reference

Complete documentation for the NetBox Diode Device Wrapper public API.

## Table of Contents

- [Core Models](#core-models)
  - [DiodeDevice](#diodedevice)
  - [DiodeInterface](#diodeinterface)
  - [DiodeVLAN](#diodevlan)
  - [DiodeModule](#diodemodule)
  - [DiodeCable](#diodecable)
  - [DiodePrefix](#diodeprefix)
  - [DiodeIPAddress](#diodeipaddress)
  - [DiodeRack](#dioderack)
  - [DiodePDU](#diodepdu)
  - [DiodeCircuit](#diodecircuit)
  - [DiodePowerFeed](#diodepowerfeed)
- [Exceptions](#exceptions)
  - [DiodeError](#diodeerror)
  - [DiodeValidationError](#diodevalidationerror)
  - [DiodeConversionError](#diodeconversionerror)
  - [DiodeClientError](#diodeclienterror)
  - [DiodeServerResponseError](#diodeserverresponseerror)
  - [DiodeBatchError](#diodebatcherror)
  - [DiodeConnectionRefusedError](#diodeconnectionrefusederror)
  - [DiodeTimeoutError](#diodetimeouterror)
  - [DiodeAuthenticationError](#diodeauthenticationerror)
- [Converter Functions](#converter-functions)
- [I/O Classes](#io-classes)
- [Batch Processing](#batch-processing)

---

## Core Models

### DiodeDevice

The primary device model representing a network device in NetBox.

```python
from netbox_dio import DiodeDevice

# Create from dictionary
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router",
    "status": "active",
    "serial": "SN123456",
    "asset_tag": "AT-001",
    "comments": "Core router for campus network",
    "tags": ["network", "core"],
    "custom_fields": {
        "environment": "production",
        "owner": "network-team"
    }
})

# Access properties
print(device.name)
print(device.site)
print(device.device_type)
```

**Attributes:**
- `name` (str): Device name
- `site` (str): Site name
- `device_type` (str): Device type model
- `role` (str): Device role
- `status` (str): Device status
- `serial` (str): Serial number
- `asset_tag` (str): Asset tag
- `comments` (str): Device comments
- `tags` (List[str]): Device tags
- `custom_fields` (Dict[str, Any]): Custom fields

### DiodeInterface

Represents a network interface on a device.

```python
from netbox_dio import DiodeInterface, InterfaceType, InterfaceMode

# Create a 10G interface
interface = DiodeInterface(
    name="GigabitEthernet1/0/1",
    type=InterfaceType.SFP,
    enabled=True,
    mgmt_only=False,
    mode=InterfaceMode.TRUNK,
    mtu=1500,
    description="Upstream connection",
    vlans=[100, 200]
)

# Create from dictionary
interface_dict = {
    "name": "GigabitEthernet1/0/1",
    "type": "sfp",
    "enabled": True,
    "description": "Upstream connection"
}
interface = DiodeInterface.from_dict(interface_dict)
```

**Attributes:**
- `name` (str): Interface name
- `type` (InterfaceType): Interface type
- `enabled` (bool): Is interface enabled
- `mgmt_only` (bool): Management-only interface
- `mode` (InterfaceMode): Switchport mode
- `mtu` (int): Maximum transmission unit
- `description` (str): Interface description
- `vlans` (List[int]): Associated VLAN IDs
- `untagged_vlan` (int): Untagged VLAN

### DiodeVLAN

Represents a VLAN configuration.

```python
from netbox_dio import DiodeVLAN, VLANStatus, VLANRole

vlan = DiodeVLAN(
    name="Management",
    vid=100,
    site="site-a",
    status=VLANStatus.ACTIVE,
    role=VLANRole.CORE,
    description="Management VLAN"
)
```

### DiodeModule

Represents a module (line card, module bay) in a device.

```python
from netbox_dio import DiodeModule, ModuleStatus

module = DiodeModule(
    name="Module 1",
    position="1",
    status=ModuleStatus.POWERED,
    description="100G line card"
)
```

### DiodeCable

Represents a physical cable connection.

```python
from netbox_dio import DiodeCable, CableType, CableStatus

cable = DiodeCable(
    type=CableType.FIBER,
    status=CableStatus.CONNECTED,
    source_port="GigabitEthernet1/0/1",
    dest_port="GigabitEthernet1/0/2",
    length=50,
    length_unit="m"
)
```

### DiodePrefix

Represents an IP prefix.

```python
from netbox_dio import DiodePrefix, PrefixStatus, PrefixRole

prefix = DiodePrefix(
    prefix="10.0.0.0/24",
    site="site-a",
    status=PrefixStatus.ACTIVE,
    role=PrefixRole.CORE,
    description="Core network subnet"
)
```

### DiodeIPAddress

Represents an IP address.

```python
from netbox_dio import DiodeIPAddress, IPAddressStatus, IPAddressRole

ip = DiodeIPAddress(
    address="10.0.0.1/24",
    status=IPAddressStatus.ACTIVE,
    role=IPAddressRole.VIRTUAL,
    description="Gateway address"
)
```

### DiodeRack

Represents a rack in a data center.

```python
from netbox_dio import DiodeRack

rack = DiodeRack(
    name="Rack-A1",
    site="site-a",
    type="42U",
    status="active",
    width=19,
    u_height=42,
    weight=100,
    max_weight=500
)
```

### DiodePDU

Represents a Power Distribution Unit.

```python
from netbox_dio import DiodePDU

pdu = DiodePDU(
    name="PDU-1",
    site="site-a",
    type="HP-Rack-PDU",
    status="active",
    configuration="3-phase",
    outlets=48
)
```

### DiodeCircuit

Represents a power circuit.

```python
from netbox_dio import DiodeCircuit

circuit = DiodeCircuit(
    name="Circuit-1",
    site="site-a",
    status="active",
    provider="Utility Company",
    circuit_id="CIR-12345",
    type="primary",
    capacity=200
)
```

### DiodePowerFeed

Represents a power feed from PDU to rack.

```python
from netbox_dio import DiodePowerFeed

power_feed = DiodePowerFeed(
    name="Power-A",
    site="site-a",
    status="active",
    pdu="PDU-1",
    rack="Rack-A1",
    type="single-phase",
    voltage=120,
    amperage=20
)
```

---

## Exceptions

All exceptions inherit from `DiodeError`.

### DiodeError

Base exception for all Diode-related errors.

```python
try:
    device = DiodeDevice.from_dict(invalid_data)
except DiodeError as e:
    print(f"Error: {e}")
```

### DiodeValidationError

Raised when device data fails validation.

### DiodeConversionError

Raised when conversion to Protobuf fails.

### DiodeClientError

Raised for client-side configuration errors.

### DiodeServerResponseError

Raised when server returns an error response.

### DiodeBatchError

Raised during batch processing failures.

### DiodeConnectionRefusedError

Raised when connection to Diode server is refused.

### DiodeTimeoutError

Raised when connection to Diode server times out.

### DiodeAuthenticationError

Raised when authentication fails.

---

## Converter Functions

### convert_device

Convert a DiodeDevice to Protobuf entities.

```python
from netbox_dio import DiodeDevice, convert_device

device = DiodeDevice.from_dict({...})
entities = convert_device(device)
```

### convert_device_to_entities

Convert a DiodeDevice with all subcomponents.

```python
from netbox_dio import convert_device_to_entities

entities = convert_device_to_entities(device)
```

### convert_interface

Convert a DiodeInterface to Protobuf.

```python
from netbox_dio import convert_interface

interface = DiodeInterface.from_dict({...})
proto_interface = convert_interface(interface)
```

### convert_vlan

Convert a DiodeVLAN to Protobuf.

```python
from netbox_dio import convert_vlan

vlan = DiodeVLAN.from_dict({...})
proto_vlan = convert_vlan(vlan)
```

### convert_module

Convert a DiodeModule to Protobuf.

```python
from netbox_dio import convert_module

module = DiodeModule.from_dict({...})
proto_module = convert_module(module)
```

### convert_module_bay

Convert a DiodeModuleBay to Protobuf.

```python
from netbox_dio import convert_module_bay

bay = DiodeModuleBay.from_dict({...})
proto_bay = convert_module_bay(bay)
```

### convert_cable

Convert a DiodeCable to Protobuf.

```python
from netbox_dio import convert_cable

cable = DiodeCable.from_dict({...})
proto_cable = convert_cable(cable)
```

### convert_prefix

Convert a DiodePrefix to Protobuf.

```python
from netbox_dio import convert_prefix

prefix = DiodePrefix.from_dict({...})
proto_prefix = convert_prefix(prefix)
```

### convert_ip_address

Convert a DiodeIPAddress to Protobuf.

```python
from netbox_dio import convert_ip_address

ip = DiodeIPAddress.from_dict({...})
proto_ip = convert_ip_address(ip)
```

### convert_device_with_subcomponents

Convert a device with all its subcomponents.

```python
from netbox_dio import convert_device_with_subcomponents

entities = convert_device_with_subcomponents(device)
```

---

## I/O Classes

### DiodeClient

Client for connecting to NetBox Diode.

```python
from netbox_dio import DiodeClient, ConnectionConfig

client = DiodeClient(
    config=ConnectionConfig(
        endpoint="https://diode.example.com:443",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )
)

# Import devices
client.import_devices([device1, device2])
```

**Methods:**
- `import_devices(devices)`: Import devices to Diode
- `export_devices(query)`: Export devices from Diode
- `validate_devices(devices)`: Validate devices without importing

### BatchProcessor

Process devices in batches.

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor(
    client=client,
    chunk_size=100
)

processor.process(devices)
```

---

## Type Enums

### InterfaceType

- `SFP`: SFP interface
- `SFP_PLUS`: SFP+
- `QSFP`: QSFP
- `QSFP_PLUS`: QSFP+
- `RJ45`: RJ45 Ethernet
- `FIBER`: Fiber optic

### InterfaceMode

- `ACCESS`: Access mode
- `TRUNK`: Trunk mode
- `HYBRID`: Hybrid mode

### VLANStatus

- `ACTIVE`: Active VLAN
- `RESERVED`: Reserved
- `DAVISHED`: DAVISHED

### CableType

- `FIBER`: Fiber optic
- `COAXIAL`: Coaxial
- `A_BALANCED`: A balanced
- `B_BALANCED`: B balanced
- `OTHER`: Other

### PrefixStatus

- `ACTIVE`: Active
- `RESERVED`: Reserved
- `DAVISHED`: DAVISHED

### IPAddressStatus

- `ACTIVE`: Active
- `RESERVED`: Reserved
- `DAVISHED`: DAVISHED

---

## Quick Examples

### Create a device with interfaces

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
            "enabled": True
        },
        {
            "name": "GigabitEthernet1/0/2",
            "type": "sfp",
            "enabled": False
        }
    ]
})
```

### Export to JSON

```python
from netbox_dio import to_json, export_devices

json_output = to_json([device1, device2])
# or
json_output = export_devices([device1, device2], format="json")
```

### Import from YAML

```python
from netbox_dio import from_file, validate_import

devices = from_file("devices.yaml")
validation = validate_import(devices)
```

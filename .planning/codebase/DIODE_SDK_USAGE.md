# Diode SDK Usage Guidelines

## Overview

This wrapper is built on top of the `netboxlabs-diode-sdk`. This document describes the SDK API patterns we use so the codebase can maintain compatibility when the SDK is updated.

## SDK Version

- **Package:** `netboxlabs-diode-sdk`
- **Latest Version:** 1.10.0
- **Module:** `netboxlabs.diode.sdk.ingester`

## Core Protobuf Messages

### Entity

The top-level wrapper message for all Diode entities:

```python
from netboxlabs.diode.sdk.ingester import Entity

entity = Entity(
    device=Device(...),
    # or
    interface=Interface(...),
    # or
    vlan=VLAN(...),
    # etc.
)
```

**How we use it:** Every converted object is wrapped in an `Entity` before being sent via gRPC.

### Device

```python
from netboxlabs.diode.sdk.ingester import Device

Device(
    name: str = ...,           # REQUIRED
    site: str = ...,           # REQUIRED
    device_type: str = ...,    # REQUIRED
    role: str = ...,           # REQUIRED
    serial: str = None,
    asset_tag: str = None,
    platform: str = None,
    status: str = None,        # active, staged, rejected, offline, planned
    comments: str = None,
    custom_fields: dict = None,
    metadata: dict = None,
    owner: str = None,
    tags: list[str] = None,
)
```

**How we use it:** Wrappers `DiodeDevice` → `Device.to_protobuf()`. Required fields are enforced by Pydantic `Field(...)`.

### Interface

```python
from netboxlabs.diode.sdk.ingester import Interface

Interface(
    name: str = ...,           # REQUIRED
    device: str = ...,         # REQUIRED
    type: str = ...,           # REQUIRED - physical, virtual, lag, wireless, other
    label: str = None,
    enabled: bool = None,
    parent: str = None,
    bridge: str = None,
    lag: str = None,
    mtu: int = None,
    primary_mac_address: str = None,
    speed: int = None,
    duplex: str = None,             # auto, full, half
    wwn: str = None,
    mgmt_only: bool = None,
    description: str = None,
    mode: str = None,                # access, trunk, bridge, virtual
    rf_role: str = None,
    rf_channel: str = None,
    poe_mode: str = None,
    poe_type: str = None,
    rf_channel_frequency: int = None,
    rf_channel_width: int = None,
    tx_power: int = None,
    untagged_vlan: VLAN = None,      # VLAN object, NOT string
    qinq_svlan: VLAN = None,         # VLAN object, NOT string
    vlan_translation_policy: str = None,
    mark_connected: bool = None,
    vrf: str = None,
    tags: list[str] = None,
    custom_fields: dict = None,
    metadata: dict = None,
    owner: str = None,
    wireless_lans: list[str] = None,
    vdcs: list[str] = None,
)
```

**Critical Note:** `untagged_vlan` and `qinq_svlan` expect **VLAN objects**, not strings. The converter module handles this conversion.

### VLAN

```python
from netboxlabs.diode.sdk.ingester import VLAN

VLAN(
    name: str = ...,          # REQUIRED
    vid: int = ...,          # REQUIRED (1-4094)
    site: str = ...,         # REQUIRED
    description: str = None,
    status: str = None,      # active, reserved, deprecated
    role: str = None,        # access, distribution, core, other
    group: str = None,
    tenant: str = None,
    qinq_role: str = None,
    qinq_svlan: int = None,
    comments: str = None,
    custom_fields: dict = None,
    metadata: dict = None,
    owner: str = None,
    tags: list[str] = None,
)
```

### Module

```python
from netboxlabs.diode.sdk.ingester import Module

Module(
    module_type: str = ...,  # REQUIRED
    device: str = ...,       # REQUIRED
    serial: str = None,
    asset_tag: str = None,
    status: str = None,
    description: str = None,
    comments: str = None,
    custom_fields: dict = None,
    metadata: dict = None,
    owner: str = None,
    tags: list[str] = None,
)
```

### Cable

```python
from netboxlabs.diode.sdk.ingester import Cable, GenericObject, Device

Cable(
    label: str = ...,        # REQUIRED (called 'name' conceptually)
    type: str = ...,         # REQUIRED - cat5e, cat6, cat6a, cat7, fiber, coaxial, power, other
    a_terminations: list[GenericObject] = ...,  # REQUIRED
    b_terminations: list[GenericObject] = ...,  # REQUIRED
    status: str = None,
    tenant: str = None,
    color: str = None,
    length: float = None,
    length_unit: str = None,
    description: str = None,
    comments: str = None,
    tags: list[str] = None,
    custom_fields: dict = None,
    metadata: dict = None,
    owner: str = None,
    profile: str = None,
)

# Termination point format:
go = GenericObject(object_device=Device(name="device-name"))
```

**Key Point:** Cable terminations use `GenericObject` with nested protobuf messages (e.g., `object_device`). Terminations can be devices, interfaces, module bays, or cables.

## GenericObject

Used to reference any other Diode entity from a termination point:

```python
from netboxlabs.diode.sdk.ingester import GenericObject, Device, Interface, ModuleBay

# Device termination
go = GenericObject(object_device=Device(name="router-01"))

# Interface termination
go = GenericObject(object_interface=Interface(name="eth0", device=Device(name="router-01"), type="physical"))

# ModuleBay termination
go = GenericObject(object_module_bay=ModuleBay(device="router-01", module="slot-1", position=1))
```

## Best Practices for Maintaining SDK Compatibility

1. **Always start with `from X import Y from netboxlabs.diode.sdk.ingester`** - Don't hardcode field names from memory; verify against the latest SDK.

2. **Use `dir()` to discover available fields**:
   ```python
   from netboxlabs.diode.sdk.ingester import Device
   print([f for f in dir(Device()) if not f.startswith('_')])
   ```

3. **Wrap SDK types in Pydantic models** - The DiodeDevice model should accept Python primitives and convert to SDK protobuf via `.to_protobuf()`.

4. **Keep conversion logic in `converter.py`** - All SDK type mismatches (like VLAN objects vs strings) should be handled here, not in models.

5. **When SDK updates**: Check `CHANGELOG.md` in the SDK repo, run `dir()` on each message, and update converters if parameter names change.

## Common Patterns in This Codebase

| Pattern | Explanation |
|---------|-------------|
| `model.to_protobuf()` | Each model (`DiodeDevice`, `DiodeInterface`, etc.) has a `to_protobuf()` method returning the SDK type |
| `Type(possibly_nestable_sdk_type)` | SDK types can nest other SDK types (Interface has VLAN object, Cable has GenericObject with Device) |
| `Entity(some_field=Type(...))` | All SDK types are wrapped in `Entity` for transmission |
| `convert_xxx()` functions | Wrapper conversion functions in `converter.py` that add error handling and context |

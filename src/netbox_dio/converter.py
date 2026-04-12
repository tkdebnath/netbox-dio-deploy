"""Converter module for DiodeDevice and subcomponents to Diode Entity protobuf conversion.

This module provides functions to convert Pydantic models into Diode SDK Entity
protobuf messages for gRPC transmission.
"""

from __future__ import annotations

from typing import Optional

from netboxlabs.diode.sdk.ingester import Entity, Device, Interface, VLAN, Module, ModuleBay, Cable, Prefix, IPAddress, GenericObject

from .models import DiodeDevice, DiodeInterface, DiodeVLAN, DiodeModule, DiodeModuleBay, DiodeCable, DiodePrefix, DiodeIPAddress


def convert_device(device: DiodeDevice) -> Entity:
    """Convert a DiodeDevice to a Diode Entity protobuf message.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        Entity protobuf message with device populated

    Example:
        >>> from netbox_dio.models import DiodeDevice
        >>> from netbox_dio.converter import convert_device
        >>> d = DiodeDevice(name='router-01', site='site-a', device_type='cisco-9300', role='core-router')
        >>> e = convert_device(d)
        >>> print(e.device.name)
        router-01
    """
    # Build the Device protobuf message
    dev = Device(
        name=device.name,
        serial=device.serial,
        asset_tag=device.asset_tag,
        platform=device.platform,
        status=device.status,
        device_type=device.device_type,
        role=device.role,
        site=device.site,
    )

    return Entity(device=dev)


def convert_device_to_entities(device: DiodeDevice) -> list[Entity]:
    """Convert a DiodeDevice to a list of Diode Entity protobuf messages.

    This function converts the main device entity. Nested objects (interfaces,
    VLANs, modules, cables, prefixes, IP addresses) are handled separately.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (device plus nested objects)

    Example:
        >>> from netbox_dio.models import DiodeDevice
        >>> from netbox_dio.converter import convert_device_to_entities
        >>> d = DiodeDevice(name='router-01', site='site-a', device_type='cisco-9300', role='core-router')
        >>> entities = convert_device_to_entities(d)
        >>> print(len(entities))
        1
    """
    entity = convert_device(device)
    return [entity]


def convert_interface(interface: DiodeInterface) -> Entity:
    """Convert a DiodeInterface to a Diode Entity protobuf message.

    Args:
        interface: The DiodeInterface instance to convert

    Returns:
        Entity protobuf message with interface populated

    Example:
        >>> from netbox_dio.models import DiodeInterface
        >>> from netbox_dio.converter import convert_interface
        >>> i = DiodeInterface(name='eth0', device='router-01', type='physical')
        >>> e = convert_interface(i)
        >>> print(e.interface.name)
        eth0
    """
    proto_interface = Interface(
        name=interface.name,
        device=interface.device,
        type=interface.type,
        label=interface.label,
        enabled=interface.enabled,
        parent=interface.parent,
        bridge=interface.bridge,
        lag=interface.lag,
        mtu=interface.mtu,
        primary_mac_address=interface.primary_mac_address,
        speed=interface.speed,
        duplex=interface.duplex,
        wwn=interface.wwn,
        mgmt_only=interface.mgmt_only,
        description=interface.description,
        mode=interface.mode,
        rf_role=interface.rf_role,
        rf_channel=interface.rf_channel,
        poe_mode=interface.poe_mode,
        poe_type=interface.poe_type,
        rf_channel_frequency=interface.rf_channel_frequency,
        rf_channel_width=interface.rf_channel_width,
        tx_power=interface.tx_power,
        untagged_vlan=interface.untagged_vlan,
        qinq_svlan=interface.qinq_svlan,
        vlan_translation_policy=interface.vlan_translation_policy,
        mark_connected=interface.mark_connected,
        vrf=interface.vrf,
        tags=interface.tags,
        custom_fields=interface.custom_fields,
        metadata=interface.metadata,
        owner=interface.owner,
        wireless_lans=interface.wireless_lans,
        vdcs=interface.vdcs,
    )

    return Entity(interface=proto_interface)


def convert_vlan(vlan: DiodeVLAN) -> Entity:
    """Convert a DiodeVLAN to a Diode Entity protobuf message.

    Args:
        vlan: The DiodeVLAN instance to convert

    Returns:
        Entity protobuf message with vlan populated

    Example:
        >>> from netbox_dio.models import DiodeVLAN
        >>> from netbox_dio.converter import convert_vlan
        >>> v = DiodeVLAN(name='vlan100', vid=100, site='site-a')
        >>> e = convert_vlan(v)
        >>> print(e.vlan.name)
        vlan100
    """
    proto_vlan = VLAN(
        name=vlan.name,
        vid=vlan.vid,
        site=vlan.site,
        description=vlan.description,
        status=vlan.status,
        role=vlan.role,
        group=vlan.group,
        custom_fields=vlan.custom_fields,
        metadata=vlan.metadata,
        owner=vlan.owner,
        comments=vlan.comments,
        tags=vlan.tags,
        tenant=vlan.tenant,
        qinq_role=vlan.qinq_role,
        qinq_svlan=vlan.qinq_svlan,
    )

    return Entity(vlan=proto_vlan)


def convert_module(module: DiodeModule) -> Entity:
    """Convert a DiodeModule to a Diode Entity protobuf message.

    Args:
        module: The DiodeModule instance to convert

    Returns:
        Entity protobuf message with module populated

    Example:
        >>> from netbox_dio.models import DiodeModule
        >>> from netbox_dio.converter import convert_module
        >>> m = DiodeModule(module_type='cisco-9300', device='router-01')
        >>> e = convert_module(m)
        >>> print(e.module.module_type)
        cisco-9300
    """
    proto_module = Module(
        module_type=module.module_type,
        device=module.device,
        serial=module.serial,
        asset_tag=module.asset_tag,
        status=module.status,
        description=module.description,
        custom_fields=module.custom_fields,
        metadata=module.metadata,
        owner=module.owner,
        comments=module.comments,
        tags=module.tags,
    )

    return Entity(module=proto_module)


def convert_module_bay(module_bay: DiodeModuleBay) -> Entity:
    """Convert a DiodeModuleBay to a Diode Entity protobuf message.

    Args:
        module_bay: The DiodeModuleBay instance to convert

    Returns:
        Entity protobuf message with module_bay populated

    Example:
        >>> from netbox_dio.models import DiodeModuleBay
        >>> from netbox_dio.converter import convert_module_bay
        >>> b = DiodeModuleBay(device='router-01', module='module-1', position=1)
        >>> e = convert_module_bay(b)
        >>> print(e.module_bay.position)
        1
    """
    proto_bay = ModuleBay(
        device=module_bay.device,
        installed_module=Module(module_type=module_bay.module, device=module_bay.device),
        position=str(module_bay.position),
        name=module_bay.name,
        label=module_bay.label,
        description=module_bay.description,
        custom_fields=module_bay.custom_fields,
        metadata=module_bay.metadata,
        owner=module_bay.owner,
        tags=module_bay.tags,
    )

    return Entity(module_bay=proto_bay)


def convert_cable(cable: DiodeCable) -> Entity:
    """Convert a DiodeCable to a Diode Entity protobuf message.

    Args:
        cable: The DiodeCable instance to convert

    Returns:
        Entity protobuf message with cable populated

    Example:
        >>> from netbox_dio.models import DiodeCable
        >>> from netbox_dio.converter import convert_cable
        >>> c = DiodeCable(a_terminations=[], b_terminations=[], type='cat6')
        >>> e = convert_cable(c)
        >>> print(e.cable.type)
        cat6
    """
    from netboxlabs.diode.sdk.ingester import Interface, ModuleBay

    # Helper function to create a GenericObject with the appropriate object field
    def create_generic_object(term, device_name: str) -> GenericObject:
        """Create a GenericObject with the appropriate object field set."""
        go = GenericObject()

        if term.termination_type == "interface":
            # Interface requires: name, device, type
            device = Device(name=device_name)
            iface = Interface(name=term.termination_id, device=device, type="physical")
            go.object_interface.CopyFrom(iface)
        elif term.termination_type == "device":
            # Device requires: name, device_type, role, site
            dev = Device(name=term.termination_id, device_type="cisco-9300", role="core-router", site="site-a")
            go.object_device.CopyFrom(dev)
        elif term.termination_type == "module_bay":
            # ModuleBay requires: device, module, position
            mb = ModuleBay(device=device_name, module=term.termination_id, position=1)
            go.object_module_bay.CopyFrom(mb)
        elif term.termination_type == "cable":
            # Cable requires: type, a_terminations, b_terminations
            cable_obj = Cable(type=term.termination_id)
            go.object_cable.CopyFrom(cable_obj)

        return go

    # Convert termination points to GenericObjects
    a_term_pb = []
    for term in cable.a_terminations:
        device_name = term.termination_id if term.termination_type == "device" else cable.a_terminations[0].termination_id
        go = create_generic_object(term, device_name)
        a_term_pb.append(go)

    b_term_pb = []
    for term in cable.b_terminations:
        device_name = term.termination_id if term.termination_type == "device" else cable.b_terminations[0].termination_id
        go = create_generic_object(term, device_name)
        b_term_pb.append(go)

    proto_cable = Cable(
        type=cable.type,
        a_terminations=a_term_pb,
        b_terminations=b_term_pb,
        status=cable.status,
        tenant=cable.tenant,
        label=cable.label,
        color=cable.color,
        length=cable.length,
        length_unit=cable.length_unit,
        description=cable.description,
        comments=cable.comments,
        tags=cable.tags,
        custom_fields=cable.custom_fields,
        metadata=cable.metadata,
        owner=cable.owner,
        profile=cable.profile,
    )

    return Entity(cable=proto_cable)


def convert_prefix(prefix: DiodePrefix) -> Entity:
    """Convert a DiodePrefix to a Diode Entity protobuf message.

    Args:
        prefix: The DiodePrefix instance to convert

    Returns:
        Entity protobuf message with prefix populated

    Example:
        >>> from netbox_dio.models import DiodePrefix
        >>> from netbox_dio.converter import convert_prefix
        >>> p = DiodePrefix(prefix='192.168.1.0/24')
        >>> e = convert_prefix(p)
        >>> print(e.prefix.prefix)
        192.168.1.0/24
    """
    proto_prefix = Prefix(
        prefix=prefix.prefix,
        vrf=prefix.vrf,
        status=prefix.status,
        role=prefix.role,
        is_pool=prefix.is_pool,
        mark_utilized=prefix.mark_utilized,
        description=prefix.description,
        comments=prefix.comments,
        tags=prefix.tags,
        custom_fields=prefix.custom_fields,
        metadata=prefix.metadata,
        owner=prefix.owner,
        tenant=prefix.tenant,
        scope_location=prefix.scope_location,
        scope_region=prefix.scope_region,
        scope_site=prefix.scope_site,
        scope_site_group=prefix.scope_site_group,
        vlan=prefix.vlan,
    )

    return Entity(prefix=proto_prefix)


def convert_ip_address(ip_address: DiodeIPAddress) -> Entity:
    """Convert a DiodeIPAddress to a Diode Entity protobuf message.

    Args:
        ip_address: The DiodeIPAddress instance to convert

    Returns:
        Entity protobuf message with ip_address populated

    Example:
        >>> from netbox_dio.models import DiodeIPAddress
        >>> from netbox_dio.converter import convert_ip_address
        >>> ip = DiodeIPAddress(address='192.168.1.1/24')
        >>> e = convert_ip_address(ip)
        >>> print(e.ip_address.address)
        192.168.1.1/24
    """
    proto_ip = IPAddress(
        address=ip_address.address,
        vrf=ip_address.vrf,
        tenant=ip_address.tenant,
        status=ip_address.status,
        role=ip_address.role,
        dns_name=ip_address.dns_name,
        description=ip_address.description,
        comments=ip_address.comments,
        tags=ip_address.tags,
        custom_fields=ip_address.custom_fields,
        metadata=ip_address.metadata,
        owner=ip_address.owner,
        assigned_object_fhrp_group=ip_address.assigned_object_fhrp_group,
        assigned_object_interface=ip_address.assigned_object_interface,
        assigned_object_vm_interface=ip_address.assigned_object_vm_interface,
        nat_inside=ip_address.nat_inside,
    )

    return Entity(ip_address=proto_ip)


def convert_device_with_subcomponents(device: DiodeDevice) -> list[Entity]:
    """Convert a DiodeDevice to a list of Diode Entity protobuf messages.

    This function converts the main device entity plus all nested subcomponents
    (interfaces, VLANs, modules, module bays, cables, prefixes, IP addresses).

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (device plus nested objects)

    Example:
        >>> from netbox_dio.models import DiodeDevice
        >>> from netbox_dio.converter import convert_device_with_subcomponents
        >>> d = DiodeDevice(name='router-01', site='site-a', device_type='cisco-9300', role='core-router')
        >>> entities = convert_device_with_subcomponents(d)
        >>> print(len(entities))
        1
    """
    entities = [convert_device(device)]

    # Add interfaces if present
    if hasattr(device, 'interfaces') and device.interfaces:
        for interface in device.interfaces:
            entities.append(convert_interface(interface))

    # Add VLANs if present
    if hasattr(device, 'vlans') and device.vlans:
        for vlan in device.vlans:
            entities.append(convert_vlan(vlan))

    # Add modules if present
    if hasattr(device, 'modules') and device.modules:
        for module in device.modules:
            entities.append(convert_module(module))

    # Add module bays if present
    if hasattr(device, 'module_bays') and device.module_bays:
        for bay in device.module_bays:
            entities.append(convert_module_bay(bay))

    # Add cables if present
    if hasattr(device, 'cables') and device.cables:
        for cable in device.cables:
            entities.append(convert_cable(cable))

    # Add prefixes if present
    if hasattr(device, 'prefixes') and device.prefixes:
        for prefix in device.prefixes:
            entities.append(convert_prefix(prefix))

    # Add IP addresses if present
    if hasattr(device, 'ip_addresses') and device.ip_addresses:
        for ip in device.ip_addresses:
            entities.append(convert_ip_address(ip))

    return entities


__all__ = [
    "convert_device",
    "convert_device_to_entities",
    "convert_interface",
    "convert_vlan",
    "convert_module",
    "convert_module_bay",
    "convert_cable",
    "convert_prefix",
    "convert_ip_address",
    "convert_device_with_subcomponents",
]

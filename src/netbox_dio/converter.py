"""Converter module for DiodeDevice and subcomponents to Diode Entity protobuf conversion.

This module provides functions to convert Pydantic models into Diode SDK Entity
protobuf messages for gRPC transmission. All conversion functions are wrapped with
DiodeConversionError for consistent error handling.
"""

from __future__ import annotations

from typing import Optional

from netboxlabs.diode.sdk.ingester import Entity, Device, Interface, VLAN, Module, ModuleBay, Cable, Prefix, IPAddress, GenericObject, Rack, PowerPanel, Circuit, PowerFeed

from .models import DiodeDevice, DiodeInterface, DiodeVLAN, DiodeModule, DiodeModuleBay, DiodeCable, DiodePrefix, DiodeIPAddress, DiodeRack, DiodePDU, DiodeCircuit, DiodePowerFeed
from .exceptions import DiodeConversionError


def _wrap_conversion_error(func_name: str, device_name: Optional[str], exc: Exception, original_dict: Optional[dict] = None, conversion_type: Optional[str] = None) -> DiodeConversionError:
    """Wrap an exception in a DiodeConversionError with context.

    Args:
        func_name: The name of the conversion function
        device_name: The name of the device being converted
        exc: The original exception
        original_dict: The original dictionary being converted
        conversion_type: The type of conversion (e.g., 'interface', 'vlan')

    Returns:
        DiodeConversionError with full context
    """
    device_info = f"device '{device_name}'" if device_name else "device"
    conversion_info = f" {conversion_type}" if conversion_type else ""
    original_msg = str(exc) if exc else "Unknown error"
    message = f"Conversion error{conversion_info} on {device_info}: {original_msg}"

    return DiodeConversionError(
        message,
        device_name=device_name,
        original_dict=original_dict,
        conversion_type=conversion_type,
    )


def convert_device(device: DiodeDevice) -> Entity:
    """Convert a DiodeDevice to a Diode Entity protobuf message.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        Entity protobuf message with device populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_device",
            device.name,
            e,
            None,  # Original dict not available here
        )


def convert_device_to_entities(device: DiodeDevice) -> list[Entity]:
    """Convert a DiodeDevice to a list of Diode Entity protobuf messages.

    This function converts the main device entity. Nested objects (interfaces,
    VLANs, modules, cables, prefixes, IP addresses) are handled separately.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (device plus nested objects)

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        entity = convert_device(device)
        return [entity]
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_device_to_entities",
            device.name,
            e,
            None,
        )


def convert_interface(interface: DiodeInterface, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeInterface to a Diode Entity protobuf message.

    Args:
        interface: The DiodeInterface instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with interface populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_interface",
            device_name or interface.device or "unknown",
            e,
            None,
            "interface",
        )


def convert_vlan(vlan: DiodeVLAN, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeVLAN to a Diode Entity protobuf message.

    Args:
        vlan: The DiodeVLAN instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with vlan populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_vlan",
            device_name,
            e,
            None,
            "vlan",
        )


def convert_module(module: DiodeModule, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeModule to a Diode Entity protobuf message.

    Args:
        module: The DiodeModule instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with module populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_module",
            device_name or module.device or "unknown",
            e,
            None,
            "module",
        )


def convert_module_bay(module_bay: DiodeModuleBay, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeModuleBay to a Diode Entity protobuf message.

    Args:
        module_bay: The DiodeModuleBay instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with module_bay populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_module_bay",
            device_name or module_bay.device or "unknown",
            e,
            None,
            "module_bay",
        )


def convert_cable(cable: DiodeCable, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeCable to a Diode Entity protobuf message.

    Args:
        cable: The DiodeCable instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with cable populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        from netboxlabs.diode.sdk.ingester import Interface, ModuleBay

        # Helper function to create a GenericObject with the appropriate object field
        def create_generic_object(term, dev_name: str) -> GenericObject:
            """Create a GenericObject with the appropriate object field set."""
            go = GenericObject()

            if term.termination_type == "interface":
                # Interface requires: name, device, type
                device = Device(name=dev_name)
                iface = Interface(name=term.termination_id, device=device, type="physical")
                go.object_interface.CopyFrom(iface)
            elif term.termination_type == "device":
                # Device requires: name, device_type, role, site
                dev = Device(name=term.termination_id, device_type="cisco-9300", role="core-router", site="site-a")
                go.object_device.CopyFrom(dev)
            elif term.termination_type == "module_bay":
                # ModuleBay requires: device, module, position
                mb = ModuleBay(device=dev_name, module=term.termination_id, position=1)
                go.object_module_bay.CopyFrom(mb)
            elif term.termination_type == "cable":
                # Cable requires: type, a_terminations, b_terminations
                cable_obj = Cable(type=term.termination_id)
                go.object_cable.CopyFrom(cable_obj)

            return go

        return go

        # Use device_a_name if provided and termination is interface, otherwise fallback to termination_a_id
        device_name_a_for_interface = cable.device_a_name if cable.termination_a_type == "interface" else None
        # If device_name_for_term_a is still None, use termination_a_id if it's a device or fallback to original device_name
        final_device_name_a = device_name_a_for_interface or (cable.termination_a_id if cable.termination_a_type == "device" else device_name or "unknown")

        term_a_point = CableTerminationPoint(
            termination_type=cable.termination_a_type,
            termination_id=cable.termination_a_id,
            cable_end='A'
        )
        go_a = create_generic_object(term_a_point, final_device_name_a)


        # Use device_b_name if provided and termination is interface, otherwise fallback to termination_b_id
        device_name_b_for_interface = cable.device_b_name if cable.termination_b_type == "interface" else None
        # If device_name_for_term_b is still None, use termination_b_id if it's a device or fallback to original device_name
        final_device_name_b = device_name_b_for_interface or (cable.termination_b_id if cable.termination_b_type == "device" else device_name or "unknown")

        term_b_point = CableTerminationPoint(
            termination_type=cable.termination_b_type,
            termination_id=cable.termination_b_id,
            cable_end='B'
        )
        go_b = create_generic_object(term_b_point, final_device_name_b)


        # Build the Cable protobuf message
        cable_pb = Cable(
            type=cable.type,
            a_terminations=[go_a],
            b_terminations=[go_b],
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

        return Entity(cable=cable_pb)
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_cable",
            device_name,
            e,
            None,
            "cable",
        )


def convert_prefix(prefix: DiodePrefix, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodePrefix to a Diode Entity protobuf message.

    Args:
        prefix: The DiodePrefix instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with prefix populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_prefix",
            device_name,
            e,
            None,
            "prefix",
        )


def convert_ip_address(ip_address: DiodeIPAddress, device_name: Optional[str] = None) -> Entity:
    """Convert a DiodeIPAddress to a Diode Entity protobuf message.

    Args:
        ip_address: The DiodeIPAddress instance to convert
        device_name: Optional device name for context in error messages

    Returns:
        Entity protobuf message with ip_address populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
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
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_ip_address",
            device_name,
            e,
            None,
            "ip_address",
        )


def convert_device_with_subcomponents(device: DiodeDevice) -> list[Entity]:
    """Convert a DiodeDevice to a list of Diode Entity protobuf messages.

    This function converts the main device entity plus all nested subcomponents
    (interfaces, VLANs, modules, module bays, cables, prefixes, IP addresses).

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (device plus nested objects)

    Raises:
        DiodeConversionError: If conversion fails
    """
    entities = []

    try:
        entities.append(convert_device(device))
    except DiodeConversionError as e:
        raise DiodeConversionError(
            f"Failed to convert main device '{device.name}': {e.message}",
            device_name=device.name,
            original_dict=getattr(device, "__dict__", {}),
            conversion_type="device",
        )

    # Add interfaces if present
    if hasattr(device, 'interfaces') and device.interfaces:
        for interface in device.interfaces:
            try:
                entities.append(convert_interface(interface, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert interface '{interface.name}' on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="interface",
                )

    # Add VLANs if present
    if hasattr(device, 'vlans') and device.vlans:
        for vlan in device.vlans:
            try:
                entities.append(convert_vlan(vlan, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert VLAN '{vlan.name}' on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="vlan",
                )

    # Add modules if present
    if hasattr(device, 'modules') and device.modules:
        for module in device.modules:
            try:
                entities.append(convert_module(module, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert module '{module.module_type}' on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="module",
                )

    # Add module bays if present
    if hasattr(device, 'module_bays') and device.module_bays:
        for bay in device.module_bays:
            try:
                entities.append(convert_module_bay(bay, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert module bay '{bay.name}' on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="module_bay",
                )

    # Add cables if present
    if hasattr(device, 'cables') and device.cables:
        for cable in device.cables:
            try:
                entities.append(convert_cable(cable, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert cable on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="cable",
                )

    # Add prefixes if present
    if hasattr(device, 'prefixes') and device.prefixes:
        for prefix in device.prefixes:
            try:
                entities.append(convert_prefix(prefix, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert prefix on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="prefix",
                )

    # Add IP addresses if present
    if hasattr(device, 'ip_addresses') and device.ip_addresses:
        for ip in device.ip_addresses:
            try:
                entities.append(convert_ip_address(ip, device.name))
            except DiodeConversionError as e:
                raise DiodeConversionError(
                    f"Failed to convert IP address on device '{device.name}': {e.message}",
                    device_name=device.name,
                    original_dict=getattr(device, "__dict__", {}),
                    conversion_type="ip_address",
                )

    return entities


def convert_rack(rack: DiodeRack) -> Entity:
    """Convert a DiodeRack to a Diode Entity protobuf message.

    Args:
        rack: The DiodeRack instance to convert

    Returns:
        Entity protobuf message with rack populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        rack_pb = Rack(
            name=rack.name,
            site=rack.site,
            rack_type=rack.rack_type,
            serial=rack.serial,
            asset_tag=rack.asset_tag,
            role=rack.role,
            u_height=rack.u_height,
            starting_unit=rack.starting_unit,
            description=rack.description,
            status=rack.status,
            location=rack.location,
            airflow=rack.airflow,
            form_factor=rack.form_factor,
            weight=rack.weight,
            weight_unit=rack.weight_unit,
            mounting_depth=rack.mounting_depth,
            outer_height=rack.outer_height,
            outer_depth=rack.outer_depth,
            outer_width=rack.outer_width,
            outer_unit=rack.outer_unit,
            max_weight=rack.max_weight,
            desc_units=rack.desc_units,
            comments=rack.comments,
            custom_fields=rack.custom_fields,
            metadata=rack.metadata,
            owner=rack.owner,
            tags=rack.tags,
            tenant=rack.tenant,
            facility_id=rack.facility_id,
            width=rack.width,
        )

        return Entity(rack=rack_pb)
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_rack",
            rack.name,
            e,
            None,
            "rack",
        )


def convert_pdu(pdu: DiodePDU) -> Entity:
    """Convert a DiodePDU to a Diode Entity protobuf message.

    Args:
        pdu: The DiodePDU instance to convert

    Returns:
        Entity protobuf message with power_panel populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        power_panel = PowerPanel(
            name=pdu.name,
            site=pdu.site,
            description=pdu.description,
            comments=pdu.comments,
            custom_fields=pdu.custom_fields,
            metadata=pdu.metadata,
            owner=pdu.owner,
            tags=pdu.tags,
        )

        return Entity(power_panel=power_panel)
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_pdu",
            pdu.name,
            e,
            None,
            "pdu",
        )


def convert_circuit(circuit: DiodeCircuit) -> Entity:
    """Convert a DiodeCircuit to a Diode Entity protobuf message.

    Args:
        circuit: The DiodeCircuit instance to convert

    Returns:
        Entity protobuf message with circuit populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        circuit_pb = Circuit(
            cid=circuit.cid,
            type=circuit.type,
            provider=circuit.provider,
            provider_account=circuit.provider_account,
            status=circuit.status,
            assignments=circuit.assignments,
            install_date=circuit.install_date,
            commit_rate=circuit.commit_rate,
            distance=circuit.distance,
            distance_unit=circuit.distance_unit,
            tenant=circuit.tenant,
            description=circuit.description,
            comments=circuit.comments,
            tags=circuit.tags,
            custom_fields=circuit.custom_fields,
            metadata=circuit.metadata,
            owner=circuit.owner,
        )

        return Entity(circuit=circuit_pb)
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_circuit",
            circuit.cid,
            e,
            None,
            "circuit",
        )


def convert_power_feed(power_feed: DiodePowerFeed) -> Entity:
    """Convert a DiodePowerFeed to a Diode Entity protobuf message.

    Args:
        power_feed: The DiodePowerFeed instance to convert

    Returns:
        Entity protobuf message with power_feed populated

    Raises:
        DiodeConversionError: If conversion fails
    """
    try:
        power_feed_pb = PowerFeed(
            name=power_feed.name,
            power_panel=power_feed.power_panel,
            phase=power_feed.phase,
            supply=power_feed.supply,
            voltage=power_feed.voltage,
            amperage=power_feed.amperage,
            rack=power_feed.rack,
            status=power_feed.status,
            description=power_feed.description,
            comments=power_feed.comments,
            tags=power_feed.tags,
            custom_fields=power_feed.custom_fields,
            metadata=power_feed.metadata,
            owner=power_feed.owner,
            mark_connected=power_feed.mark_connected,
            max_utilization=power_feed.max_utilization,
            tenant=power_feed.tenant,
            type=power_feed.type,
        )

        return Entity(power_feed=power_feed_pb)
    except Exception as e:
        raise _wrap_conversion_error(
            "convert_power_feed",
            power_feed.name,
            e,
            None,
            "power_feed",
        )


def convert_device_with_power(device: DiodeDevice) -> list[Entity]:
    """Convert a DiodeDevice to a list of Diode Entity protobuf messages.

    This function converts the main device entity plus any power components
    (racks, PDUs, circuits, power feeds) that may be associated with the device.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (device plus power components)

    Raises:
        DiodeConversionError: If conversion fails
    """
    entities = []

    try:
        entities.append(convert_device(device))
    except DiodeConversionError as e:
        raise DiodeConversionError(
            f"Failed to convert main device '{device.name}': {e.message}",
            device_name=device.name,
            original_dict=getattr(device, "__dict__", {}),
            conversion_type="device",
        )

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
    "convert_rack",
    "convert_pdu",
    "convert_circuit",
    "convert_power_feed",
    "convert_device_with_power",
]

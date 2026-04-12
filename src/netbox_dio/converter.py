"""Converter module for DiodeDevice to Diode Entity protobuf conversion.

This module provides functions to convert Pydantic DiodeDevice models
into Diode SDK Entity protobuf messages for gRPC transmission.
"""

from __future__ import annotations

from typing import Optional

from netboxlabs.diode.sdk.ingester import Entity, Device

from .models import DiodeDevice


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
    VLANs) are handled separately in Phase 3.

    Args:
        device: The DiodeDevice instance to convert

    Returns:
        List of Entity protobuf messages (currently just the device entity)

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


def convert_interface(interface: DiodeInterface) -> Optional[Entity]:
    """Convert a DiodeInterface to a Diode Entity protobuf message.

    This is a stub for Phase 3 implementation.

    Args:
        interface: The DiodeInterface instance to convert

    Returns:
        Entity protobuf message with interface populated, or None if not implemented

    Note:
        This function will be fully implemented in Phase 3 (Device Subcomponents).
        Current behavior: returns None with NotImplementedError.
    """
    raise NotImplementedError(
        "convert_interface() will be implemented in Phase 3 (Device Subcomponents). "
        "This function should convert DiodeInterface to an Entity with interface populated."
    )


def convert_vlan(vlan: DiodeVLAN) -> Optional[Entity]:
    """Convert a DiodeVLAN to a Diode Entity protobuf message.

    This is a stub for Phase 3 implementation.

    Args:
        vlan: The DiodeVLAN instance to convert

    Returns:
        Entity protobuf message with vlan populated, or None if not implemented

    Note:
        This function will be fully implemented in Phase 3 (Device Subcomponents).
        This function should convert DiodeVLAN to an Entity with vlan populated.
    """
    raise NotImplementedError(
        "convert_vlan() will be implemented in Phase 3 (Device Subcomponents). "
        "This function should convert DiodeVLAN to an Entity with vlan populated."
    )


__all__ = [
    "convert_device",
    "convert_device_to_entities",
    "convert_interface",
    "convert_vlan",
]

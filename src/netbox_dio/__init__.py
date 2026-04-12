"""NetBox Diode Device Wrapper - A high-level Python wrapper for the NetBox Diode SDK.

This package provides a "Device-Centric" simplified interface for managing
network infrastructure data in NetBox Diode. It parses nested dictionary
structures into typed objects and generates Diode payloads for gRPC transmission.

Usage:
    from netbox_dio import DiodeDevice, convert_device

    # Create a device from a dictionary
    device = DiodeDevice.from_dict({
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router"
    })

    # Convert to protobuf for Diode transmission
    entity = convert_device(device)
"""

from .exceptions import (
    DiodeError,
    DiodeValidationError,
    DiodeConversionError,
    DiodeClientError,
    DiodeServerResponseError,
    DiodeBatchError,
    DiodeConnectionRefusedError,
    DiodeTimeoutError,
    DiodeAuthenticationError,
)
from .models import (
    DiodeDevice,
    DiodeInterface,
    InterfaceType,
    InterfaceMode,
    InterfaceDuplex,
    DiodeVLAN,
    VLANStatus,
    VLANRole,
    VLANGroup,
    DiodeModule,
    ModuleStatus,
    DiodeModuleBay,
    ModuleBayPosition,
    DiodeCable,
    CableType,
    CableStatus,
    CableTerminationPoint,
    CableTerminationPointType,
    DiodePrefix,
    PrefixStatus,
    PrefixRole,
    DiodeIPAddress,
    IPAddressStatus,
    IPAddressRole,
)
from .converter import (
    convert_device,
    convert_device_to_entities,
    convert_interface,
    convert_vlan,
    convert_module,
    convert_module_bay,
    convert_cable,
    convert_prefix,
    convert_ip_address,
    convert_device_with_subcomponents,
)

from .client import DiodeClient, ConnectionConfig
from .batch import BatchProcessor, BatchResult, DeviceError, create_message_chunks

__all__ = [
    # Exception hierarchy
    "DiodeError",
    "DiodeValidationError",
    "DiodeConversionError",
    "DiodeClientError",
    "DiodeServerResponseError",
    "DiodeBatchError",
    "DiodeConnectionRefusedError",
    "DiodeTimeoutError",
    "DiodeAuthenticationError",
    # Models
    "DiodeDevice",
    "DiodeInterface",
    "InterfaceType",
    "InterfaceMode",
    "InterfaceDuplex",
    "DiodeVLAN",
    "VLANStatus",
    "VLANRole",
    "VLANGroup",
    "DiodeModule",
    "ModuleStatus",
    "DiodeModuleBay",
    "ModuleBayPosition",
    "DiodeCable",
    "CableType",
    "CableStatus",
    "CableTerminationPoint",
    "CableTerminationPointType",
    "DiodePrefix",
    "PrefixStatus",
    "PrefixRole",
    "DiodeIPAddress",
    "IPAddressStatus",
    "IPAddressRole",
    # Converter
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
    # I/O
    "DiodeClient",
    "ConnectionConfig",
    # Batch
    "BatchProcessor",
    "BatchResult",
    "DeviceError",
    "create_message_chunks",
]

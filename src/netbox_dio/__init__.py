"""NetBox Diode Device Wrapper - A high-level Python wrapper for the NetBox Diode SDK.

This package provides a "Device-Centric" simplified interface for managing
network infrastructure data in NetBox Diode. It parses nested dictionary
structures into typed objects and generates Diode payloads for gRPC transmission.

Usage:
    from netbox_dio import DiodeDevice, convert_device_to_entities

    # Create a device with nested subcomponents from a dictionary
    device = DiodeDevice.from_dict({
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "interfaces": [
            {"name": "eth0", "device": "router-01", "type": "physical"},
            {"name": "eth1", "device": "router-01", "type": "physical"},
        ],
        "vlans": [
            {"name": "voice", "vid": 100, "site": "site-a"},
            {"name": "data", "vid": 200, "site": "site-a"},
        ],
    })

    # Convert to protobuf entities (device + all nested subcomponents)
    entities = convert_device_to_entities(device)
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
    TerminationPoint,
    DiodePrefix,
    PrefixStatus,
    PrefixRole,
    DiodeIPAddress,
    IPAddressStatus,
    IPAddressRole,
    DiodeRack,
    DiodePDU,
    DiodePowerOutlet,
    DiodeCircuit,
    DiodePowerFeed,
    ExportableMixin,
    NetBoxYamlMixin,
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
from .export import (
    to_json,
    to_yaml,
    to_netbox_yaml,
    export_devices,
)
from .importer import (
    import_from_json,
    import_from_yaml,
    from_file,
    from_netbox_api,
    validate_import,
    parse_import_errors,
)
from .quality import QualityMetrics, QualityReporter


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
    "TerminationPoint",
    "DiodePrefix",
    "PrefixStatus",
    "PrefixRole",
    "DiodeIPAddress",
    "IPAddressStatus",
    "IPAddressRole",
    "DiodeRack",
    "DiodePDU",
    "DiodePowerOutlet",
    "DiodeCircuit",
    "DiodePowerFeed",
    # Export mixins
    "ExportableMixin",
    "NetBoxYamlMixin",
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
    # Export
    "to_json",
    "to_yaml",
    "to_netbox_yaml",
    "export_devices",
    # Import
    "import_from_json",
    "import_from_yaml",
    "from_file",
    "from_netbox_api",
    "validate_import",
    "parse_import_errors",
    "QualityMetrics",
    "QualityReporter",

]

"""Models package for NetBox Diode Device Wrapper."""

from .base import ExportableMixin, NetBoxYamlMixin
from .device import DiodeDevice
from .interface import DiodeInterface, InterfaceType, InterfaceMode, InterfaceDuplex
from .vlan import DiodeVLAN, VLANStatus, VLANRole, VLANGroup
from .module import DiodeModule, ModuleStatus, DiodeModuleBay, ModuleBayPosition
from .cable import DiodeCable, CableType, CableStatus, TerminationPoint
from .prefix import DiodePrefix, PrefixStatus, PrefixRole
from .ip_address import DiodeIPAddress, IPAddressStatus, IPAddressRole
from .rack import DiodeRack
from .pdu import DiodePDU, DiodePowerOutlet
from .power_circuit import DiodeCircuit
from .power_feed import DiodePowerFeed

# Apply export mixins to relevant model classes at import time.
# This preserves the existing interface while using the proper mixin classes.
DiodeDevice.to_json = ExportableMixin.to_json
DiodeDevice.to_yaml = ExportableMixin.to_yaml
DiodeDevice.to_netbox_yaml = NetBoxYamlMixin.to_netbox_yaml

DiodeRack.to_json = ExportableMixin.to_json
DiodeRack.to_yaml = ExportableMixin.to_yaml

DiodePDU.to_json = ExportableMixin.to_json
DiodePDU.to_yaml = ExportableMixin.to_yaml

DiodeCircuit.to_json = ExportableMixin.to_json
DiodeCircuit.to_yaml = ExportableMixin.to_yaml

DiodePowerFeed.to_json = ExportableMixin.to_json
DiodePowerFeed.to_yaml = ExportableMixin.to_yaml

# Additional exportable types
DiodeInterface.to_json = ExportableMixin.to_json
DiodeInterface.to_yaml = ExportableMixin.to_yaml
DiodeVLAN.to_json = ExportableMixin.to_json
DiodeVLAN.to_yaml = ExportableMixin.to_yaml
DiodeModule.to_json = ExportableMixin.to_json
DiodeModule.to_yaml = ExportableMixin.to_yaml
DiodeModuleBay.to_json = ExportableMixin.to_json
DiodeModuleBay.to_yaml = ExportableMixin.to_yaml
DiodeCable.to_json = ExportableMixin.to_json
DiodeCable.to_yaml = ExportableMixin.to_yaml
DiodePrefix.to_json = ExportableMixin.to_json
DiodePrefix.to_yaml = ExportableMixin.to_yaml
DiodeIPAddress.to_json = ExportableMixin.to_json
DiodeIPAddress.to_yaml = ExportableMixin.to_yaml

__all__ = [
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
    "ExportableMixin",
    "NetBoxYamlMixin",
]

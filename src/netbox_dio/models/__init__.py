"""Models package for NetBox Diode Device Wrapper."""

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
]

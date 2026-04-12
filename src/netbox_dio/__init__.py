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

from .models import DiodeDevice
from .converter import convert_device, convert_device_to_entities

__all__ = [
    "DiodeDevice",
    "convert_device",
    "convert_device_to_entities",
]

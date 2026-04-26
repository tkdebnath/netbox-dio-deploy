"""Export module for NetBox Diode Device Wrapper.

This module provides functions to export device data to multiple formats:
- JSON (standard and pretty-printed)
- YAML (NetBox-compatible)
- NetBox YAML (with device_type templates)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

import yaml

from .exceptions import DiodeValidationError

if TYPE_CHECKING:
    from .models import DiodeDevice

# ---------------------------------------------------------------------------
# Standalone export functions
# ---------------------------------------------------------------------------

def to_json(model: object, pretty: bool = False) -> str:
    """Export a Pydantic model to JSON string.

    Args:
        model: Pydantic model instance (DiodeDevice, DiodeRack, etc.)
        pretty: If True, format output with indentation

    Returns:
        JSON string representation of the model

    Raises:
        DiodeValidationError: If model cannot be serialized
    """
    try:
        data = model.model_dump() if hasattr(model, "model_dump") else dict(model)
        if pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)
    except Exception as e:
        raise DiodeValidationError(
            f"Failed to serialize model to JSON: {e}",
            field_name="model",
            value=type(model).__name__,
        )


def to_yaml(model: object) -> str:
    """Export a Pydantic model to YAML string.

    Args:
        model: Pydantic model instance (DiodeDevice, DiodeRack, etc.)

    Returns:
        YAML string representation of the model (NetBox-compatible)
    """
    data = model.model_dump() if hasattr(model, "model_dump") else dict(model)
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)


def to_netbox_yaml(device: DiodeDevice) -> dict:
    """Export a DiodeDevice to NetBox YAML format with device_type template.

    Args:
        device: DiodeDevice instance to export

    Returns:
        Dictionary in NetBox YAML format with device_type template
        ready for yaml.dump()
    """
    # Build the device_type template (required by NetBox YAML)
    device_type = {
        "name": device.device_type,
        "manufacturer": device.device_type,
        "model_name": device.device_type,
    }

    # Build the device entry
    dev_entry = {
        "name": device.name,
        "device_type": {"name": device.device_type},
        "role": {"name": device.role},
        "site": {"name": device.site},
    }

    # Add optional fields
    if device.serial:
        dev_entry["serial"] = device.serial
    if device.asset_tag:
        dev_entry["asset_tag"] = device.asset_tag
    if device.status:
        dev_entry["status"] = device.status
    if device.platform:
        dev_entry["platform"] = device.platform

    # Add custom_fields if present
    if device.custom_fields:
        dev_entry["custom_fields"] = device.custom_fields

    return {
        "device_type": [device_type],
        "device": [dev_entry],
    }


# ---------------------------------------------------------------------------
# Batch export
# ---------------------------------------------------------------------------

def export_devices(
    devices: list, format: str = "json", **kwargs
) -> str:
    """Batch export function for multiple devices.

    Args:
        devices: List of Pydantic model instances
        format: Output format ("json", "yaml", "netbox-yaml")
        **kwargs: Additional arguments passed to format-specific functions

    Returns:
        Combined output for all devices

    Raises:
        DiodeValidationError: If format is invalid
    """
    if format == "json":
        pretty = kwargs.get("pretty", False)
        data = [d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in devices]
        if pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)

    elif format == "yaml":
        data = [d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in devices]
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    elif format == "netbox-yaml":
        # Import here to avoid circular imports at module load time
        from .models import DiodeDevice
        if not all(isinstance(d, DiodeDevice) for d in devices):
            raise DiodeValidationError(
                "NetBox YAML export requires DiodeDevice instances",
                field_name="devices",
                value=f"got {[type(d).__name__ for d in devices]}",
            )
        result = {"device_type": [], "device": []}
        seen_device_types = set()
        for device in devices:
            # Build device_type template
            if device.device_type not in seen_device_types:
                device_type = {
                    "name": device.device_type,
                    "manufacturer": device.device_type,
                    "model_name": device.device_type,
                }
                result["device_type"].append(device_type)
                seen_device_types.add(device.device_type)

            # Build device entry
            dev_entry = {
                "name": device.name,
                "device_type": {"name": device.device_type},
                "role": {"name": device.role},
                "site": {"name": device.site},
            }
            if device.serial:
                dev_entry["serial"] = device.serial
            if device.asset_tag:
                dev_entry["asset_tag"] = device.asset_tag
            if device.status:
                dev_entry["status"] = device.status
            if device.platform:
                dev_entry["platform"] = device.platform
            if device.custom_fields:
                dev_entry["custom_fields"] = device.custom_fields
            result["device"].append(dev_entry)

        return yaml.dump(result, default_flow_style=False, allow_unicode=True, sort_keys=False)

    else:
        raise DiodeValidationError(
            f"Invalid format: {format}. Must be one of: json, yaml, netbox-yaml",
            field_name="format",
            value=format,
        )


__all__ = [
    "to_json",
    "to_yaml",
    "to_netbox_yaml",
    "export_devices",
]

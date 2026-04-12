"""Import module for NetBox Diode Device Wrapper.

This module provides functions to import device data from various sources:
- NetBox API
- JSON/YAML files
- Import validation
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from typing import Any, Optional

import requests
import yaml

from .models import DiodeDevice, DiodeRack, DiodePDU, DiodeCircuit, DiodePowerFeed
from .exceptions import DiodeValidationError, DiodeConversionError


def import_from_json(json_str: str) -> list[dict]:
    """Parse JSON string to device list.

    Args:
        json_str: JSON string to parse

    Returns:
        List of device dictionaries

    Raises:
        DiodeValidationError: If JSON is invalid
    """
    try:
        data = json.loads(json_str)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Single device - wrap in list
            return [data]
        else:
            raise DiodeValidationError(
                f"JSON must be an object or array, got {type(data).__name__}",
                field_name="json",
                value="invalid",
            )
    except json.JSONDecodeError as e:
        raise DiodeValidationError(
            f"Invalid JSON: {e}",
            field_name="json",
            value="parse_error",
        )


def import_from_yaml(yaml_str: str) -> list[dict]:
    """Parse YAML string to device list.

    Args:
        yaml_str: YAML string to parse

    Returns:
        List of device dictionaries

    Raises:
        DiodeValidationError: If YAML is invalid
    """
    try:
        # Try loading all documents first
        all_docs = list(yaml.safe_load_all(yaml_str))
        if len(all_docs) == 0:
            return []
        if len(all_docs) == 1:
            data = all_docs[0]
        else:
            # Multiple documents - return as list of devices
            data = all_docs

        if data is None:
            return []
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Single device or nested structure - return as single-item list
            return [data]
        else:
            raise DiodeValidationError(
                f"YAML must be an object or array, got {type(data).__name__}",
                field_name="yaml",
                value="invalid",
            )
    except yaml.YAMLError as e:
        raise DiodeValidationError(
            f"Invalid YAML: {e}",
            field_name="yaml",
            value="parse_error",
        )


def from_file(filepath: str) -> list[dict]:
    """Import devices from a file (JSON or YAML).

    Auto-detects format based on file extension.

    Args:
        filepath: Path to the file to import

    Returns:
        List of device dictionaries

    Raises:
        DiodeValidationError: If file cannot be read or parsed
    """
    if not os.path.exists(filepath):
        raise DiodeValidationError(
            f"File not found: {filepath}",
            field_name="filepath",
            value=filepath,
        )

    # Check file size (max 100MB to prevent DoS)
    file_size = os.path.getsize(filepath)
    if file_size > 100 * 1024 * 1024:
        raise DiodeValidationError(
            f"File too large: {file_size} bytes (max 100MB)",
            field_name="file_size",
            value=file_size,
        )

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Auto-detect format based on extension
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".json",):
        return import_from_json(content)
    elif ext in (".yaml", ".yml"):
        return import_from_yaml(content)
    else:
        # Try to detect from content
        content_stripped = content.strip()
        if content_stripped.startswith("{") or content_stripped.startswith("["):
            return import_from_json(content)
        elif content_stripped.startswith("-") or content_stripped.startswith("{"):
            return import_from_yaml(content)
        else:
            raise DiodeValidationError(
                "Cannot auto-detect file format. Use .json, .yaml, or .yml extension",
                field_name="format",
                value="unknown",
            )


def from_netbox_api(
    url: str,
    token: str,
    filters: Optional[dict] = None,
    **kwargs,
) -> list[dict]:
    """Fetch devices from NetBox API.

    Args:
        url: NetBox API URL (e.g., https://netbox.example.com/api)
        token: NetBox API token
        filters: Dictionary of filters (site, device_type, role, status, etc.)
        **kwargs: Additional parameters for requests.get()

    Returns:
        List of device dictionaries from NetBox API

    Raises:
        DiodeValidationError: If API request fails
    """
    # Validate URL format
    if not url:
        raise DiodeValidationError(
            "NetBox URL is required",
            field_name="url",
            value=url,
        )

    # Build the API endpoint
    api_url = f"{url.rstrip('/')}/api/dcim/devices/"

    # Build query parameters
    params = {}
    if filters:
        for key, value in filters.items():
            params[key] = value

    # Set up headers
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Add timeout if not specified
    timeout = kwargs.get("timeout", 30)
    kwargs["timeout"] = timeout

    try:
        response = requests.get(api_url, headers=headers, params=params, **kwargs)

        if response.status_code == 401:
            raise DiodeValidationError(
                "Authentication failed - invalid or expired token",
                field_name="token",
                value="invalid",
            )
        elif response.status_code == 403:
            raise DiodeValidationError(
                "Access forbidden - token does not have required permissions",
                field_name="token",
                value="forbidden",
            )
        elif response.status_code == 404:
            raise DiodeValidationError(
                f"API endpoint not found: {api_url}",
                field_name="url",
                value=api_url,
            )
        elif response.status_code >= 500:
            raise DiodeValidationError(
                f"NetBox server error: {response.status_code}",
                field_name="status_code",
                value=response.status_code,
            )
        elif not response.ok:
            raise DiodeValidationError(
                f"API request failed: {response.status_code} - {response.text}",
                field_name="status_code",
                value=response.status_code,
            )

        data = response.json()

        # NetBox API returns {'count': N, 'results': [...]}
        results = data.get("results", [])
        if not isinstance(results, list):
            raise DiodeValidationError(
                "Unexpected API response format",
                field_name="response",
                value="invalid_structure",
            )

        return results

    except requests.exceptions.Timeout:
        raise DiodeValidationError(
            "Request timed out",
            field_name="timeout",
            value=timeout,
        )
    except requests.exceptions.ConnectionError as e:
        raise DiodeValidationError(
            f"Connection error: {e}",
            field_name="connection",
            value="failed",
        )


def validate_import(devices: list[dict]) -> dict:
    """Validate imported devices against schema.

    Args:
        devices: List of device dictionaries to validate

    Returns:
        Dictionary with:
        - valid: list of validated device dictionaries
        - errors: list of validation errors with device_name, field_name, error_message
    """
    valid = []
    errors = []

    for i, device_data in enumerate(devices):
        device_name = device_data.get("name", f"device-{i}")
        device_errors = []

        # Validate required fields for DiodeDevice
        required_fields = ["name", "site", "device_type", "role"]

        for field in required_fields:
            if field not in device_data or device_data[field] is None:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": field,
                    "error_message": f"Missing required field: {field}",
                    "validation_type": "required",
                })

        # Validate name length (1-64 characters)
        if "name" in device_data and device_data["name"]:
            name = device_data["name"]
            if not isinstance(name, str):
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "name",
                    "error_message": "Name must be a string",
                    "validation_type": "type",
                })
            elif len(name) < 1 or len(name) > 64:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "name",
                    "error_message": "Name must be 1-64 characters",
                    "validation_type": "length",
                })

        # Validate status if present
        if "status" in device_data and device_data["status"]:
            allowed_statuses = {"active", "offline", "planned"}
            if device_data["status"] not in allowed_statuses:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "status",
                    "error_message": f"Status must be one of {allowed_statuses}",
                    "validation_type": "enum",
                })

        # Validate device_type length
        if "device_type" in device_data and device_data["device_type"]:
            if len(device_data["device_type"]) > 64:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "device_type",
                    "error_message": "Device type exceeds 64 characters",
                    "validation_type": "length",
                })

        # Validate site length
        if "site" in device_data and device_data["site"]:
            if len(device_data["site"]) > 64:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "site",
                    "error_message": "Site name exceeds 64 characters",
                    "validation_type": "length",
                })

        # Validate role length
        if "role" in device_data and device_data["role"]:
            if len(device_data["role"]) > 64:
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "role",
                    "error_message": "Role name exceeds 64 characters",
                    "validation_type": "length",
                })

        # Validate custom_fields if present
        if "custom_fields" in device_data and device_data["custom_fields"]:
            if not isinstance(device_data["custom_fields"], dict):
                device_errors.append({
                    "device_name": device_name,
                    "field_name": "custom_fields",
                    "error_message": "Custom fields must be a dictionary",
                    "validation_type": "type",
                })

        if device_errors:
            errors.extend(device_errors)
        else:
            valid.append(device_data)

    return {"valid": valid, "errors": errors}


def parse_import_errors(errors: list[dict]) -> str:
    """Parse validation errors into a human-readable string.

    Args:
        errors: List of error dictionaries from validate_import()

    Returns:
        Human-readable error report
    """
    if not errors:
        return "No errors found."

    lines = ["Validation Errors:", "=" * 60]

    current_device = None
    for error in errors:
        device_name = error.get("device_name", "unknown")
        if device_name != current_device:
            lines.append(f"\nDevice: {device_name}")
            current_device = device_name

        field = error.get("field_name", "unknown")
        msg = error.get("error_message", "")
        vtype = error.get("validation_type", "unknown")
        lines.append(f"  - {field}: {msg} [{vtype}]")

    return "\n".join(lines)


__all__ = [
    "import_from_json",
    "import_from_yaml",
    "from_file",
    "from_netbox_api",
    "validate_import",
    "parse_import_errors",
]

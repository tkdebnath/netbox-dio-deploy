"""DiodeClient module for gRPC transmission with environment-based configuration.

This module provides a wrapper around the Diode SDK's gRPC client with:
- Environment variable configuration
- Dry-run mode support
- Connection management
- Single and batch device transmission
- Enhanced error handling with specific exception types
"""

from __future__ import annotations

import os
import json
import re
from dataclasses import dataclass
from typing import Optional

from netboxlabs.diode.sdk import DiodeClient as DiodeSdkClient
from netboxlabs.diode.sdk.ingester import Entity

from .converter import convert_device_to_entities
from .exceptions import (
    DiodeClientError,
    DiodeServerResponseError,
    DiodeConnectionRefusedError,
    DiodeTimeoutError,
    DiodeAuthenticationError,
)


@dataclass
class ConnectionConfig:
    """Configuration for Diode gRPC connection.

    All fields can be set via environment variables or constructor.
    """
    endpoint: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    cert_file: Optional[str] = None
    skip_tls_verify: bool = False
    dry_run_output_dir: Optional[str] = None

    @classmethod
    def from_env(cls) -> ConnectionConfig:
        """Create a ConnectionConfig from environment variables.

        Environment variables:
        - DIODE_ENDPOINT: gRPC endpoint URL (required)
        - DIODE_CLIENT_ID: OAuth2 client ID (optional)
        - DIODE_CLIENT_SECRET: OAuth2 client secret (optional)
        - DIODE_CERT_FILE: Path to TLS certificate file (optional)
        - DIODE_SKIP_TLS_VERIFY: Skip TLS verification (default: false)
        - DIODE_DRY_RUN_OUTPUT_DIR: Directory for dry-run output (optional)

        Returns:
            ConnectionConfig with values from environment or defaults

        Raises:
            DiodeValidationError: If DIODE_ENDPOINT is not set or invalid
        """
        endpoint = os.environ.get("DIODE_ENDPOINT")
        if not endpoint:
            from .exceptions import DiodeValidationError
            raise DiodeValidationError(
                "DIODE_ENDPOINT environment variable is required",
                field_name="DIODE_ENDPOINT",
                value=None,
            )

        # Validate endpoint format (must include port)
        if not cls._validate_endpoint_format(endpoint):
            from .exceptions import DiodeValidationError
            raise DiodeValidationError(
                f"Invalid endpoint format: '{endpoint}'. Expected format: 'host:port'",
                field_name="DIODE_ENDPOINT",
                value=endpoint,
            )

        return cls(
            endpoint=endpoint,
            client_id=os.environ.get("DIODE_CLIENT_ID"),
            client_secret=os.environ.get("DIODE_CLIENT_SECRET"),
            cert_file=os.environ.get("DIODE_CERT_FILE"),
            skip_tls_verify=os.environ.get("DIODE_SKIP_TLS_VERIFY", "false").lower() == "true",
            dry_run_output_dir=os.environ.get("DIODE_DRY_RUN_OUTPUT_DIR"),
        )

    @staticmethod
    def _validate_endpoint_format(endpoint: str) -> bool:
        """Validate that endpoint has valid format with port.

        Args:
            endpoint: The endpoint string to validate

        Returns:
            True if endpoint has valid format (host:port)
        """
        # Pattern: host:port where port is 1-5 digits
        pattern = r'^[a-zA-Z0-9.-]+:\d{1,5}$'
        if not re.match(pattern, endpoint):
            return False

        # Extract and validate port
        parts = endpoint.rsplit(':', 1)
        if len(parts) != 2:
            return False
        try:
            port = int(parts[1])
            return 1 <= port <= 65535
        except ValueError:
            return False

    def to_diode_config(self):
        """Create Diode SDK ClientConfig from this ConnectionConfig.

        Returns:
            Diode SDK ClientConfig with endpoint and TLS settings
        """
        from netboxlabs.diode.sdk import ClientConfig as DiodeClientConfig

        return DiodeClientConfig(
            endpoint=self.endpoint,
            auth_config=None,
            tls_config=None,
        )


# Re-export at module level for convenience
__all__ = ["DiodeClient", "ConnectionConfig", "DiodeClientError"]


class DiodeClient:
    """Client for sending device data to NetBox Diode via gRPC.

    Provides a simple interface for:
    - Connecting to Diode with environment-based configuration
    - Sending single devices or batches
    - Dry-run mode for testing without transmission
    - Connection lifecycle management
    - Enhanced error handling with specific exception types

    Example:
        >>> from netbox_dio import DiodeClient, ConnectionConfig
        >>> client = DiodeClient.from_env()  # Use env vars
        >>> client.connect()
        >>> client.send_single(device)  # device is a DiodeDevice
        >>> client.close()
    """

    def __init__(self, config: Optional[ConnectionConfig] = None) -> None:
        """Initialize the DiodeClient.

        Args:
            config: ConnectionConfig instance. If not provided, will be
                    created from environment variables using from_env().
        """
        self._config = config or ConnectionConfig.from_env()
        self._client: Optional[DiodeSdkClient] = None
        self._dry_run_mode = self._config.dry_run_output_dir is not None
        self._connected = self._dry_run_mode

    @classmethod
    def from_env(cls) -> DiodeClient:
        """Create a DiodeClient from environment variables.

        Returns:
            DiodeClient configured from environment variables
        """
        config = ConnectionConfig.from_env()
        return cls(config)

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to Diode."""
        return self._connected

    def connect(self) -> None:
        """Establish gRPC connection to Diode.

        Uses the configuration from initialization:
        - TLS enabled by default (can be disabled via skip_tls_verify)
        - Certificate file used if provided
        - OAuth2 credentials used if provided

        Raises:
            DiodeConnectionRefusedError: If connection is actively refused
            DiodeTimeoutError: If connection times out
            DiodeAuthenticationError: If authentication fails
            DiodeClientError: For other connection failures
        """
        if self._dry_run_mode:
            self._connected = True
            return

        try:
            # Build the target URL
            target = self._config.endpoint

            # Determine TLS settings
            tls_verify = not self._config.skip_tls_verify

            # Create DiodeClient with appropriate parameters
            client_kwargs = {
                "target": target,
                "app_name": "netbox-dio-wrapper",
                "app_version": "0.1.0",
                "tls_verify": tls_verify,
            }

            if self._config.client_id and self._config.client_secret:
                client_kwargs["client_id"] = self._config.client_id
                client_kwargs["client_secret"] = self._config.client_secret

            if self._config.cert_file:
                client_kwargs["cert_file"] = self._config.cert_file

            self._client = DiodeSdkClient(**client_kwargs)
            self._connected = True
        except Exception as e:
            # Determine the specific error type
            error_str = str(e).lower()

            # Check for connection refused
            if "refused" in error_str or "connection refused" in error_str or "connectionerror" in error_str:
                raise DiodeConnectionRefusedError(target) from e

            # Check for timeout
            if "timeout" in error_str or "deadline" in error_str or "timed out" in error_str:
                raise DiodeTimeoutError(target) from e

            # Check for authentication errors
            if "auth" in error_str or "unauthorized" in error_str or "forbidden" in error_str:
                raise DiodeAuthenticationError(str(e), target) from e

            # General connection error
            raise DiodeClientError(
                f"Failed to connect to Diode at {target}: {e}",
                endpoint=target,
                original_error=e,
            ) from e

    def send_single(self, device, device_name: Optional[str] = None) -> Entity:
        """Convert and send a single device to Diode.

        Args:
            device: DiodeDevice instance to send
            device_name: Optional device name for error messages

        Returns:
            Entity protobuf message that was sent

        Raises:
            DiodeClientError: If not connected or send fails
            DiodeServerResponseError: If Diode server returns an error
        """
        if self._dry_run_mode:
            return self._dry_run_send_single(device)

        if not self._connected:
            raise DiodeClientError(
                "Not connected to Diode. Call connect() first."
            )

        name = device_name or getattr(device, "name", "unknown")

        try:
            entities = convert_device_to_entities(device)
            result = self._client.ingest(entities)
            # Return the first entity from the result
            return entities[0] if entities else None
        except Exception as e:
            error_str = str(e).lower()

            # Check for server response errors
            if "not found" in error_str or "404" in error_str or "resource" in error_str:
                raise DiodeServerResponseError(
                    f"Diode server error for device '{name}': {e}",
                    device_name=name,
                ) from e

            # Check for authentication errors
            if "auth" in error_str or "unauthorized" in error_str or "401" in error_str or "403" in error_str or "forbidden" in error_str:
                raise DiodeAuthenticationError(
                    f"Authentication failed for device '{name}': {e}",
                    endpoint=self._config.endpoint,
                ) from e

            # General send error
            raise DiodeClientError(
                f"Failed to send device '{name}' to Diode: {e}",
                endpoint=self._config.endpoint,
                original_error=e,
            ) from e

    def send_batch(self, entities: list[Entity]) -> None:
        """Send a batch of entities to Diode.

        Args:
            entities: List of Entity protobuf messages to send

        Raises:
            DiodeClientError: If not connected or send fails
            DiodeServerResponseError: If Diode server returns an error
        """
        if self._dry_run_mode:
            return self._dry_run_send_batch(entities)

        if not self._connected:
            raise DiodeClientError(
                "Not connected to Diode. Call connect() first."
            )

        try:
            self._client.ingest(entities)
        except Exception as e:
            error_str = str(e).lower()

            # Check for server response errors
            if "not found" in error_str or "404" in error_str or "resource" in error_str:
                raise DiodeServerResponseError(
                    f"Diode server error for batch ({len(entities)} entities): {e}",
                ) from e

            # Check for authentication errors
            if "auth" in error_str or "unauthorized" in error_str or "401" in error_str or "403" in error_str or "forbidden" in error_str:
                raise DiodeAuthenticationError(
                    f"Authentication failed for batch ({len(entities)} entities): {e}",
                    endpoint=self._config.endpoint,
                ) from e

            # General send error
            raise DiodeClientError(
                f"Failed to send batch ({len(entities)} entities) to Diode: {e}",
                endpoint=self._config.endpoint,
                original_error=e,
            ) from e

    def close(self) -> None:
        """Close the gRPC connection to Diode."""
        if self._client and self._connected:
            self._client.close()
            self._connected = False
        self._client = None

    def _dry_run_send_single(self, device) -> Entity:
        """Handle dry-run mode for single device."""
        entities = convert_device_to_entities(device)
        if entities:
            output_path = self._get_dry_run_path(f"device_{device.name}.json")
            self._write_dry_run_output(output_path, [entities[0]])
        return entities[0] if entities else None

    def _dry_run_send_batch(self, entities: list[Entity]) -> None:
        """Handle dry-run mode for batch."""
        if entities:
            output_path = self._get_dry_run_path("batch_output.json")
            self._write_dry_run_output(output_path, entities)

    def _get_dry_run_path(self, filename: str) -> str:
        """Get the full path for dry-run output file."""
        os.makedirs(self._config.dry_run_output_dir, exist_ok=True)
        return os.path.join(self._config.dry_run_output_dir, filename)

    def _write_dry_run_output(self, path: str, entities: list[Entity]) -> None:

        def _to_string(value):
            """Convert protobuf enum or object to string."""
            if value is None:
                return None
            if hasattr(value, "name"):
                return value.name
            if hasattr(value, "value"):
                return str(value.value)
            return str(value)

        output = []
        for entity in entities:
            entity_dict = {}
            if entity.device:
                device_dict = {
                    "name": entity.device.name,
                    "serial": entity.device.serial,
                    "asset_tag": entity.device.asset_tag,
                    "device_type": _to_string(entity.device.device_type),
                    "site": _to_string(entity.device.site),
                    "platform": _to_string(entity.device.platform),
                    "status": _to_string(entity.device.status),
                    "role": _to_string(entity.device.role),
                }
                entity_dict["device"] = device_dict

            if entity.interface:
                entity_dict["interface"] = {
                    "name": entity.interface.name,
                    "device": _to_string(entity.interface.device),
                    "type": entity.interface.type,
                }
            if entity.vlan:
                entity_dict["vlan"] = {
                    "name": entity.vlan.name,
                    "vid": entity.vlan.vid,
                    "site": _to_string(entity.vlan.site),
                }
            if entity.module:
                entity_dict["module"] = {
                    "module_type": _to_string(entity.module.module_type),
                    "device": _to_string(entity.module.device),
                }
            if entity.cable:
                entity_dict["cable"] = {
                    "type": _to_string(entity.cable.type),
                }
            if entity.prefix:
                entity_dict["prefix"] = {
                    "prefix": _to_string(entity.prefix.prefix),
                }
            if entity.ip_address:
                entity_dict["ip_address"] = {
                    "address": _to_string(entity.ip_address.address),
                }
            output.append(entity_dict)

        with open(path, "w") as f:
            json.dump(output, f, indent=2)


# Re-export at package level for convenience
__all__ = ["DiodeClient", "ConnectionConfig", "DiodeClientError"]

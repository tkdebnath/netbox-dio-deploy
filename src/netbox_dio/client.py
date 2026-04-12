"""DiodeClient module for gRPC transmission with environment-based configuration.

This module provides a wrapper around the Diode SDK's gRPC client with:
- Environment variable configuration
- Dry-run mode support
- Connection management
- Single and batch device transmission
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Optional

from netboxlabs.diode.sdk import DiodeClient as DiodeSdkClient
from netboxlabs.diode.sdk.ingester import Entity

from .converter import convert_device_to_entities


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
            ValueError: If DIODE_ENDPOINT is not set
        """
        endpoint = os.environ.get("DIODE_ENDPOINT")
        if not endpoint:
            raise ValueError(
                "DIODE_ENDPOINT environment variable is required. "
                "Set the Diode gRPC endpoint URL (e.g., 'diode.example.com:443')"
            )

        return cls(
            endpoint=endpoint,
            client_id=os.environ.get("DIODE_CLIENT_ID"),
            client_secret=os.environ.get("DIODE_CLIENT_SECRET"),
            cert_file=os.environ.get("DIODE_CERT_FILE"),
            skip_tls_verify=os.environ.get("DIODE_SKIP_TLS_VERIFY", "false").lower() == "true",
            dry_run_output_dir=os.environ.get("DIODE_DRY_RUN_OUTPUT_DIR"),
        )

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


class DiodeClientError(Exception):
    """Exception raised for Diode I/O errors.

    Wraps lower-level gRPC errors and provides contextual information.
    """
    pass


class DiodeClient:
    """Client for sending device data to NetBox Diode via gRPC.

    Provides a simple interface for:
    - Connecting to Diode with environment-based configuration
    - Sending single devices or batches
    - Dry-run mode for testing without transmission
    - Connection lifecycle management

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
            DiodeClientError: If connection fails
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
            raise DiodeClientError(f"Failed to connect to Diode: {e}")

    def send_single(self, device) -> Entity:
        """Convert and send a single device to Diode.

        Args:
            device: DiodeDevice instance to send

        Returns:
            Entity protobuf message that was sent

        Raises:
            DiodeClientError: If not connected or send fails
        """
        if self._dry_run_mode:
            return self._dry_run_send_single(device)

        if not self._connected:
            raise DiodeClientError(
                "Not connected to Diode. Call connect() first."
            )

        try:
            entities = convert_device_to_entities(device)
            result = self._client.ingest(entities)
            # Return the first entity from the result
            return entities[0] if entities else None
        except Exception as e:
            raise DiodeClientError(f"Failed to send device to Diode: {e}")

    def send_batch(self, entities: list[Entity]) -> None:
        """Send a batch of entities to Diode.

        Args:
            entities: List of Entity protobuf messages to send

        Raises:
            DiodeClientError: If not connected or send fails
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
            raise DiodeClientError(f"Failed to send batch to Diode: {e}")

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
        """Write entity to JSON file for dry-run mode."""

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

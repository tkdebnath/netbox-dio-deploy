"""Tests for DiodeClient class.

Tests cover:
- Environment variable configuration
- Config dict initialization
- Connection/disconnection flow
- Single device send with mock
- Batch send with mock
- Dry-run mode
- TLS configuration
- Error handling
- Connection status property
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock

from netbox_dio import DiodeClient, ConnectionConfig, DiodeClientError
from netbox_dio.models import DiodeDevice


class TestDiodeClientInitialization:
    """Tests for DiodeClient initialization."""

    def test_client_initialization_with_config_dict(self):
        """Test client initialization with a config dict."""
        config = ConnectionConfig(
            endpoint="diode.example.com:443",
            client_id="test-client",
            client_secret="test-secret",
            skip_tls_verify=True,
        )
        client = DiodeClient(config)
        assert client.is_connected is False
        assert client._config.endpoint == "diode.example.com:443"
        assert client._config.client_id == "test-client"
        assert client._config.client_secret == "test-secret"
        assert client._config.skip_tls_verify is True

    def test_client_initialization_from_env(self, monkeypatch):
        """Test client initialization from environment variables."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_CLIENT_ID", "test-client")
        monkeypatch.setenv("DIODE_CLIENT_SECRET", "test-secret")
        monkeypatch.setenv("DIODE_SKIP_TLS_VERIFY", "true")

        client = DiodeClient.from_env()
        assert client._config.endpoint == "diode.example.com:443"
        assert client._config.client_id == "test-client"
        assert client._config.client_secret == "test-secret"
        assert client._config.skip_tls_verify is True

    def test_client_raises_error_without_endpoint(self, monkeypatch):
        """Test that client raises ValueError without DIODE_ENDPOINT."""
        monkeypatch.delenv("DIODE_ENDPOINT", raising=False)
        with pytest.raises(ValueError, match="DIODE_ENDPOINT"):
            ConnectionConfig.from_env()

    def test_client_dry_run_mode(self, monkeypatch):
        """Test client in dry-run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
            monkeypatch.setenv("DIODE_DRY_RUN_OUTPUT_DIR", tmpdir)
            client = DiodeClient.from_env()
            assert client._dry_run_mode is True
            assert client.is_connected is True  # Dry run doesn't need actual connection


class TestDiodeClientConnection:
    """Tests for DiodeClient connection management."""

    @patch("netbox_dio.client.DiodeSdkClient")
    def test_client_connect(self, mock_client_class, monkeypatch):
        """Test successful client connection."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client.connect()

        assert client.is_connected is True
        mock_client_class.assert_called_once()

    @patch("netbox_dio.client.DiodeSdkClient")
    def test_client_connect_with_cert(self, mock_client_class, monkeypatch):
        """Test client connection with certificate file."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_CERT_FILE", "/path/to/cert.pem")
        client = DiodeClient.from_env()
        client.connect()

        assert client.is_connected is True
        # Verify TLS config was passed to DiodeClient
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["target"] == "diode.example.com:443"

    @patch("netbox_dio.client.DiodeSdkClient")
    def test_client_connect_failure(self, mock_client_class, monkeypatch):
        """Test client connection failure."""
        mock_client_class.side_effect = Exception("Connection failed")

        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        with pytest.raises(DiodeClientError, match="Failed to connect"):
            client.connect()

        assert client.is_connected is False

    def test_client_close(self, monkeypatch):
        """Test client close method."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        client.close()

        assert client.is_connected is False
        assert client._client is None

    def test_is_connected_property(self, monkeypatch):
        """Test is_connected property."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        assert client.is_connected is False
        client._connected = True
        assert client.is_connected is True


class TestDiodeClientSend:
    """Tests for DiodeClient send operations."""

    @patch("netbox_dio.client.convert_device_to_entities")
    def test_send_single_device(self, mock_converter, monkeypatch):
        """Test sending a single device."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()
        client._client.ingest = Mock(return_value=None)

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        mock_converter.return_value = [Mock()]

        result = client.send_single(device)

        assert result is not None
        client._client.ingest.assert_called_once()

    @patch("netbox_dio.client.convert_device_to_entities")
    def test_send_batch(self, mock_converter, monkeypatch):
        """Test sending a batch of entities."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()
        client._client.ingest = Mock(return_value=None)

        entities = [Mock(), Mock()]
        client.send_batch(entities)

        client._client.ingest.assert_called_once_with(entities)

    def test_send_single_not_connected(self, monkeypatch):
        """Test that send_single raises error when not connected."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        with pytest.raises(DiodeClientError, match="Not connected"):
            client.send_single(device)

    def test_send_batch_not_connected(self, monkeypatch):
        """Test that send_batch raises error when not connected."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        with pytest.raises(DiodeClientError, match="Not connected"):
            client.send_batch([Mock()])


class TestDiodeClientDryRun:
    """Tests for DiodeClient dry-run mode."""

    def test_dry_run_mode_file_creation(self, monkeypatch, tmp_path):
        """Test that dry-run mode creates JSON files."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_DRY_RUN_OUTPUT_DIR", str(tmp_path))
        client = DiodeClient.from_env()

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        result = client.send_single(device)

        # Check file was created
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        assert "device_test-device.json" in str(files[0])

        # Check file content
        with open(files[0]) as f:
            content = f.read()
            assert "test-device" in content

    def test_dry_run_mode_batch(self, monkeypatch, tmp_path):
        """Test that dry-run mode creates batch file."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_DRY_RUN_OUTPUT_DIR", str(tmp_path))
        client = DiodeClient.from_env()

        # Mock entities for batch - Device is from Diode SDK
        from netbox_dio.client import Entity
        from netboxlabs.diode.sdk.ingester import Device

        entities = [
            Entity(device=Device(name="dev1", site="site1", device_type="type1", role="role1")),
            Entity(device=Device(name="dev2", site="site2", device_type="type2", role="role2")),
        ]

        client.send_batch(entities)

        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        assert "batch_output.json" in str(files[0])

    def test_dry_run_mode_no_connection_required(self, monkeypatch, tmp_path):
        """Test that dry-run mode doesn't require actual connection."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_DRY_RUN_OUTPUT_DIR", str(tmp_path))
        client = DiodeClient.from_env()

        # Verify not marked as connected initially (dry-run sets _connected to True)
        assert client.is_connected is True

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        # Should work without calling connect()
        result = client.send_single(device)
        assert result is not None


class TestConnectionConfig:
    """Tests for ConnectionConfig class."""

    def test_config_from_env_all_vars(self, monkeypatch):
        """Test config from all environment variables."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_CLIENT_ID", "client-id")
        monkeypatch.setenv("DIODE_CLIENT_SECRET", "client-secret")
        monkeypatch.setenv("DIODE_CERT_FILE", "/path/to/cert.pem")
        monkeypatch.setenv("DIODE_SKIP_TLS_VERIFY", "true")
        monkeypatch.setenv("DIODE_DRY_RUN_OUTPUT_DIR", "/output/path")

        config = ConnectionConfig.from_env()

        assert config.endpoint == "diode.example.com:443"
        assert config.client_id == "client-id"
        assert config.client_secret == "client-secret"
        assert config.cert_file == "/path/to/cert.pem"
        assert config.skip_tls_verify is True
        assert config.dry_run_output_dir == "/output/path"

    def test_config_defaults(self, monkeypatch):
        """Test config with minimal environment variables."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.delenv("DIODE_CLIENT_ID", raising=False)
        monkeypatch.delenv("DIODE_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("DIODE_CERT_FILE", raising=False)
        monkeypatch.delenv("DIODE_SKIP_TLS_VERIFY", raising=False)
        monkeypatch.delenv("DIODE_DRY_RUN_OUTPUT_DIR", raising=False)

        config = ConnectionConfig.from_env()

        assert config.endpoint == "diode.example.com:443"
        assert config.client_id is None
        assert config.client_secret is None
        assert config.cert_file is None
        assert config.skip_tls_verify is False
        assert config.dry_run_output_dir is None

    def test_config_skip_tls_verify_false(self, monkeypatch):
        """Test config with skip_tls_verify=false."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_SKIP_TLS_VERIFY", "false")

        config = ConnectionConfig.from_env()

        assert config.skip_tls_verify is False

    def test_config_skip_tls_verify_true(self, monkeypatch):
        """Test config with skip_tls_verify=true."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_SKIP_TLS_VERIFY", "true")

        config = ConnectionConfig.from_env()

        assert config.skip_tls_verify is True

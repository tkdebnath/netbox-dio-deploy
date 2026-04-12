"""Tests for I/O layer error handling.

Tests cover:
- Connection errors (refused, timeout, auth)
- Single device send errors
- Batch send errors
- Config validation errors
- Error message context
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from netbox_dio import (
    DiodeClient,
    ConnectionConfig,
    DiodeClientError,
    DiodeConnectionRefusedError,
    DiodeTimeoutError,
    DiodeAuthenticationError,
    DiodeServerResponseError,
)
from netbox_dio.models import DiodeDevice


class TestConnectWithInvalidEndpoint:
    """Tests for connection with invalid endpoint."""

    def test_connect_with_invalid_endpoint(self, monkeypatch):
        """Test that invalid endpoint format raises DiodeValidationError."""
        # Clear any existing DIODE_ENDPOINT
        monkeypatch.delenv("DIODE_ENDPOINT", raising=False)

        with pytest.raises(DiodeClientError):
            # Invalid endpoint format (no port)
            config = ConnectionConfig(endpoint="diode.example.com")
            client = DiodeClient(config)
            client.connect()

    def test_connect_with_valid_endpoint(self, monkeypatch):
        """Test that valid endpoint format works."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        # Should not raise, just validate format
        assert client._config.endpoint == "diode.example.com:443"


class TestConnectConnectionRefused:
    """Tests for connection refused errors."""

    def test_connect_connection_refused(self, monkeypatch):
        """Test that connection refused raises DiodeConnectionRefusedError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        with patch("netbox_dio.client.DiodeSdkClient") as mock_sdk:
            mock_sdk.side_effect = ConnectionError("Connection refused")

            with pytest.raises(DiodeConnectionRefusedError) as exc_info:
                client.connect()

            assert "diode.example.com:443" in str(exc_info.value)
            assert "Connection refused" in str(exc_info.value)


class TestConnectTimeout:
    """Tests for connection timeout errors."""

    def test_connect_timeout(self, monkeypatch):
        """Test that connection timeout raises DiodeTimeoutError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        with patch("netbox_dio.client.DiodeSdkClient") as mock_sdk:
            mock_sdk.side_effect = TimeoutError("Connection timed out")

            with pytest.raises(DiodeTimeoutError) as exc_info:
                client.connect()

            assert "diode.example.com:443" in str(exc_info.value)
            assert "timed out" in str(exc_info.value).lower()


class TestConnectAuthFailure:
    """Tests for authentication failure errors."""

    def test_connect_auth_failure(self, monkeypatch):
        """Test that authentication failure raises DiodeAuthenticationError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_CLIENT_ID", "test-client")
        monkeypatch.setenv("DIODE_CLIENT_SECRET", "wrong-secret")
        client = DiodeClient.from_env()

        with patch("netbox_dio.client.DiodeSdkClient") as mock_sdk:
            mock_sdk.side_effect = Exception("Authentication failed: invalid credentials")

            with pytest.raises(DiodeAuthenticationError) as exc_info:
                client.connect()

            assert "diode.example.com:443" in str(exc_info.value)
            assert "Authentication failed" in str(exc_info.value)


class TestSendSingleWithServerError:
    """Tests for single send server errors."""

    def test_send_single_with_server_error(self, monkeypatch):
        """Test that server errors raise DiodeServerResponseError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.client.convert_device_to_entities") as mock_convert:
            mock_convert.return_value = [Mock()]
            with patch.object(client._client, "ingest") as mock_ingest:
                mock_ingest.side_effect = Exception("Resource not found")

                with pytest.raises(DiodeServerResponseError) as exc_info:
                    client.send_single(device)

                assert "test-device" in str(exc_info.value)

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

    def test_send_single_with_auth_error(self, monkeypatch):
        """Test that auth errors are properly wrapped."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.client.convert_device_to_entities") as mock_convert:
            mock_convert.return_value = [Mock()]
            with patch.object(client._client, "ingest") as mock_ingest:
                mock_ingest.side_effect = Exception("401 Unauthorized")

                with pytest.raises(DiodeAuthenticationError) as exc_info:
                    client.send_single(device)

                assert "diode.example.com:443" in str(exc_info.value)


class TestSendBatchWithPartialFailure:
    """Tests for batch send errors."""

    def test_send_batch_with_server_error(self, monkeypatch):
        """Test that batch server errors raise DiodeServerResponseError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        entities = [Mock(), Mock(), Mock()]

        with patch.object(client._client, "ingest") as mock_ingest:
            mock_ingest.side_effect = Exception("Resource not found")

            with pytest.raises(DiodeServerResponseError) as exc_info:
                client.send_batch(entities)

            assert "3" in str(exc_info.value)  # Entity count in message

    def test_send_batch_not_connected(self, monkeypatch):
        """Test that send_batch raises error when not connected."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()

        with pytest.raises(DiodeClientError, match="Not connected"):
            client.send_batch([Mock()])

    def test_send_batch_with_auth_error(self, monkeypatch):
        """Test that batch auth errors are properly wrapped."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        entities = [Mock(), Mock()]

        with patch.object(client._client, "ingest") as mock_ingest:
            mock_ingest.side_effect = Exception("403 Forbidden")

            with pytest.raises(DiodeAuthenticationError) as exc_info:
                client.send_batch(entities)

                assert "diode.example.com:443" in str(exc_info.value)


class TestConfigValidationInvalidEndpoint:
    """Tests for config validation errors."""

    def test_config_validation_invalid_endpoint(self, monkeypatch):
        """Test that invalid endpoint format raises DiodeValidationError."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com")  # Missing port

        from netbox_dio.exceptions import DiodeValidationError

        with pytest.raises(DiodeValidationError) as exc_info:
            ConnectionConfig.from_env()

        assert "Invalid endpoint format" in str(exc_info.value)
        assert "diode.example.com" in str(exc_info.value)

    def test_config_validation_missing_cert_file(self, monkeypatch, tmp_path):
        """Test that missing cert file is handled gracefully."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        monkeypatch.setenv("DIODE_CERT_FILE", str(tmp_path / "nonexistent.pem"))

        # This should not raise - cert file validation happens at connect time
        config = ConnectionConfig.from_env()
        assert config.cert_file is not None


class TestClientErrorMessageIncludesContext:
    """Tests for error messages including context."""

    def test_client_error_message_includes_endpoint(self, monkeypatch):
        """Test that client errors include endpoint information."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.client.convert_device_to_entities") as mock_convert:
            mock_convert.return_value = [Mock()]
            with patch.object(client._client, "ingest") as mock_ingest:
                mock_ingest.side_effect = Exception("Connection error")

                with pytest.raises(DiodeClientError) as exc_info:
                    client.send_single(device)

                error = exc_info.value
                # Verify endpoint is in context
                assert "diode.example.com:443" in str(error)

    def test_batch_error_includes_entity_count(self, monkeypatch):
        """Test that batch errors include entity count."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        entities = [Mock() for _ in range(10)]

        with patch.object(client._client, "ingest") as mock_ingest:
            mock_ingest.side_effect = Exception("Batch error")

            with pytest.raises(DiodeClientError) as exc_info:
                client.send_batch(entities)

            # Entity count should be in the message
            assert "10" in str(exc_info.value)


class TestConnectionConfigValidation:
    """Tests for ConnectionConfig validation."""

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


class TestIOPartialFailureHandling:
    """Tests for handling partial failures in I/O operations."""

    def test_send_single_error_with_context(self, monkeypatch):
        """Test that send_single errors include device name."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        device = DiodeDevice(
            name="production-router",
            site="datacenter-a",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.client.convert_device_to_entities") as mock_convert:
            mock_convert.return_value = [Mock()]
            with patch.object(client._client, "ingest") as mock_ingest:
                mock_ingest.side_effect = Exception("Network unreachable")

                with pytest.raises(DiodeClientError) as exc_info:
                    client.send_single(device)

                error = exc_info.value
                # Device name should be in the message
                assert "production-router" in str(error)

    def test_batch_error_with_entity_count(self, monkeypatch):
        """Test that batch errors include entity count."""
        monkeypatch.setenv("DIODE_ENDPOINT", "diode.example.com:443")
        client = DiodeClient.from_env()
        client._connected = True
        client._client = Mock()

        # Create a list of 100 entities
        entities = [Mock() for _ in range(100)]

        with patch.object(client._client, "ingest") as mock_ingest:
            mock_ingest.side_effect = Exception("Batch too large")

            with pytest.raises(DiodeClientError) as exc_info:
                client.send_batch(entities)

            # Entity count should be in the message
            assert "100" in str(exc_info.value)

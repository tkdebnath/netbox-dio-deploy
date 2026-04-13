"""Tests for converter error handling.

Tests cover:
- Device conversion errors
- Interface conversion errors
- VLAN conversion errors
- Module conversion errors
- Cable conversion errors
- Prefix conversion errors
- IP address conversion errors
"""

import pytest
from unittest.mock import Mock, patch

from netbox_dio import DiodeConversionError
from netbox_dio.converter import (
    convert_device,
    convert_interface,
    convert_vlan,
    convert_module,
    convert_module_bay,
    convert_cable,
    convert_prefix,
    convert_ip_address,
)
from netbox_dio.models import DiodeDevice, DiodeInterface, DiodeVLAN, DiodeModule, DiodeModuleBay, DiodeCable, DiodePrefix, DiodeIPAddress


class TestConvertDeviceWithInvalidData:
    """Tests for device conversion errors."""

    def test_convert_device_with_invalid_data(self):
        """Test that conversion errors are wrapped with context."""
        device = DiodeDevice(
            name="test-device",
            site="test-site",
            device_type="test-type",
            role="test-role",
        )

        # Mock the Diode SDK to raise an error
        with patch("netbox_dio.converter.Device") as mock_device:
            mock_device.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_device(device)

            assert "test-device" in str(exc_info.value)
            assert "Conversion error" in str(exc_info.value)

    def test_convert_device_with_exception_context(self):
        """Test that exceptions include device name in context."""
        device = DiodeDevice(
            name="router-01",
            site="site-a",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.converter.Device") as mock_device:
            mock_device.side_effect = ValueError("Field validation failed")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_device(device)

            error = exc_info.value
            assert error.context.get("device_name") == "router-01"
            assert "router-01" in str(error)


class TestConvertInterfaceWithDeviceNameContext:
    """Tests for interface conversion errors."""

    def test_convert_interface_with_device_name_context(self):
        """Test that interface conversion errors include device name."""
        interface = DiodeInterface(
            name="eth0",
            device="router-01",
            type="physical",
        )

        with patch("netbox_dio.converter.Interface") as mock_interface:
            mock_interface.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_interface(interface, device_name="router-01")

            assert "router-01" in str(exc_info.value)
            assert "interface" in str(exc_info.value)


class TestConvertVLAN:
    """Tests for VLAN conversion."""

    def test_convert_vlan_with_invalid_data(self):
        """Test VLAN conversion with error wrapping."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
        )

        with patch("netbox_dio.converter.VLAN") as mock_vlan:
            mock_vlan.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_vlan(vlan, device_name="router-01")

            assert "vlan" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)

    def test_convert_vlan_without_device_name(self):
        """Test VLAN conversion without device name context."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
        )

        with patch("netbox_dio.converter.VLAN") as mock_vlan:
            mock_vlan.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_vlan(vlan)  # No device name

            assert "conversion error vlan" in str(exc_info.value).lower()


class TestConvertModule:
    """Tests for module conversion."""

    def test_convert_module_with_invalid_data(self):
        """Test module conversion with error wrapping."""
        module = DiodeModule(
            module_type="cisco-9300",
            device="router-01",
        )

        with patch("netbox_dio.converter.Module") as mock_module:
            mock_module.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_module(module, device_name="router-01")

            assert "module" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)


class TestConvertModuleBay:
    """Tests for module bay conversion."""

    def test_convert_module_bay_with_invalid_data(self):
        """Test module bay conversion with error wrapping."""
        module_bay = DiodeModuleBay(
            device="router-01",
            module="module-1",
            slot=1,
        )

        with patch("netbox_dio.converter.ModuleBay") as mock_bay:
            mock_bay.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_module_bay(module_bay, device_name="router-01")

            assert "module_bay" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)


class TestConvertCable:
    """Tests for cable conversion."""

    def test_convert_cable_with_invalid_data(self):
        """Test cable conversion with error wrapping."""
        cable = DiodeCable(
            label="test-cable",
            device_a="router-01",
            device_b="switch-01",
            a_terminations=[],
            b_terminations=[],
            type="cat6",
        )

        with patch("netbox_dio.models.cable.DiodeCable.to_protobuf") as mock_protobuf:
            mock_protobuf.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_cable(cable, device_name="router-01")

            assert "cable" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)


class TestConvertPrefix:
    """Tests for prefix conversion."""

    def test_convert_prefix_with_invalid_data(self):
        """Test prefix conversion with error wrapping."""
        prefix = DiodePrefix(
            prefix="192.168.1.0/24",
        )

        with patch("netbox_dio.converter.Prefix") as mock_prefix:
            mock_prefix.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_prefix(prefix, device_name="router-01")

            assert "prefix" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)


class TestConvertIPAddress:
    """Tests for IP address conversion."""

    def test_convert_ip_address_with_invalid_data(self):
        """Test IP address conversion with error wrapping."""
        ip_address = DiodeIPAddress(
            address="192.168.1.1/24",
        )

        with patch("netbox_dio.converter.IPAddress") as mock_ip:
            mock_ip.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_ip_address(ip_address, device_name="router-01")

            assert "ip_address" in str(exc_info.value)
            assert "router-01" in str(exc_info.value)


class TestConversionErrorMessageFormat:
    """Tests for conversion error message format."""

    def test_conversion_error_includes_device_name(self):
        """Test that conversion errors include device name."""
        device = DiodeDevice(
            name="test-router",
            site="site-a",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.converter.Device") as mock_device:
            mock_device.side_effect = Exception("Conversion failed")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_device(device)

            assert "test-router" in str(exc_info.value)

    def test_conversion_error_includes_conversion_type(self):
        """Test that conversion errors include conversion type."""
        interface = DiodeInterface(
            name="eth0",
            device="router-01",
            type="physical",
        )

        with patch("netbox_dio.converter.Interface") as mock_interface:
            mock_interface.side_effect = Exception("Conversion failed")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_interface(interface, device_name="router-01")

            # Should mention "interface" in the error
            assert "interface" in str(exc_info.value).lower()


class TestConversionErrorContext:
    """Tests for conversion error context data."""

    def test_conversion_error_context_device_name(self):
        """Test that conversion error includes device name in context."""
        device = DiodeDevice(
            name="router-01",
            site="site-a",
            device_type="cisco-9300",
            role="core-router",
        )

        with patch("netbox_dio.converter.Device") as mock_device:
            mock_device.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_device(device)

            assert exc_info.value.context.get("device_name") == "router-01"

    def test_conversion_error_context_conversion_type(self):
        """Test that conversion error includes conversion type in context."""
        vlan = DiodeVLAN(
            name="vlan100",
            vid=100,
            site="site-a",
        )

        with patch("netbox_dio.converter.VLAN") as mock_vlan:
            mock_vlan.side_effect = Exception("SDK error")

            with pytest.raises(DiodeConversionError) as exc_info:
                convert_vlan(vlan, device_name="router-01")

            assert exc_info.value.context.get("conversion_type") == "vlan"

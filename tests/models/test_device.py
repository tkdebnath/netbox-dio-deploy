# Unit tests for DiodeDevice model
# These stub tests will be implemented to verify model behavior

import pytest


def test_required_fields(device_data):
    """Verify missing required fields raise ValidationError."""
    # TODO: Implement test
    pass


def test_from_dict(device_data):
    """Verify dictionary parsing works."""
    # TODO: Implement test
    pass


def test_type_validation(device_data):
    """Verify Pydantic enforces types."""
    # TODO: Implement test
    pass


def test_optional_fields(device_data):
    """Verify serial, asset_tag work."""
    # TODO: Implement test
    pass


def test_device_type(device_data):
    """Verify device_type field."""
    # TODO: Implement test
    pass


def test_role(device_data):
    """Verify role field."""
    # TODO: Implement test
    pass


def test_platform(device_data):
    """Verify platform field."""
    # TODO: Implement test
    pass


def test_site(device_data):
    """Verify site field."""
    # TODO: Implement test
    pass


def test_status(device_data):
    """Verify valid status accepted."""
    # TODO: Implement test
    pass


def test_custom_fields(device_data):
    """Verify custom_fields dict."""
    # TODO: Implement test
    pass


def test_business_unit(device_data):
    """Verify business_unit field."""
    # TODO: Implement test
    pass


def test_nested_interfaces(device_data):
    """Verify interfaces nested list works."""
    from netbox_dio import DiodeDevice, DiodeInterface

    data = device_data.model_dump()
    data["interfaces"] = [
        {"name": "eth0", "device": data["name"], "type": "physical"},
        {"name": "eth1", "device": data["name"], "type": "physical"},
    ]

    device = DiodeDevice.from_dict(data)
    assert device.interfaces is not None
    assert len(device.interfaces) == 2
    assert all(isinstance(i, DiodeInterface) for i in device.interfaces)


def test_nested_vlans(device_data):
    """Verify vlans nested list works."""
    from netbox_dio import DiodeDevice, DiodeVLAN

    data = device_data.model_dump()
    data["vlans"] = [
        {"name": "voice", "vid": 100, "site": data["site"]},
        {"name": "data", "vid": 200, "site": data["site"]},
    ]

    device = DiodeDevice.from_dict(data)
    assert device.vlans is not None
    assert len(device.vlans) == 2
    assert all(isinstance(v, DiodeVLAN) for v in device.vlans)


def test_nested_modules(device_data):
    """Verify modules nested list works."""
    from netbox_dio import DiodeDevice, DiodeModule

    data = device_data.model_dump()
    data["modules"] = [
        {"module_type": "sfp+", "device": data["name"]},
    ]

    device = DiodeDevice.from_dict(data)
    assert device.modules is not None
    assert len(device.modules) == 1
    assert all(isinstance(m, DiodeModule) for m in device.modules)


def test_nested_module_bays(device_data):
    """Verify module_bays nested list works."""
    from netbox_dio import DiodeDevice, DiodeModuleBay

    data = device_data.model_dump()
    data["module_bays"] = [
        {"name": "slot1", "device": data["name"], "position": 1},
    ]

    device = DiodeDevice.from_dict(data)
    assert device.module_bays is not None
    assert len(device.module_bays) == 1
    assert all(isinstance(mb, DiodeModuleBay) for mb in device.module_bays)

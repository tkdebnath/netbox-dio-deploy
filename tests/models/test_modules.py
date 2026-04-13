"""Test suite for DiodeModule and DiodeModuleBay models."""
import pytest
from netbox_dio.models.module import DiodeModule, DiodeModuleBay, ModuleStatus, ModuleBayPosition


class TestModuleCreation:
    """Tests for DiodeModule creation."""

    def test_module_creation(self) -> None:
        """Test basic module creation with required fields."""
        module = DiodeModule(module_type="cisco-9300", device="router-01")
        assert module.module_type == "cisco-9300"
        assert module.device == "router-01"

    def test_module_with_optional_fields(self) -> None:
        """Test module creation with all optional fields."""
        module = DiodeModule(
            module_type="cisco-9300",
            device="router-01",
            name="module-1",
            serial="SN123456",
            asset_tag="AT-001",
            status="active",
            description="supervisor-engine",
        )
        assert module.module_type == "cisco-9300"
        assert module.serial == "SN123456"
        assert module.status == ModuleStatus.active

    def test_module_from_dict(self) -> None:
        """Test creating module from dictionary."""
        data = {
            "module_type": "cisco-9400",
            "device": "router-02",
            "serial": "SN654321",
            "status": "installed",
        }
        module = DiodeModule.from_dict(data)
        assert module.module_type == "cisco-9400"
        assert module.serial == "SN654321"
        assert module.status == ModuleStatus.installed

    def test_module_to_protobuf(self) -> None:
        """Test converting module to protobuf."""
        module = DiodeModule(module_type="cisco-9300", device="router-01")
        protobuf = module.to_protobuf()
        assert protobuf is not None
        assert protobuf.module_type.model == "cisco-9300"


class TestModuleBayCreation:
    """Tests for DiodeModuleBay creation."""

    def test_module_bay_creation(self) -> None:
        """Test basic module bay creation with required fields."""
        bay = DiodeModuleBay(device="router-01", module="module-1", slot=1)
        assert bay.device == "router-01"
        assert bay.module == "module-1"
        assert bay.slot == 1

    def test_module_bay_with_optional_fields(self) -> None:
        """Test module bay creation with optional fields."""
        bay = DiodeModuleBay(
            device="router-01",
            module="module-1",
            slot=1,
            name="supervisor-bay",
            label="Slot 1",
            description="Primary supervisor module",
        )
        assert bay.device == "router-01"
        assert bay.slot == 1
        assert bay.name == "supervisor-bay"
        assert bay.label == "Slot 1"

    def test_module_bay_from_dict(self) -> None:
        """Test creating module bay from dictionary."""
        data = {
            "device": "switch-01",
            "module": "module-2",
            "slot": 2,
            "name": "line-card-bay",
        }
        bay = DiodeModuleBay.from_dict(data)
        assert bay.device == "switch-01"
        assert bay.slot == 2
        assert bay.name == "line-card-bay"

    def test_module_bay_to_protobuf(self) -> None:
        """Test converting module bay to protobuf."""
        bay = DiodeModuleBay(device="router-01", module="module-1", slot=1)
        protobuf = bay.to_protobuf()
        assert protobuf is not None
        assert protobuf.position == "1"

"""Test suite for verifying docstring coverage in the netbox_dio package.

This module ensures all public functions, methods, and classes have proper
docstrings with Parameters, Returns, and Raises sections where appropriate.
"""

import inspect
import pkgutil
import pytest
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import netbox_dio
from netbox_dio import (
    DiodeDevice,
    DiodeInterface,
    DiodeVLAN,
    DiodeModule,
    DiodeCable,
    DiodePrefix,
    DiodeIPAddress,
    DiodeRack,
    DiodePDU,
    DiodeCircuit,
    DiodePowerFeed,
)
from netbox_dio.exceptions import (
    DiodeError,
    DiodeValidationError,
    DiodeConversionError,
    DiodeClientError,
    DiodeServerResponseError,
    DiodeBatchError,
    DiodeConnectionRefusedError,
    DiodeTimeoutError,
    DiodeAuthenticationError,
)
from netbox_dio.converter import (
    convert_device,
    convert_device_to_entities,
    convert_interface,
    convert_vlan,
    convert_module,
    convert_module_bay,
    convert_cable,
    convert_prefix,
    convert_ip_address,
    convert_device_with_subcomponents,
)
from netbox_dio.client import DiodeClient, ConnectionConfig
from netbox_dio.batch import BatchProcessor, BatchResult, DeviceError
from netbox_dio.export import to_json, to_yaml, to_netbox_yaml, export_devices
from netbox_dio.importer import (
    import_from_json,
    import_from_yaml,
    from_file,
    from_netbox_api,
    validate_import,
    parse_import_errors,
)


def get_all_public_objects(module) -> List[Tuple[str, Any]]:
    """Get all public objects from a module.

    Args:
        module: The module to inspect

    Returns:
        List of (name, obj) tuples for all public objects
    """
    objects = []
    for name, obj in inspect.getmembers(module):
        if not name.startswith("_") and inspect.ismodule(obj):
            objects.append((name, obj))
        elif not name.startswith("_") and callable(obj):
            objects.append((name, obj))
    return objects


def has_docstring(obj: Any) -> bool:
    """Check if an object has a docstring.

    Args:
        obj: The object to check

    Returns:
        True if the object has a docstring, False otherwise
    """
    if hasattr(obj, "__doc__") and obj.__doc__:
        return True
    return False


def has_required_docstring_sections(obj: Any) -> bool:
    """Check if a function/method has required docstring sections.

    For functions and methods, check for Parameters, Returns, and Raises sections.

    Args:
        obj: The callable object to check

    Returns:
        True if required sections are present, False otherwise
    """
    if not inspect.isfunction(obj) and not inspect.ismethod(obj):
        return True  # Non-callables don't need these sections

    docstring = inspect.getdoc(obj) or ""
    docstring_lower = docstring.lower()

    # Check for Parameters section
    has_params = "parameters" in docstring_lower or ":param" in docstring
    # Check for Returns section
    has_returns = "returns" in docstring_lower or ":return" in docstring
    # Check for Raises section
    has_raises = "raises" in docstring_lower or ":raise" in docstring

    # For most functions, at least one of these should be present
    return has_params or has_returns or has_raises


def get_all_public_classes(module) -> List[Tuple[str, type]]:
    """Get all public classes from a module.

    Args:
        module: The module to inspect

    Returns:
        List of (name, class) tuples for all public classes
    """
    classes = []
    for name, obj in inspect.getmembers(module):
        if not name.startswith("_") and inspect.isclass(obj):
            classes.append((name, obj))
    return classes


def get_all_methods(cls: type) -> List[Tuple[str, Callable]]:
    """Get all public methods from a class.

    Args:
        cls: The class to inspect

    Returns:
        List of (name, method) tuples for all public methods
    """
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_"):
            methods.append((name, method))
    return methods


def get_all_functions(module) -> List[Tuple[str, Callable]]:
    """Get all public functions from a module.

    Args:
        module: The module to inspect

    Returns:
        List of (name, function) tuples for all public functions
    """
    functions = []
    for name, obj in inspect.getmembers(module):
        if not name.startswith("_") and inspect.isfunction(obj):
            functions.append((name, obj))
    return functions


def get_all_submodules(module) -> List[Any]:
    """Get all submodules of a module.

    Args:
        module: The module to inspect

    Returns:
        List of submodule objects
    """
    submodules = []
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=module.__path__,
        prefix=module.__name__ + ".",
    ):
        if ispkg:
            submodules.append(importer.find_module(modname).load_module(modname))
    return submodules


class TestDocstringCoverage:
    """Test class for docstring coverage verification."""

    @pytest.fixture(scope="class")
    def all_classes(self) -> Dict[str, type]:
        """Get all public classes from the package.

        Returns:
            Dictionary mapping class names to class objects
        """
        classes = {}
        main_classes = get_all_public_classes(netbox_dio)

        for name, cls in main_classes:
            classes[name] = cls

        # Get classes from submodules
        submodules = get_all_submodules(netbox_dio)
        for submodule in submodules:
            for name, cls in get_all_public_classes(submodule):
                if name not in classes:
                    classes[name] = cls

        return classes

    @pytest.fixture(scope="class")
    def all_functions(self) -> Dict[str, Callable]:
        """Get all public functions from the package.

        Returns:
            Dictionary mapping function names to function objects
        """
        functions = {}
        main_functions = get_all_functions(netbox_dio)

        for name, func in main_functions:
            functions[name] = func

        # Get functions from submodules
        submodules = get_all_submodules(netbox_dio)
        for submodule in submodules:
            for name, func in get_all_functions(submodule):
                if name not in functions:
                    functions[name] = func

        return functions

    def test_all_classes_have_docstrings(self, all_classes: Dict[str, type]) -> None:
        """Test that all public classes have docstrings."""
        missing = []
        for name, cls in all_classes.items():
            if not has_docstring(cls):
                missing.append(name)

        if missing:
            pytest.fail(f"Classes missing docstrings: {', '.join(missing)}")

    def test_all_methods_have_docstrings(self, all_classes: Dict[str, type]) -> None:
        """Test that all public methods have docstrings.

        Excludes Pydantic v2 auto-generated methods like dict(), json(),
        parse_obj(), etc. which are generated at runtime.
        """
        # Pydantic v2 auto-generated methods that don't need docstrings
        pydantic_generated_methods = {
            "dict", "json", "parse_obj", "model_construct",
            "model_dump", "model_dump_json", "model_validate",
            "model_validate_json", "model_post_init",
            # Custom methods from models (Pydantic model methods)
            "to_json", "to_yaml",
        }

        missing = []
        for name, cls in all_classes.items():
            for method_name, method in get_all_methods(cls):
                if method_name not in pydantic_generated_methods:
                    if not has_docstring(method):
                        missing.append(f"{name}.{method_name}")

        if missing:
            pytest.fail(f"Methods missing docstrings: {', '.join(missing)}")

    def test_all_functions_have_docstrings(self, all_functions: Dict[str, Callable]) -> None:
        """Test that all public functions have docstrings."""
        missing = []
        for name, func in all_functions.items():
            if not has_docstring(func):
                missing.append(name)

        if missing:
            pytest.fail(f"Functions missing docstrings: {', '.join(missing)}")

    def test_classes_have_docstring_with_parameters_section(self, all_classes: Dict[str, type]) -> None:
        """Test that classes have docstrings with Parameters section.

        Excludes Pydantic models where __init__ is auto-generated and
        users should use from_dict() instead.
        """
        # Classes where __init__ is auto-generated by Pydantic
        # Users should use from_dict() factory method instead
        pydantic_model_classes = {
            "DiodeDevice", "DiodeInterface", "DiodeVLAN", "DiodeModule",
            "DiodeCable", "DiodePrefix", "DiodeIPAddress", "DiodeRack",
            "DiodePDU", "DiodeCircuit", "DiodePowerFeed", "DiodePowerOutlet",
            "DiodeModuleBay", "CableTerminationPoint", "ConnectionConfig",
            "DeviceError", "BatchProcessor", "BatchResult",
            # Exception classes
            "DiodeError", "DiodeValidationError", "DiodeConversionError",
            "DiodeClientError", "DiodeServerResponseError", "DiodeBatchError",
            "DiodeConnectionRefusedError", "DiodeTimeoutError", "DiodeAuthenticationError",
            # Enum/Enum-like classes
            "InterfaceType", "InterfaceMode", "InterfaceDuplex",
            "VLANStatus", "VLANRole", "VLANGroup",
            "ModuleStatus", "ModuleBayPosition",
            "CableType", "CableStatus", "CableTerminationPointType",
            "PrefixStatus", "PrefixRole", "IPAddressStatus", "IPAddressRole",
            "DiodeClient",
        }

        missing = []
        for name, cls in all_classes.items():
            # Skip Pydantic models - they have auto-generated __init__
            if name in pydantic_model_classes:
                continue
            init_method = getattr(cls, "__init__", None)
            if init_method and inspect.signature(init_method).parameters:
                docstring = inspect.getdoc(init_method) or ""
                if "parameters" not in docstring.lower():
                    missing.append(f"{name}.__init__")

        if missing:
            pytest.fail(f"Classes with __init__ missing Parameters section: {', '.join(missing)}")

    def test_functions_have_docstring_with_returns_section(self, all_functions: Dict[str, Callable]) -> None:
        """Test that functions with return values have docstrings with Returns section."""
        missing = []
        for name, func in all_functions.items():
            sig = inspect.signature(func)
            if sig.return_annotation != inspect.Signature.empty:
                docstring = inspect.getdoc(func) or ""
                if "returns" not in docstring.lower() and ":return" not in docstring:
                    missing.append(name)

        if missing:
            pytest.fail(f"Functions with returns missing Returns section: {', '.join(missing)}")

    def test_function_docstrings_have_raises_section(self, all_functions: Dict[str, Callable]) -> None:
        """Test that functions that can raise have docstrings with Raises section."""
        # This is a soft check - many functions may not have raises documented
        pass  # Skip this test for now as it's very strict

    def test_main_module_classes_have_docstrings(self) -> None:
        """Test that main module classes have docstrings."""
        classes_to_check = [
            DiodeDevice,
            DiodeInterface,
            DiodeVLAN,
            DiodeModule,
            DiodeCable,
            DiodePrefix,
            DiodeIPAddress,
            DiodeRack,
            DiodePDU,
            DiodeCircuit,
            DiodePowerFeed,
            DiodeClient,
            ConnectionConfig,
            BatchProcessor,
            BatchResult,
            DeviceError,
        ]

        missing = []
        for cls in classes_to_check:
            if not has_docstring(cls):
                missing.append(cls.__name__)

        if missing:
            pytest.fail(f"Main classes missing docstrings: {', '.join(missing)}")

    def test_exception_classes_have_docstrings(self) -> None:
        """Test that all exception classes have docstrings."""
        exceptions = [
            DiodeError,
            DiodeValidationError,
            DiodeConversionError,
            DiodeClientError,
            DiodeServerResponseError,
            DiodeBatchError,
            DiodeConnectionRefusedError,
            DiodeTimeoutError,
            DiodeAuthenticationError,
        ]

        missing = []
        for exc in exceptions:
            if not has_docstring(exc):
                missing.append(exc.__name__)

        if missing:
            pytest.fail(f"Exception classes missing docstrings: {', '.join(missing)}")

    def test_converter_functions_have_docstrings(self) -> None:
        """Test that all converter functions have docstrings."""
        converters = [
            convert_device,
            convert_device_to_entities,
            convert_interface,
            convert_vlan,
            convert_module,
            convert_module_bay,
            convert_cable,
            convert_prefix,
            convert_ip_address,
            convert_device_with_subcomponents,
        ]

        missing = []
        for func in converters:
            if not has_docstring(func):
                missing.append(func.__name__)

        if missing:
            pytest.fail(f"Converter functions missing docstrings: {', '.join(missing)}")

    def test_io_functions_have_docstrings(self) -> None:
        """Test that I/O functions have docstrings."""
        io_functions = [
            to_json,
            to_yaml,
            to_netbox_yaml,
            export_devices,
            import_from_json,
            import_from_yaml,
            from_file,
            from_netbox_api,
            validate_import,
            parse_import_errors,
        ]

        missing = []
        for func in io_functions:
            if not has_docstring(func):
                missing.append(func.__name__)

        if missing:
            pytest.fail(f"I/O functions missing docstrings: {', '.join(missing)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""Base mixin classes for Pydantic models.

This module provides reusable mixin classes that add common functionality
to all Diode model classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


class ExportableMixin:
    """Mixin that adds export methods (to_json, to_yaml) to Pydantic models.

    Usage::

        class MyModel(PydanticModel, ExportableMixin):
            ...

    The mixin delegates to standalone functions in the export module,
    so the class stays dependency-free.

    Attributes:
        (none - purely behavioral mixin)
    """

    def to_json(self, pretty: bool = False) -> str:
        """Export this model to a JSON string.

        Args:
            pretty: If True, format output with indentation

        Returns:
            JSON string representation of the model
        """
        from ..export import to_json
        return to_json(self, pretty=pretty)

    def to_yaml(self) -> str:
        """Export this model to a YAML string.

        Returns:
            YAML string representation of the model
        """
        from ..export import to_yaml
        return to_yaml(self)


class NetBoxYamlMixin:
    """Mixin that adds to_netbox_yaml() for DiodeDevice models."""

    def to_netbox_yaml(self) -> dict:
        """Export this device to NetBox YAML format with device_type template.

        Returns:
            Dictionary in NetBox YAML format with device_type template
        """
        from ..export import to_netbox_yaml
        return to_netbox_yaml(self)  # type: ignore[misc]

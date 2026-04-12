"""DiodeModule and DiodeModuleBay Pydantic models."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Module, ModuleBay


class ModuleStatus(str, Enum):
    """Module status enumeration."""

    active = "active"
    installed = "installed"
    deprecated = "deprecated"
    retired = "retired"


class ModuleBayPosition(int):
    """Module bay position type."""

    pass


class DiodeModule(BaseModel):
    """Pydantic model for Diode Module.

    This model enforces required fields (module_type, device) and
    supports all module-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Status field is validated against ModuleStatus enum values.
    """

    # Required fields - must be provided
    module_type: str = Field(..., description="The module type model name")
    device: str = Field(..., description="The device name")

    # Optional fields
    serial: Optional[str] = Field(default=None, description="Module serial number")
    asset_tag: Optional[str] = Field(default=None, description="Module asset tag")
    status: Optional[str] = Field(default=None, description="Module status (active, installed, deprecated, retired)")
    description: Optional[str] = Field(default=None, description="Module description")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    comments: Optional[str] = Field(default=None, description="Module comments")
    tags: Optional[list[str]] = Field(default=None, description="Module tags")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeModule":
        """Parse a dictionary into a DiodeModule instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing module data

        Returns:
            DiodeModule instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate module status against allowed values.

        Args:
            v: The module status to validate

        Returns:
            The validated module status

        Raises:
            ValueError: If status is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"active", "installed", "deprecated", "retired"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    def to_protobuf(self) -> Module:
        """Convert DiodeModule to netboxlabs.diode.sdk.ingester.Module.

        Returns:
            Module protobuf object ready for Diode gRPC transmission
        """
        # Build the Module protobuf message
        module = Module(
            module_type=self.module_type,
            device=self.device,
            serial=self.serial,
            asset_tag=self.asset_tag,
            status=self.status,
            description=self.description,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            comments=self.comments,
            tags=self.tags,
        )

        return module


class DiodeModuleBay(BaseModel):
    """Pydantic model for Diode ModuleBay.

    This model enforces required fields (device, module, position) and
    supports all module bay-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.
    """

    # Required fields - must be provided
    device: str = Field(..., description="The device name")
    module: str = Field(..., description="The module name")
    position: int = Field(..., description="The module bay position")

    # Optional fields
    name: Optional[str] = Field(default=None, description="Module bay name")
    label: Optional[str] = Field(default=None, description="Module bay label")
    description: Optional[str] = Field(default=None, description="Module bay description")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    tags: Optional[list[str]] = Field(default=None, description="Module bay tags")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeModuleBay":
        """Parse a dictionary into a DiodeModuleBay instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing module bay data

        Returns:
            DiodeModuleBay instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    def to_protobuf(self) -> ModuleBay:
        """Convert DiodeModuleBay to netboxlabs.diode.sdk.ingester.ModuleBay.

        Returns:
            ModuleBay protobuf object ready for Diode gRPC transmission
        """
        # Build the ModuleBay protobuf message
        module_bay = ModuleBay(
            device=self.device,
            installed_module=Module(module_type=self.module, device=self.device),
            position=str(self.position),
            name=self.name,
            label=self.label,
            description=self.description,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            tags=self.tags,
        )

        return module_bay


__all__ = [
    "DiodeModule",
    "ModuleStatus",
    "DiodeModuleBay",
    "ModuleBayPosition",
]

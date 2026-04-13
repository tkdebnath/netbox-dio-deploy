"""DiodeCable Pydantic model for cable relationships."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Cable, GenericObject, Device, Interface


class CableType(str, Enum):
    """Cable type enumeration."""

    cat5e = "cat5e"
    cat6 = "cat6"
    cat6a = "cat6a"
    cat7 = "cat7"
    fiber = "fiber"
    coaxial = "coaxial"
    power = "power"
    other = "other"


class CableStatus(str, Enum):
    """Cable status enumeration."""

    active = "active"
    planned = "planned"
    decommissioned = "decommissioned"
    available = "available"


class TerminationPoint(BaseModel):
    """Pydantic model for a single cable termination point.

    Represents one end of a cable connection.
    Can terminate to: device, interface, module_bay, or another cable.
    """

    type: str = Field(..., description="Termination type: device, interface, module_bay, or cable")
    id: str = Field(..., description="Termination identifier (name or ID)")
    device_name: Optional[str] = Field(default=None, description="Device name for interface/module_bay terminations")
    cable_end: str = Field(default="A", description="Cable end identifier (A or B)")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate termination type."""
        allowed = {"device", "interface", "module_bay", "cable"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @field_validator("cable_end")
    @classmethod
    def validate_cable_end(cls, v: str) -> str:
        """Validate cable end value."""
        allowed = {"A", "B"}
        if v not in allowed:
            raise ValueError(f"cable_end must be one of {allowed}")
        return v


class DiodeCable(BaseModel):
    """Pydantic model for Diode Cable.

    This model wraps the SDK's Cable protobuf for easier construction.
    Required fields: label, device_a, device_b, type

    Note: In the SDK, Cable.a_terminations and Cable.b_terminations are
          lists of GenericObject. We simplify this to single device references.
    """

    # Required fields - must be provided
    label: str = Field(..., description="Cable label")
    device_a: str = Field(..., description="Device A name (termination point A)")
    device_b: str = Field(..., description="Device B name (termination point B)")
    type: str = Field(..., description="The cable type (cat5e, cat6, cat6a, cat7, fiber, coaxial, power, other)")

    # Optional fields matching SDK Cable
    status: Optional[str] = Field(default=None, description="Cable status (active, planned, decommissioned, available)")
    tenant: Optional[str] = Field(default=None, description="Tenant")
    color: Optional[str] = Field(default=None, description="Color")
    length: Optional[float] = Field(default=None, description="Length")
    length_unit: Optional[str] = Field(default=None, description="Length unit")
    description: Optional[str] = Field(default=None, description="Description")
    comments: Optional[str] = Field(default=None, description="Comments")
    tags: Optional[list[str]] = Field(default=None, description="Tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom fields")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    profile: Optional[str] = Field(default=None, description="Profile")

    @model_validator(mode="after")
    def validate_device_names(self):
        """Ensure device_a and device_b are non-empty."""
        if not self.device_a:
            raise ValueError("device_a is required")
        if not self.device_b:
            raise ValueError("device_b is required")
        return self

    @field_validator("type")
    @classmethod
    def validate_cable_type(cls, v: str) -> str:
        """Validate cable type."""
        allowed = {"cat5e", "cat6", "cat6a", "cat7", "fiber", "coaxial", "power", "other"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @field_validator("status")
    @classmethod
    def validate_cable_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate cable status."""
        if v is None:
            return v
        allowed = {"active", "planned", "decommissioned", "available"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeCable":
        """Parse a dictionary into a DiodeCable instance.

        Args:
            data: Dictionary containing cable data

        Returns:
            DiodeCable instance with validated data
        """
        return cls.model_validate(data)

    def to_protobuf(self) -> Cable:
        """Convert DiodeCable to netboxlabs.diode.sdk.ingester.Cable.

        Returns:
            Cable protobuf object ready for Diode gRPC transmission
        """
        # Create GenericObjects for A and B terminations pointing to devices
        go_a = GenericObject(object_device=Device(name=self.device_a))
        go_b = GenericObject(object_device=Device(name=self.device_b))

        # Build the Cable protobuf message matching SDK expectations
        return Cable(
            label=self.label,
            type=self.type,
            a_terminations=[go_a],
            b_terminations=[go_b],
            status=self.status,
            tenant=self.tenant,
            color=self.color,
            length=self.length,
            length_unit=self.length_unit,
            description=self.description,
            comments=self.comments,
            tags=self.tags,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            profile=self.profile,
        )


__all__ = [
    "DiodeCable",
    "CableType",
    "CableStatus",
    "TerminationPoint",
]

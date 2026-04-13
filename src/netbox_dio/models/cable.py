"""DiodeCable Pydantic model for cable relationships."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from netboxlabs.diode.sdk.ingester import Cable


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


class CableTerminationPointType(str, Enum):
    """Cable termination point type enumeration."""

    device = "device"
    interface = "interface"
    module_bay = "module_bay"
    cable = "cable"


class CableTerminationPoint(BaseModel):
    """Pydantic model for Cable Termination Point.

    Represents one end of a cable termination.
    """

    termination_type: str = Field(..., description="The termination type (device, interface, module_bay, cable)")
    termination_id: str = Field(..., description="The termination object identifier")
    cable_end: str = Field(..., description="The cable end (A or B)")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "CableTerminationPoint":
        """Parse a dictionary into a CableTerminationPoint instance."""
        return cls.model_validate(data)

    @field_validator("termination_type")
    @classmethod
    def validate_termination_type(cls, v: str) -> str:
        """Validate termination type against allowed values."""
        allowed = {"device", "interface", "module_bay", "cable"}
        if v not in allowed:
            raise ValueError(f"termination_type must be one of {allowed}")
        return v

    @field_validator("cable_end")
    @classmethod
    def validate_cable_end(cls, v: str) -> str:
        """Validate cable end against allowed values."""
        allowed = {"A", "B"}
        if v not in allowed:
            raise ValueError(f"cable_end must be one of {allowed}")
        return v


class DiodeCable(BaseModel):
    """Pydantic model for Diode Cable.

    This model enforces required fields (a_terminations, b_terminations, type) and
    supports all cable-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.
    """

    # Required fields - must be provided
    termination_a_type: str = Field(..., description="Type of the first termination point")
    termination_a_id: str = Field(..., description="ID of the first termination point")
    termination_b_type: str = Field(..., description="Type of the second termination point")
    termination_b_id: str = Field(..., description="ID of the second termination point")
    device_a_name: Optional[str] = Field(default=None, description="Name of the device for termination A, required if termination_type is 'interface'")
    device_b_name: Optional[str] = Field(default=None, description="Name of the device for termination B, required if termination_type is 'interface'")
    type: str = Field(..., description="The cable type (cat5e, cat6, cat6a, cat7, fiber, coaxial, power, other)")

    # Optional fields
    status: Optional[str] = Field(default=None, description="Cable status (active, planned, decommissioned, available)")
    tenant: Optional[str] = Field(default=None, description="Tenant name")
    label: Optional[str] = Field(default=None, description="Cable label")
    color: Optional[str] = Field(default=None, description="Cable color")
    length: Optional[float] = Field(default=None, description="Cable length")
    length_unit: Optional[str] = Field(default=None, description="Cable length unit (m, ft)")
    description: Optional[str] = Field(default=None, description="Cable description")
    comments: Optional[str] = Field(default=None, description="Cable comments")
    tags: Optional[list[str]] = Field(default=None, description="Cable tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    profile: Optional[str] = Field(default=None, description="Cable profile")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeCable":
        """Parse a dictionary into a DiodeCable instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing cable data

        Returns:
            DiodeCable instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate cable type against allowed values.

        Args:
            v: The cable type to validate

        Returns:
            The validated cable type

        Raises:
            ValueError: If type is not one of the allowed values
        """
        allowed = {"cat5e", "cat6", "cat6a", "cat7", "fiber", "coaxial", "power", "other"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate cable status against allowed values.

        Args:
            v: The cable status to validate

        Returns:
            The validated cable status

        Raises:
            ValueError: If status is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"active", "planned", "decommissioned", "available"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    def to_protobuf(self) -> Cable:
        """Convert DiodeCable to netboxlabs.diode.sdk.ingester.Cable.

        Returns:
            Cable protobuf object ready for Diode gRPC transmission
        """
        from netboxlabs.diode.sdk.ingester import GenericObject, Interface, Device, Module, ModuleBay

        # Helper function to create a GenericObject with the appropriate object field
        def create_generic_object(term: CableTerminationPoint, device_name: str) -> GenericObject:
            """Create a GenericObject with the appropriate object field set."""
            go = GenericObject()

            if term.termination_type == "interface":
                # Interface requires: name, device, type
                # The device field expects a Device message
                device = Device(name=device_name)
                iface = Interface(name=term.termination_id, device=device, type="physical")
                go.object_interface.CopyFrom(iface)
            elif term.termination_type == "device":
                # Device requires: name, device_type, role, site
                dev = Device(name=term.termination_id, device_type="cisco-9300", role="core-router", site="site-a")
                go.object_device.CopyFrom(dev)
            elif term.termination_type == "module_bay":
                # ModuleBay requires: device, module, position
                mb = ModuleBay(device=device_name, module=term.termination_id, position=1)
                go.object_module_bay.CopyFrom(mb)
            elif term.termination_type == "cable":
                # Cable requires: type, a_terminations, b_terminations
                cable = Cable(type=term.termination_id)
                go.object_cable.CopyFrom(cable)

            return go

        # Convert termination points to GenericObjects
        a_term_pb = []
        for term in self.a_terminations:
            device_name = term.termination_id if term.termination_type == "device" else self.a_terminations[0].termination_id
            go = create_generic_object(term, device_name)
            a_term_pb.append(go)

        b_term_pb = []
        for term in self.b_terminations:
            device_name = term.termination_id if term.termination_type == "device" else self.b_terminations[0].termination_id
            go = create_generic_object(term, device_name)
            b_term_pb.append(go)

        # Build the Cable protobuf message
        cable = Cable(
            type=self.type,
            a_terminations=a_term_pb,
            b_terminations=b_term_pb,
            status=self.status,
            tenant=self.tenant,
            label=self.label,
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

        return cable


__all__ = [
    "DiodeCable",
    "CableType",
    "CableStatus",
    "CableTerminationPoint",
    "CableTerminationPointType",
]

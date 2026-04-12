"""DiodeVLAN Pydantic model with VLAN assignment fields."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import VLAN


class VLANStatus(str, Enum):
    """VLAN status enumeration."""

    active = "active"
    reserved = "reserved"
    deprecated = "deprecated"


class VLANRole(str, Enum):
    """VLAN role enumeration."""

    access = "access"
    distribution = "distribution"
    core = "core"
    other = "other"


class VLANGroup(str, Enum):
    """VLAN group enumeration."""

    access = "access"
    distribution = "distribution"
    core = "core"
    other = "other"


class DiodeVLAN(BaseModel):
    """Pydantic model for Diode VLAN with VLAN assignment fields.

    This model enforces required fields (name, vid, site) and
    supports all VLAN-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Status field is validated against VLANStatus enum values.
    Role field is validated against VLANRole enum values.
    """

    # Required fields - must be provided
    name: str = Field(..., description="The VLAN name")
    vid: int = Field(..., description="The VLAN ID (1-4094)")
    site: str = Field(..., description="The site name")

    # Optional fields
    description: Optional[str] = Field(default=None, description="VLAN description")
    status: Optional[str] = Field(default=None, description="VLAN status (active, reserved, deprecated)")
    role: Optional[str] = Field(default=None, description="VLAN role (access, distribution, core, other)")
    group: Optional[str] = Field(default=None, description="VLAN group name")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    comments: Optional[str] = Field(default=None, description="VLAN comments")
    tags: Optional[list[str]] = Field(default=None, description="VLAN tags")
    tenant: Optional[str] = Field(default=None, description="Tenant name")
    qinq_role: Optional[str] = Field(default=None, description="Q-in-Q role")
    qinq_svlan: Optional[int] = Field(default=None, description="Q-in-Q SVLAN ID")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeVLAN":
        """Parse a dictionary into a DiodeVLAN instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing VLAN data

        Returns:
            DiodeVLAN instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate VLAN status against allowed values.

        Args:
            v: The VLAN status to validate

        Returns:
            The validated VLAN status

        Raises:
            ValueError: If status is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"active", "reserved", "deprecated"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate VLAN role against allowed values.

        Args:
            v: The VLAN role to validate

        Returns:
            The validated VLAN role

        Raises:
            ValueError: If role is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"access", "distribution", "core", "other"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v

    @field_validator("vid")
    @classmethod
    def validate_vid(cls, v: int) -> int:
        """Validate VLAN ID against allowed range.

        Args:
            v: The VLAN ID to validate

        Returns:
            The validated VLAN ID

        Raises:
            ValueError: If VLAN ID is not in valid range (1-4094)
        """
        if v < 1 or v > 4094:
            raise ValueError(f"vid must be between 1 and 4094, got {v}")
        return v

    def to_protobuf(self) -> VLAN:
        """Convert DiodeVLAN to netboxlabs.diode.sdk.ingester.VLAN.

        Returns:
            VLAN protobuf object ready for Diode gRPC transmission
        """
        # Build the VLAN protobuf message
        vlan = VLAN(
            name=self.name,
            vid=self.vid,
            site=self.site,
            description=self.description,
            status=self.status,
            role=self.role,
            group=self.group,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            comments=self.comments,
            tags=self.tags,
            tenant=self.tenant,
            qinq_role=self.qinq_role,
            qinq_svlan=self.qinq_svlan,
        )

        return vlan


__all__ = [
    "DiodeVLAN",
    "VLANStatus",
    "VLANRole",
    "VLANGroup",
]

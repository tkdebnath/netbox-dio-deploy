"""DiodePrefix Pydantic model for IPv4/IPv6 prefix management."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Prefix, VRF


class PrefixStatus(str, Enum):
    """Prefix status enumeration."""

    active = "active"
    reserved = "reserved"
    deprecated = "deprecated"
    available = "available"


class PrefixRole(str, Enum):
    """Prefix role enumeration."""

    network = "network"
    loopback = "loopback"
    relay = "relay"
    vrf = "vrf"
    other = "other"


class DiodePrefix(BaseModel):
    """Pydantic model for Diode Prefix.

    This model enforces required fields (prefix) and
    supports all prefix-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Status field is validated against PrefixStatus enum values.
    Role field is validated against PrefixRole enum values.
    """

    # Required fields - must be provided
    prefix: str = Field(..., description="The IP prefix in CIDR notation (e.g., 192.168.1.0/24)")

    # Optional fields
    vrf: Optional[str] = Field(default=None, description="VRF name")
    status: Optional[str] = Field(default=None, description="Prefix status (active, reserved, deprecated, available)")
    role: Optional[str] = Field(default=None, description="Prefix role (network, loopback, relay, vrf, other)")
    is_pool: Optional[bool] = Field(default=None, description="Is this prefix a pool?")
    mark_utilized: Optional[int] = Field(default=None, description="Mark as utilized at this percentage")
    description: Optional[str] = Field(default=None, description="Prefix description")
    comments: Optional[str] = Field(default=None, description="Prefix comments")
    tags: Optional[list[str]] = Field(default=None, description="Prefix tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    tenant: Optional[str] = Field(default=None, description="Tenant name")
    scope_location: Optional[str] = Field(default=None, description="Scope location name")
    scope_region: Optional[str] = Field(default=None, description="Scope region name")
    scope_site: Optional[str] = Field(default=None, description="Scope site name")
    scope_site_group: Optional[str] = Field(default=None, description="Scope site group name")
    vlan: Optional[str] = Field(default=None, description="VLAN name")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodePrefix":
        """Parse a dictionary into a DiodePrefix instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing prefix data

        Returns:
            DiodePrefix instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate prefix status against allowed values.

        Args:
            v: The prefix status to validate

        Returns:
            The validated prefix status

        Raises:
            ValueError: If status is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"active", "reserved", "deprecated", "available"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate prefix role against allowed values.

        Args:
            v: The prefix role to validate

        Returns:
            The validated prefix role

        Raises:
            ValueError: If role is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"network", "loopback", "relay", "vrf", "other"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Validate prefix format.

        Args:
            v: The prefix string to validate

        Returns:
            The validated prefix string

        Raises:
            ValueError: If prefix format is invalid
        """
        # Basic IPv4/IPv6 prefix validation using regex
        import re

        # IPv4 CIDR pattern
        ipv4_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
        # IPv6 CIDR pattern (simplified)
        ipv6_pattern = r"^[0-9a-fA-F:]+/\d{1,3}$"

        if not re.match(ipv4_pattern, v) and not re.match(ipv6_pattern, v):
            raise ValueError(f"prefix must be in CIDR notation (e.g., 192.168.1.0/24 or 2001:db8::/32)")
        return v

    def to_protobuf(self) -> Prefix:
        """Convert DiodePrefix to netboxlabs.diode.sdk.ingester.Prefix.

        Returns:
            Prefix protobuf object ready for Diode gRPC transmission
        """
        # Convert string references to VRF objects where needed
        vrf_obj = None
        if self.vrf:
            vrf_obj = VRF(name=self.vrf)

        # Build the Prefix protobuf message
        prefix = Prefix(
            prefix=self.prefix,
            vrf=vrf_obj,
            status=self.status,
            role=self.role,
            is_pool=self.is_pool,
            mark_utilized=self.mark_utilized,
            description=self.description,
            comments=self.comments,
            tags=self.tags,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            tenant=self.tenant,
            scope_location=self.scope_location,
            scope_region=self.scope_region,
            scope_site=self.scope_site,
            scope_site_group=self.scope_site_group,
            vlan=self.vlan,
        )

        return prefix


__all__ = [
    "DiodePrefix",
    "PrefixStatus",
    "PrefixRole",
]

"""DiodeIPAddress Pydantic model for IP assignment."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import IPAddress, VRF


class IPAddressStatus(str, Enum):
    """IP address status enumeration."""

    active = "active"
    reserved = "reserved"
    deprecated = "deprecated"
    available = "available"
    deny = "deny"


class IPAddressRole(str, Enum):
    """IP address role enumeration."""

    loopback = "loopback"
    secondary = "secondary"
    anycast = "anycast"
    vip = "vip"
    vrrp = "vrrp"
    haproxy = "haproxy"
    other = "other"


class DiodeIPAddress(BaseModel):
    """Pydantic model for Diode IP Address.

    This model enforces required fields (address) and
    supports all IP address-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Status field is validated against IPAddressStatus enum values.
    Role field is validated against IPAddressRole enum values.
    """

    # Required fields - must be provided
    address: str = Field(..., description="The IP address in CIDR notation (e.g., 192.168.1.1/24)")

    # Optional fields
    vrf: Optional[str] = Field(default=None, description="VRF name")
    tenant: Optional[str] = Field(default=None, description="Tenant name")
    status: Optional[str] = Field(default=None, description="IP address status (active, reserved, deprecated, available, deny)")
    role: Optional[str] = Field(default=None, description="IP address role (loopback, secondary, anycast, vip, vrrp, haproxy, other)")
    dns_name: Optional[str] = Field(default=None, description="DNS name for the IP address")
    description: Optional[str] = Field(default=None, description="IP address description")
    comments: Optional[str] = Field(default=None, description="IP address comments")
    tags: Optional[list[str]] = Field(default=None, description="IP address tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    assigned_object_fhrp_group: Optional[str] = Field(default=None, description="FHRP group name")
    assigned_object_interface: Optional[str] = Field(default=None, description="Assigned interface name")
    assigned_object_vm_interface: Optional[str] = Field(default=None, description="Assigned VM interface name")
    nat_inside: Optional[str] = Field(default=None, description="NAT inside IP address")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeIPAddress":
        """Parse a dictionary into a DiodeIPAddress instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing IP address data

        Returns:
            DiodeIPAddress instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address status against allowed values.

        Args:
            v: The IP address status to validate

        Returns:
            The validated IP address status

        Raises:
            ValueError: If status is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"active", "reserved", "deprecated", "available", "deny"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address role against allowed values.

        Args:
            v: The IP address role to validate

        Returns:
            The validated IP address role

        Raises:
            ValueError: If role is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"loopback", "secondary", "anycast", "vip", "vrrp", "haproxy", "other"}
        if v not in allowed:
            raise ValueError(f"role must be one of {allowed}")
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate IP address format.

        Args:
            v: The IP address string to validate

        Returns:
            The validated IP address string

        Raises:
            ValueError: If address format is invalid
        """
        # Basic IPv4/IPv6 address validation using regex
        import re

        # IPv4 CIDR pattern
        ipv4_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
        # IPv6 CIDR pattern (simplified)
        ipv6_pattern = r"^[0-9a-fA-F:]+/\d{1,3}$"

        if not re.match(ipv4_pattern, v) and not re.match(ipv6_pattern, v):
            raise ValueError(f"address must be in CIDR notation (e.g., 192.168.1.1/24 or 2001:db8::1/64)")
        return v

    def to_protobuf(self) -> IPAddress:
        """Convert DiodeIPAddress to netboxlabs.diode.sdk.ingester.IPAddress.

        Returns:
            IPAddress protobuf object ready for Diode gRPC transmission
        """
        # Convert string references to VRF objects where needed
        vrf_obj = None
        if self.vrf:
            vrf_obj = VRF(name=self.vrf)

        # Build the IPAddress protobuf message
        ip = IPAddress(
            address=self.address,
            vrf=vrf_obj,
            tenant=self.tenant,
            status=self.status,
            role=self.role,
            dns_name=self.dns_name,
            description=self.description,
            comments=self.comments,
            tags=self.tags,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            assigned_object_fhrp_group=self.assigned_object_fhrp_group,
            assigned_object_interface=self.assigned_object_interface,
            assigned_object_vm_interface=self.assigned_object_vm_interface,
            nat_inside=self.nat_inside,
        )

        return ip


__all__ = [
    "DiodeIPAddress",
    "IPAddressStatus",
    "IPAddressRole",
]

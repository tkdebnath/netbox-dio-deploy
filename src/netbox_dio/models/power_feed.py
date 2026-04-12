"""DiodePowerFeed Pydantic model for power feeds."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import PowerFeed


class DiodePowerFeed(BaseModel):
    """Pydantic model for Diode PowerFeed.

    This model represents a power feed with required fields (name, power_panel)
    and supports all power feed-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Validation rules:
    - voltage: 100-600
    - amperage: 1-500
    - phase: single-phase, 2-phase, 3-phase
    """

    # Required fields - must be provided
    name: str = Field(..., description="Power feed name")
    power_panel: str = Field(..., description="Reference to PowerPanel")

    # Optional fields
    phase: Optional[str] = Field(default=None, description="Phase type")
    supply: Optional[str] = Field(default=None, description="Supply type (ac, dc)")
    voltage: Optional[int] = Field(default=None, description="Voltage (100-600V)")
    amperage: Optional[int] = Field(default=None, description="Amperage (1-500A)")
    capacity: Optional[int] = Field(default=None, description="Capacity in kVA")
    rack: Optional[str] = Field(default=None, description="Rack reference")
    status: Optional[str] = Field(default=None, description="Power feed status")
    description: Optional[str] = Field(default=None, description="Power feed description")
    comments: Optional[str] = Field(default=None, description="Power feed comments")
    tags: Optional[list[str]] = Field(default=None, description="Power feed tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    mark_connected: Optional[bool] = Field(default=None, description="Mark as connected")
    max_utilization: Optional[int] = Field(default=None, description="Maximum utilization percentage")
    tenant: Optional[str] = Field(default=None, description="Tenant reference")
    type: Optional[str] = Field(default=None, description="Power feed type")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodePowerFeed":
        """Parse a dictionary into a DiodePowerFeed instance.

        Args:
            data: Dictionary containing power feed data

        Returns:
            DiodePowerFeed instance with validated data
        """
        return cls.model_validate(data)

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        """Validate power feed name length (1-64 characters).

        Args:
            v: The power feed name to validate

        Returns:
            The validated name

        Raises:
            ValueError: If name length is invalid
        """
        if not v:
            raise ValueError("Power feed name cannot be empty")
        if len(v) < 1:
            raise ValueError("Power feed name is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"Power feed name exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("power_panel")
    @classmethod
    def validate_power_panel_length(cls, v: str) -> str:
        """Validate power panel reference length (1-64 characters).

        Args:
            v: The power panel reference to validate

        Returns:
            The validated reference

        Raises:
            ValueError: If reference length is invalid
        """
        if not v:
            raise ValueError("Power panel reference cannot be empty")
        if len(v) < 1:
            raise ValueError("Power panel reference is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"Power panel reference exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("voltage")
    @classmethod
    def validate_voltage(cls, v: Optional[int]) -> Optional[int]:
        """Validate voltage is in valid range (100-600).

        Args:
            v: The voltage value to validate

        Returns:
            The validated voltage

        Raises:
            ValueError: If voltage is out of range
        """
        if v is None:
            return v
        if v < 100:
            raise ValueError(f"voltage must be at least 100 (got {v})")
        if v > 600:
            raise ValueError(f"voltage exceeds maximum of 600 (got {v})")
        return v

    @field_validator("amperage")
    @classmethod
    def validate_amperage(cls, v: Optional[int]) -> Optional[int]:
        """Validate amperage is in valid range (1-500).

        Args:
            v: The amperage value to validate

        Returns:
            The validated amperage

        Raises:
            ValueError: If amperage is out of range
        """
        if v is None:
            return v
        if v < 1:
            raise ValueError(f"amperage must be positive (got {v})")
        if v > 500:
            raise ValueError(f"amperage exceeds maximum of 500 (got {v})")
        return v

    @field_validator("phase")
    @classmethod
    def validate_phase(cls, v: Optional[str]) -> Optional[str]:
        """Validate phase type.

        Args:
            v: The phase value to validate

        Returns:
            The validated phase

        Raises:
            ValueError: If phase is not valid
        """
        if v is None:
            return v
        allowed = {"single-phase", "2-phase", "3-phase"}
        if v not in allowed:
            raise ValueError(f"phase must be one of {allowed} (got {v})")
        return v

    def to_protobuf(self) -> PowerFeed:
        """Convert DiodePowerFeed to netboxlabs.diode.sdk.ingester.PowerFeed.

        Returns:
            PowerFeed protobuf object ready for Diode gRPC transmission
        """
        power_feed_args = {
            "name": self.name,
            "power_panel": self.power_panel,
        }
        if self.phase:
            power_feed_args["phase"] = self.phase
        if self.supply:
            power_feed_args["supply"] = self.supply
        if self.voltage is not None:
            power_feed_args["voltage"] = self.voltage
        if self.amperage is not None:
            power_feed_args["amperage"] = self.amperage
        if self.rack:
            power_feed_args["rack"] = self.rack
        if self.status:
            power_feed_args["status"] = self.status
        if self.description:
            power_feed_args["description"] = self.description
        if self.comments:
            power_feed_args["comments"] = self.comments
        if self.tags:
            power_feed_args["tags"] = self.tags
        if self.custom_fields:
            power_feed_args["custom_fields"] = self.custom_fields
        if self.metadata:
            power_feed_args["metadata"] = self.metadata
        if self.owner:
            power_feed_args["owner"] = self.owner
        if self.mark_connected is not None:
            power_feed_args["mark_connected"] = self.mark_connected
        if self.max_utilization is not None:
            power_feed_args["max_utilization"] = self.max_utilization
        if self.tenant:
            power_feed_args["tenant"] = self.tenant
        if self.type:
            power_feed_args["type"] = self.type

        return PowerFeed(**power_feed_args)


__all__ = ["DiodePowerFeed"]

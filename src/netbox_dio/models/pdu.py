"""DiodePDU Pydantic model with PowerPanel support.

Note: The Diode SDK's PowerPanel protobuf has limited fields (name, site, description, etc.).
Power-specific attributes like amperage, voltage, phase are on PowerFeed.
This model represents the PDU as PowerPanel with associated PowerFeeds/outlets.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from netboxlabs.diode.sdk.ingester import PowerPanel, PowerFeed, PowerOutlet


class DiodePowerOutlet(BaseModel):
    """Pydantic model for Diode PowerOutlet (representing PDU outlets).

    Represents individual power outlets on a PDU.
    """

    # Required fields
    name: str = Field(..., description="Power outlet name")
    device: str = Field(..., description="Parent device reference")
    type: str = Field(..., description="Outlet type (e.g., iec-309, l14-30)")

    # Optional fields
    serial: Optional[str] = Field(default=None, description="Outlet serial number")
    asset_tag: Optional[str] = Field(default=None, description="Outlet asset tag")
    status: Optional[str] = Field(default=None, description="Outlet status")
    power_port: Optional[str] = Field(default=None, description="Parent power port")
    feed_leg: Optional[str] = Field(default=None, description="Circuit leg (A, B, C)")
    color: Optional[str] = Field(default=None, description="Outlet color code")
    description: Optional[str] = Field(default=None, description="Outlet description")
    comments: Optional[str] = Field(default=None, description="Outlet comments")
    tags: Optional[list[str]] = Field(default=None, description="Outlet tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodePowerOutlet":
        """Parse a dictionary into a DiodePowerOutlet instance.

        Args:
            data: Dictionary containing power outlet data

        Returns:
            DiodePowerOutlet instance with validated data
        """
        return cls.model_validate(data)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate outlet type.

        Args:
            v: The outlet type to validate

        Returns:
            The validated type

        Raises:
            ValueError: If type is invalid
        """
        # Standard IEC and NEMA outlet types
        allowed = {
            "iec-309", "iec-309-1p", "iec-309-3p", "l5-30", "l5-20", "l6-30", "l6-20",
            "l14-30", "l14-20", "l21-30", "l21-20", "cmx6100", "cmx6200", "hardwired",
            "nema-5-15", "nema-5-20", "nema-6-15", "nema-6-20", "nema-l5-30", "nema-l6-30",
            "c13", "c19", "c14", "c20", "schuko", "British_Standard", "Italian_Place",
            "Swiss_127V", "Brazila_127V", "Brazila_220V", "Australian_240V"
        }
        if v not in allowed:
            raise ValueError(f"type must be a valid outlet type (got {v})")
        return v


class DiodePDU(BaseModel):
    """Pydantic model for Diode PDU (Power Distribution Unit).

    This model represents a PDU as a PowerPanel with associated PowerFeeds/outlets.
    Enforces required fields (name, site) and supports all PDU-level attributes.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Validation rules:
    - amperage: 1-500
    - voltage: 100-600
    - phase: single-phase, 2-phase, 3-phase
    """

    # Required fields - must be provided
    name: str = Field(..., description="PDU name")
    site: str = Field(..., description="Site name")

    # Optional fields for PowerPanel (Diode SDK PowerPanel has limited fields)
    description: Optional[str] = Field(default=None, description="PDU description")
    status: Optional[str] = Field(default=None, description="PDU status")
    location: Optional[str] = Field(default=None, description="Location within site")
    comments: Optional[str] = Field(default=None, description="PDU comments")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    tags: Optional[list[str]] = Field(default=None, description="PDU tags")

    # Power-specific attributes (mapped to PowerFeed in Diode SDK)
    # These are stored for the converter to use
    amperage: Optional[int] = Field(default=None, description="Maximum amperage")
    phase: Optional[str] = Field(default=None, description="Phase type")
    voltage: Optional[int] = Field(default=None, description="Voltage rating")

    # Optional list of outlets (PowerFeeds)
    outlets: Optional[List[DiodePowerOutlet]] = Field(default=None, description="Power outlets")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodePDU":
        """Parse a dictionary into a DiodePDU instance.

        Args:
            data: Dictionary containing PDU data

        Returns:
            DiodePDU instance with validated data
        """
        return cls.model_validate(data)

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        """Validate PDU name length (1-64 characters).

        Args:
            v: The PDU name to validate

        Returns:
            The validated name

        Raises:
            ValueError: If name length is invalid
        """
        if not v:
            raise ValueError("PDU name cannot be empty")
        if len(v) < 1:
            raise ValueError("PDU name is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"PDU name exceeds maximum length of 64 characters (got {len(v)})")
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

    def to_protobuf(self) -> PowerPanel:
        """Convert DiodePDU to netboxlabs.diode.sdk.ingester.PowerPanel.

        Returns:
            PowerPanel protobuf object ready for Diode gRPC transmission
        """
        # PowerPanel in Diode SDK only accepts: name, site, description, comments,
        # custom_fields, metadata, owner, tags
        power_panel_args = {
            "name": self.name,
            "site": self.site,
        }
        if self.description:
            power_panel_args["description"] = self.description
        if self.comments:
            power_panel_args["comments"] = self.comments
        if self.custom_fields:
            power_panel_args["custom_fields"] = self.custom_fields
        if self.metadata:
            power_panel_args["metadata"] = self.metadata
        if self.owner:
            power_panel_args["owner"] = self.owner
        if self.tags:
            power_panel_args["tags"] = self.tags

        return PowerPanel(**power_panel_args)


__all__ = ["DiodePDU", "DiodePowerOutlet"]

"""DiodeRack Pydantic model with validation for rack infrastructure."""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from netboxlabs.diode.sdk.ingester import Rack


class DiodeRack(BaseModel):
    """Pydantic model for Diode Rack with mandatory field validation.

    This model enforces required fields (name, site, rack_type) on initialization
    and supports all rack-level attributes defined in the NetBox Diode SDK.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    SDK Field Mapping (all fields from netboxlabs.diode.sdk.ingester.Rack):
    - name: str (REQUIRED) - The rack name
    - facility_id: str (optional) - Rack facility ID
    - site: str | Site (REQUIRED) - Site this rack belongs to
    - location: str | Location (optional) - Location within site
    - tenant: str | Tenant (optional) - Tenant owning the rack
    - status: str (optional) - Rack status
    - role: str | RackRole (optional) - Rack role reference
    - serial: str (optional) - Rack serial number
    - asset_tag: str (optional) - Rack asset tag
    - rack_type: str | RackType (REQUIRED) - Rack type model name
    - form_factor: str (optional) - Rack form factor
    - width: int (optional) - Rack width in mm
    - u_height: int (optional) - Height in U positions
    - starting_unit: int (optional) - Starting unit number (1 or 48)
    - weight: float (optional) - Weight of installed equipment
    - max_weight: int (optional) - Maximum rack weight capacity
    - weight_unit: str (optional) - Weight unit
    - desc_units: bool (optional) - Whether units count downward
    - outer_width: int (optional) - Outer frame width
    - outer_depth: int (optional) - Outer frame depth
    - outer_unit: str (optional) - Outer dimensions unit
    - mounting_depth: int (optional) - Mounting depth in mm
    - airflow: str (optional) - Airflow direction
    - description: str (optional) - Rack description
    - comments: str (optional) - Rack comments
    - tags: list[str] (optional) - Rack tags
    - custom_fields: dict (optional) - Custom field values
    - outer_height: int (optional) - Outer frame height
    - metadata: dict (optional) - Additional metadata
    - owner: str (optional) - Owner reference

    The following fields are wrapper-only additions for device position tracking:
    - device_positions: list[dict] (optional) - List of device entries with position info
    """

    # Required fields - must be provided
    name: str = Field(..., description="The rack name")
    site: str = Field(..., description="The site name (parent site/container)")
    rack_type: str = Field(..., description="The rack type model name")

    # Optional fields - SDK attributes
    facility_id: Optional[str] = Field(default=None, description="Rack facility ID")
    location: Optional[str] = Field(default=None, description="Location within site")
    tenant: Optional[str] = Field(default=None, description="Tenant reference")
    status: Optional[str] = Field(default=None, description="Rack status")
    role: Optional[str] = Field(default=None, description="Rack role")
    serial: Optional[str] = Field(default=None, description="Rack serial number")
    asset_tag: Optional[str] = Field(default=None, description="Rack asset tag")
    form_factor: Optional[str] = Field(default=None, description="Rack form factor")
    width: Optional[int] = Field(default=None, description="Rack width in mm")
    u_height: Optional[int] = Field(default=None, description="Height available in U positions")
    starting_unit: Optional[int] = Field(default=None, description="Starting unit number")
    weight: Optional[float] = Field(default=None, description="Weight of equipment")
    max_weight: Optional[int] = Field(default=None, description="Maximum weight capacity")
    weight_unit: Optional[str] = Field(default=None, description="Weight unit")
    desc_units: Optional[bool] = Field(default=None, description="Units count downward")
    outer_width: Optional[int] = Field(default=None, description="Outer frame width")
    outer_depth: Optional[int] = Field(default=None, description="Outer frame depth")
    outer_unit: Optional[str] = Field(default=None, description="Outer dimension unit")
    mounting_depth: Optional[int] = Field(default=None, description="Mounting depth in mm")
    airflow: Optional[str] = Field(default=None, description="Airflow direction")
    description: Optional[str] = Field(default=None, description="Rack description")
    comments: Optional[str] = Field(default=None, description="Rack comments")
    tags: Optional[list[str]] = Field(default=None, description="Rack tags")
    custom_fields: Optional[dict[str, Any]] = Field(default=None, description="Custom field values")
    outer_height: Optional[int] = Field(default=None, description="Outer frame height")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner reference")

    # Wrapper-only fields (not in SDK) - used for device position tracking
    device_positions: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="List of device positions within this rack for tracking (wrapper-only, not sent to SDK)",
    )

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeRack":
        """Parse a dictionary into a DiodeRack instance.

        Args:
            data: Dictionary containing rack data

        Returns:
            DiodeRack instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        """Validate rack name length (1-64 characters).

        Args:
            v: The rack name to validate

        Returns:
            The validated name

        Raises:
            ValueError: If name length is invalid
        """
        if not v:
            raise ValueError("Rack name cannot be empty")
        if len(v) < 1:
            raise ValueError("Rack name is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"Rack name exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("rack_type")
    @classmethod
    def validate_rack_type_length(cls, v: str) -> str:
        """Validate rack type length (1-64 characters).

        Args:
            v: The rack type to validate

        Returns:
            The validated type

        Raises:
            ValueError: If type length is invalid
        """
        if not v:
            raise ValueError("Rack type cannot be empty")
        if len(v) > 64:
            raise ValueError(f"Rack type exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("serial")
    @classmethod
    def validate_serial_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate serial number length (0-64 characters).

        Args:
            v: The serial number to validate

        Returns:
            The validated serial number
        """
        if v is None:
            return v
        if len(v) > 64:
            raise ValueError(f"Serial number exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("asset_tag")
    @classmethod
    def validate_asset_tag_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate asset tag length (0-64 characters).

        Args:
            v: The asset tag to validate

        Returns:
            The validated asset tag
        """
        if v is None:
            return v
        if len(v) > 64:
            raise ValueError(f"Asset tag exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("u_height")
    @classmethod
    def validate_u_height(cls, v: Optional[int]) -> Optional[int]:
        """Validate u_height is a positive integer (1-100).

        Args:
            v: The u_height value to validate

        Returns:
            The validated u_height

        Raises:
            ValueError: If u_height is not positive or exceeds 100
        """
        if v is None:
            return v
        if v < 1:
            raise ValueError(f"u_height must be positive (got {v})")
        if v > 100:
            raise ValueError(f"u_height exceeds maximum of 100 (got {v})")
        return v

    @field_validator("starting_unit")
    @classmethod
    def validate_starting_unit(cls, v: Optional[int]) -> Optional[int]:
        """Validate starting_unit is 1 or 48.

        Args:
            v: The starting_unit value to validate

        Returns:
            The validated starting_unit

        Raises:
            ValueError: If starting_unit is not 1 or 48
        """
        if v is None:
            return v
        if v not in {1, 48}:
            raise ValueError(f"starting_unit must be 1 or 48 (got {v})")
        return v

    def to_protobuf(self) -> Rack:
        """Convert DiodeRack to netboxlabs.diode.sdk.ingester.Rack.

        All fields are passed directly to SDK Rack constructor for type coercion.
        Wrapper-only fields (device_positions) are not transmitted.

        Returns:
            Rack protobuf object ready for Diode gRPC transmission
        """
        return Rack(
            name=self.name,
            facility_id=self.facility_id,
            site=self.site,
            location=self.location,
            tenant=self.tenant,
            status=self.status,
            role=self.role,
            serial=self.serial,
            asset_tag=self.asset_tag,
            rack_type=self.rack_type,
            form_factor=self.form_factor,
            width=self.width,
            u_height=self.u_height,
            starting_unit=self.starting_unit,
            weight=self.weight,
            max_weight=self.max_weight,
            weight_unit=self.weight_unit,
            desc_units=self.desc_units,
            outer_width=self.outer_width,
            outer_depth=self.outer_depth,
            outer_unit=self.outer_unit,
            mounting_depth=self.mounting_depth,
            airflow=self.airflow,
            description=self.description,
            comments=self.comments,
            tags=self.tags,
            custom_fields=self.custom_fields,
            outer_height=self.outer_height,
            metadata=self.metadata,
            owner=self.owner,
        )

    def get_device_positions(self) -> list[dict[str, Any]]:
        """Get device positions with rack/site/location inheritance.

        For each device position entry:
        - If 'site' or 'location' is not specified, inherit from rack

        Returns:
            List of device position entries with all fields resolved

        Example:
            >>> rack = DiodeRack(
            ...     name="rack-01",
            ...     site="dc-east",
            ...     location="building-a",
            ...     rack_type="42u",
            ...     device_positions=[
            ...         {"device": "router-01", "position": 10.0},
            ...         {"device": "switch-01", "position": 20.0, "location": "build-b"},
            ...     ],
            ... )
            >>> rack.get_device_positions()
            [
                {"device": "router-01", "position": 10.0, "site": "dc-east", "location": "building-a"},
                {"device": "switch-01", "position": 20.0, "site": "dc-east", "location": "build-b"},
            ]
        """
        if not self.device_positions:
            return []

        resolved = []
        for pos in self.device_positions:
            resolved_position = dict(pos)

            # Apply site inheritance
            if "site" not in resolved_position:
                resolved_position["site"] = self.site

            # Apply location inheritance
            if "location" not in resolved_position:
                resolved_position["location"] = self.location

            resolved.append(resolved_position)

        return resolved


__all__ = ["DiodeRack"]

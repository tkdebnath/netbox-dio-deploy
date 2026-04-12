"""DiodeRack Pydantic model with validation for rack infrastructure."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Rack


class DiodeRack(BaseModel):
    """Pydantic model for Diode Rack with mandatory field validation.

    This model enforces required fields (name, site, rack_type) on initialization
    and supports all rack-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Validation rules:
    - u_height: positive integer (1-100)
    - starting_unit: 1 or 48
    - name: 1-64 characters
    - serial/asset_tag: 0-64 characters
    """

    # Required fields - must be provided
    name: str = Field(..., description="The rack name")
    site: str = Field(..., description="The site name")
    rack_type: str = Field(..., description="The rack type (e.g., 42u, 45u)")

    # Optional fields
    serial: Optional[str] = Field(default=None, description="Rack serial number")
    asset_tag: Optional[str] = Field(default=None, description="Rack asset tag")
    role: Optional[str] = Field(default=None, description="Rack role")
    u_height: Optional[int] = Field(default=None, description="Number of RU available")
    starting_unit: Optional[int] = Field(default=None, description="Starting RU number")
    description: Optional[str] = Field(default=None, description="Rack description")
    status: Optional[str] = Field(default=None, description="Rack status")
    location: Optional[str] = Field(default=None, description="Location within site")
    airflow: Optional[str] = Field(default=None, description="Airflow direction")
    form_factor: Optional[str] = Field(default=None, description="Rack form factor")
    weight: Optional[float] = Field(default=None, description="Rack weight")
    weight_unit: Optional[str] = Field(default=None, description="Weight unit")
    mounting_depth: Optional[int] = Field(default=None, description="Mounting depth in mm")
    outer_height: Optional[int] = Field(default=None, description="Outer height")
    outer_depth: Optional[int] = Field(default=None, description="Outer depth")
    outer_width: Optional[int] = Field(default=None, description="Outer width")
    outer_unit: Optional[str] = Field(default=None, description="Dimension unit")
    max_weight: Optional[float] = Field(default=None, description="Maximum weight capacity")
    desc_units: Optional[bool] = Field(default=None, description="Whether units are top-to-bottom")
    comments: Optional[str] = Field(default=None, description="Rack comments")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    tags: Optional[list[str]] = Field(default=None, description="Rack tags")
    tenant: Optional[str] = Field(default=None, description="Tenant reference")
    facility_id: Optional[str] = Field(default=None, description="Facility ID")
    width: Optional[int] = Field(default=None, description="Rack width")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeRack":
        """Parse a dictionary into a DiodeRack instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

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

        Returns:
            Rack protobuf object ready for Diode gRPC transmission
        """
        return Rack(
            name=self.name,
            site=self.site,
            rack_type=self.rack_type,
            serial=self.serial,
            asset_tag=self.asset_tag,
            role=self.role,
            u_height=self.u_height,
            starting_unit=self.starting_unit,
            description=self.description,
            status=self.status,
            location=self.location,
            airflow=self.airflow,
            form_factor=self.form_factor,
            weight=self.weight,
            weight_unit=self.weight_unit,
            mounting_depth=self.mounting_depth,
            outer_height=self.outer_height,
            outer_depth=self.outer_depth,
            outer_width=self.outer_width,
            outer_unit=self.outer_unit,
            max_weight=self.max_weight,
            desc_units=self.desc_units,
            comments=self.comments,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            tags=self.tags,
            tenant=self.tenant,
            facility_id=self.facility_id,
            width=self.width,
        )


__all__ = ["DiodeRack"]

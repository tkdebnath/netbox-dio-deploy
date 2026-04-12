"""DiodeDevice Pydantic model with mandatory field validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from netboxlabs.diode.sdk.ingester import Device


class DiodeDevice(BaseModel):
    """Pydantic model for Diode Device with mandatory field validation.

    This model enforces required fields (name, site, device_type, role) and
    supports all device-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Status field is validated to accept only: active, offline, planned.
    """

    # Required fields - must be provided
    name: str = Field(..., description="The device name")
    site: str = Field(..., description="The site name")
    device_type: str = Field(..., description="The device type model name")
    role: str = Field(..., description="The device role name")

    # Optional fields
    serial: Optional[str] = Field(default=None, description="Device serial number")
    asset_tag: Optional[str] = Field(default=None, description="Device asset tag")
    platform: Optional[str] = Field(default=None, description="Device platform")
    status: Optional[str] = Field(default=None, description="Device status (active, offline, planned)")
    custom_fields: Optional[dict[str, Any]] = Field(default=None, description="Custom field values")
    business_unit: Optional[str] = Field(default=None, description="Business unit for mapping to custom_fields")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True  # Validate on attribute assignment

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeDevice":
        """Parse a dictionary into a DiodeDevice instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing device data

        Returns:
            DiodeDevice instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status field against allowed values.

        Args:
            v: The status value to validate

        Returns:
            The validated status value

        Raises:
            ValueError: If status is not one of 'active', 'offline', or 'planned'
        """
        if v is None:
            return v
        allowed = {"active", "offline", "planned"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    def to_protobuf(self) -> Device:
        """Convert DiodeDevice to netboxlabs.diode.sdk.ingester.Device.

        Returns:
            Device protobuf object ready for Diode gRPC transmission
        """
        # The Diode SDK's Device protobuf expects custom_fields as a dict[str, CustomFieldValue].
        # Since we cannot easily convert dict[str, Any] to CustomFieldValue objects without
        # knowing the field type, we set custom_fields to None by default to avoid SDK errors.
        # Users should use the converter module for more sophisticated custom field handling.
        custom_fields = None

        return Device(
            name=self.name,
            serial=self.serial,
            asset_tag=self.asset_tag,
            platform=self.platform,
            status=self.status,
            device_type=self.device_type,
            role=self.role,
            site=self.site,
            custom_fields=custom_fields,
        )

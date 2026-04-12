"""DiodeDevice Pydantic model with mandatory field validation."""

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Any, Optional
from netboxlabs.diode.sdk.ingester import Device

from ..exceptions import DiodeValidationError


class DiodeDevice(BaseModel):
    """Pydantic model for Diode Device with mandatory field validation.

    This model enforces required fields (name, site, device_type, role) on initialization.

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
    def from_dict(cls, data: dict, device_name: Optional[str] = None) -> "DiodeDevice":
        """Parse a dictionary into a DiodeDevice instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.
        Wraps Pydantic ValidationError with DiodeValidationError for consistent error handling.

        Args:
            data: Dictionary containing device data
            device_name: Optional device name to include in error messages

        Returns:
            DiodeDevice instance with validated data

        Raises:
            DiodeValidationError: If required fields are missing or types are incorrect
        """
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            # Extract field names and values from the error
            error_details = []
            for error in e.errors():
                field = error.get("loc", [])[0] if error.get("loc") else "unknown"
                value = error.get("input", "unknown")
                msg = error.get("msg", "Validation failed")
                error_details.append({
                    "field": field,
                    "value": value,
                    "message": msg,
                })

            # Create a descriptive error message
            if len(error_details) == 1:
                err = error_details[0]
                field_name = err["field"]
                value = err["value"]
                message = f"Device '{device_name or 'unknown'}': {err['message']} on field '{field_name}'"
                if value != "unknown":
                    message += f" (value: {value})"
            else:
                # Multiple validation errors
                field_names = [err["field"] for err in error_details]
                # Include the first error's field_name and value for context
                first_err = error_details[0]
                field_name = first_err["field"]
                value = first_err["value"]
                message = f"Device '{device_name or 'unknown'}': Multiple validation errors on fields: {', '.join(field_names)}"
                if value != "unknown":
                    message += f" (first error: {first_err['message']} on '{field_name}')"

            raise DiodeValidationError(
                message,
                field_name=field_name if len(error_details) == 1 else field_names[0],
                value=value if len(error_details) == 1 else value,
                device_name=device_name,
            )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str], info) -> Optional[str]:
        """Validate status field against allowed values.

        Args:
            v: The status value to validate
            info: Pydantic ValidationInfo for accessing device context

        Returns:
            The validated status value

        Raises:
            ValueError: If status is not one of 'active', 'offline', or 'planned'
        """
        if v is None:
            return v
        allowed = {"active", "offline", "planned"}
        if v not in allowed:
            device_name = "unknown"
            # Try to get device name from validation context
            if hasattr(info, "data") and info.data:
                device_name = info.data.get("name", "unknown")
            raise ValueError(f"Device '{device_name}': status '{v}' is not valid. Must be one of: {', '.join(sorted(allowed))}")
        return v

    @classmethod
    def validate_name_length(cls, name: str) -> str:
        """Validate device name length.

        Args:
            name: The device name to validate

        Returns:
            The validated name

        Raises:
            DiodeValidationError: If name is not between 1 and 64 characters
        """
        if not name:
            raise DiodeValidationError(
                "Device name cannot be empty",
                field_name="name",
                value=name,
            )
        if len(name) > 64:
            raise DiodeValidationError(
                f"Device name exceeds maximum length of 64 characters (got {len(name)})",
                field_name="name",
                value=name,
            )
        if len(name) < 1:
            raise DiodeValidationError(
                "Device name is too short (minimum 1 character)",
                field_name="name",
                value=name,
            )
        return name

    @classmethod
    def validate_serial_format(cls, serial: Optional[str]) -> Optional[str]:
        """Validate serial number format.

        Args:
            serial: The serial number to validate

        Returns:
            The validated serial number

        Raises:
            DiodeValidationError: If serial format is invalid
        """
        if serial is None:
            return serial
        if len(serial) > 64:
            raise DiodeValidationError(
                f"Serial number exceeds maximum length of 64 characters (got {len(serial)})",
                field_name="serial",
                value=serial,
            )
        return serial

    @classmethod
    def validate_asset_tag_format(cls, asset_tag: Optional[str]) -> Optional[str]:
        """Validate asset tag format.

        Args:
            asset_tag: The asset tag to validate

        Returns:
            The validated asset tag

        Raises:
            DiodeValidationError: If asset tag format is invalid
        """
        if asset_tag is None:
            return asset_tag
        if len(asset_tag) > 64:
            raise DiodeValidationError(
                f"Asset tag exceeds maximum length of 64 characters (got {len(asset_tag)})",
                field_name="asset_tag",
                value=asset_tag,
            )
        return asset_tag

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

"""DiodeInterface Pydantic model with type-specific fields."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Interface, VLAN


class InterfaceType(str, Enum):
    """Interface type enumeration."""

    physical = "physical"
    virtual = "virtual"
    lag = "lag"
    wireless = "wireless"
    other = "other"


class InterfaceMode(str, Enum):
    """Interface mode enumeration."""

    access = "access"
    trunk = "trunk"
    bridge = "bridge"
    virtual = "virtual"


class InterfaceDuplex(str, Enum):
    """Interface duplex mode enumeration."""

    auto = "auto"
    full = "full"
    half = "half"


class DiodeInterface(BaseModel):
    """Pydantic model for Diode Interface with type-specific fields.

    This model enforces required fields (name, device, type) and
    supports all interface-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Type field is validated against InterfaceType enum values.
    Mode field is validated against InterfaceMode enum values.
    Duplex field is validated against InterfaceDuplex enum values.
    """

    # Required fields - must be provided
    name: str = Field(..., description="The interface name")
    device: str = Field(..., description="The device name")
    type: str = Field(..., description="The interface type (physical, virtual, lag, wireless, other)")

    # Optional fields
    label: Optional[str] = Field(default=None, description="Interface label")
    enabled: Optional[bool] = Field(default=None, description="Is interface enabled")
    parent: Optional[str] = Field(default=None, description="Parent interface name")
    bridge: Optional[str] = Field(default=None, description="Bridge interface name")
    lag: Optional[str] = Field(default=None, description="LAG interface name")
    mtu: Optional[int] = Field(default=None, description="Maximum transmission unit")
    primary_mac_address: Optional[str] = Field(default=None, description="Primary MAC address")
    speed: Optional[int] = Field(default=None, description="Speed in Mbps")
    duplex: Optional[str] = Field(default=None, description="Duplex mode (auto, full, half)")
    wwn: Optional[str] = Field(default=None, description="World wide name")
    mgmt_only: Optional[bool] = Field(default=None, description="Management only interface")
    description: Optional[str] = Field(default=None, description="Interface description")
    mode: Optional[str] = Field(default=None, description="Interface mode (access, trunk, bridge, virtual)")
    rf_role: Optional[str] = Field(default=None, description="Wireless role")
    rf_channel: Optional[str] = Field(default=None, description="Wireless channel")
    poe_mode: Optional[str] = Field(default=None, description="PoE mode")
    poe_type: Optional[str] = Field(default=None, description="PoE type")
    rf_channel_frequency: Optional[int] = Field(default=None, description="Wireless channel frequency")
    rf_channel_width: Optional[int] = Field(default=None, description="Wireless channel width")
    tx_power: Optional[int] = Field(default=None, description="Transmit power in dBm")
    untagged_vlan: Optional[str] = Field(default=None, description="Untagged VLAN name")
    qinq_svlan: Optional[str] = Field(default=None, description="Q-in-Q SVLAN name")
    vlan_translation_policy: Optional[str] = Field(default=None, description="VLAN translation policy")
    mark_connected: Optional[bool] = Field(default=None, description="Mark as connected")
    vrf: Optional[str] = Field(default=None, description="VRF name")
    tags: Optional[list[str]] = Field(default=None, description="Interface tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")
    wireless_lans: Optional[list[str]] = Field(default=None, description="Wireless LAN names")
    vdcs: Optional[list[str]] = Field(default=None, description="Virtual device context names")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeInterface":
        """Parse a dictionary into a DiodeInterface instance.

        Uses Pydantic's model_validate() for proper type coercion and validation.

        Args:
            data: Dictionary containing interface data

        Returns:
            DiodeInterface instance with validated data

        Raises:
            ValidationError: If required fields are missing or types are incorrect
        """
        return cls.model_validate(data)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate interface type against allowed values.

        Args:
            v: The interface type to validate

        Returns:
            The validated interface type

        Raises:
            ValueError: If type is not one of the allowed values
        """
        allowed = {"physical", "virtual", "lag", "wireless", "other"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: Optional[str]) -> Optional[str]:
        """Validate interface mode against allowed values.

        Args:
            v: The interface mode to validate

        Returns:
            The validated interface mode

        Raises:
            ValueError: If mode is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"access", "trunk", "bridge", "virtual"}
        if v not in allowed:
            raise ValueError(f"mode must be one of {allowed}")
        return v

    @field_validator("duplex")
    @classmethod
    def validate_duplex(cls, v: Optional[str]) -> Optional[str]:
        """Validate interface duplex against allowed values.

        Args:
            v: The duplex mode to validate

        Returns:
            The validated duplex mode

        Raises:
            ValueError: If duplex is not one of the allowed values
        """
        if v is None:
            return v
        allowed = {"auto", "full", "half"}
        if v not in allowed:
            raise ValueError(f"duplex must be one of {allowed}")
        return v

    def to_protobuf(self) -> Interface:
        """Convert DiodeInterface to netboxlabs.diode.sdk.ingester.Interface.

        Returns:
            Interface protobuf object ready for Diode gRPC transmission
        """
        # Build the Interface protobuf message directly without hardcoded VLAN objects
        interface = Interface(
            name=self.name,
            device=self.device,
            type=self.type,
            label=self.label,
            enabled=self.enabled,
            parent=self.parent,
            bridge=self.bridge,
            lag=self.lag,
            mtu=self.mtu,
            primary_mac_address=self.primary_mac_address,
            speed=self.speed,
            duplex=self.duplex,
            wwn=self.wwn,
            mgmt_only=self.mgmt_only,
            description=self.description,
            mode=self.mode,
            rf_role=self.rf_role,
            rf_channel=self.rf_channel,
            poe_mode=self.poe_mode,
            poe_type=self.poe_type,
            rf_channel_frequency=self.rf_channel_frequency,
            rf_channel_width=self.rf_channel_width,
            tx_power=self.tx_power,
            untagged_vlan=self.untagged_vlan,
            qinq_svlan=self.qinq_svlan,
            vlan_translation_policy=self.vlan_translation_policy,
            mark_connected=self.mark_connected,
            vrf=self.vrf,
            tags=self.tags,
            custom_fields=self.custom_fields,
            metadata=self.metadata,
            owner=self.owner,
            wireless_lans=self.wireless_lans,
            vdcs=self.vdcs,
        )

        return interface


__all__ = [
    "DiodeInterface",
    "InterfaceType",
    "InterfaceMode",
    "InterfaceDuplex",
]

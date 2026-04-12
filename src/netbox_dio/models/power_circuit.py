"""DiodeCircuit Pydantic model for power circuits."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from netboxlabs.diode.sdk.ingester import Circuit


class DiodeCircuit(BaseModel):
    """Pydantic model for Diode Circuit.

    This model represents a power circuit with required fields (cid, name)
    and supports all circuit-level attributes defined in the requirements.

    Required fields use `Field(...)` to ensure they must be provided.
    Optional fields use `Field(default=None)` to allow omission.

    Validation rules:
    - cid: 1-64 characters
    - name: 1-64 characters
    - commit_rate: 0-100000000000 (0-100Gbps)
    """

    # Required fields - must be provided
    cid: str = Field(..., description="Circuit ID (unique identifier)")
    name: str = Field(..., description="Circuit name")

    # Optional fields
    type: Optional[str] = Field(default=None, description="Circuit type from CircuitType")
    provider: Optional[str] = Field(default=None, description="Provider reference")
    provider_account: Optional[str] = Field(default=None, description="Provider account reference")
    status: Optional[str] = Field(default=None, description="Circuit status")
    assignments: Optional[list] = Field(default=None, description="Circuit assignments (terminations)")
    install_date: Optional[str] = Field(default=None, description="Installation date")
    commit_rate: Optional[int] = Field(default=None, description="Commit rate in bps")
    distance: Optional[float] = Field(default=None, description="Physical distance")
    distance_unit: Optional[str] = Field(default=None, description="Distance unit (m, km, ft, mi)")
    tenant: Optional[str] = Field(default=None, description="Tenant reference")
    description: Optional[str] = Field(default=None, description="Circuit description")
    comments: Optional[str] = Field(default=None, description="Circuit comments")
    tags: Optional[list[str]] = Field(default=None, description="Circuit tags")
    custom_fields: Optional[dict] = Field(default=None, description="Custom field values")
    metadata: Optional[dict] = Field(default=None, description="Metadata")
    owner: Optional[str] = Field(default=None, description="Owner")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeCircuit":
        """Parse a dictionary into a DiodeCircuit instance.

        Args:
            data: Dictionary containing circuit data

        Returns:
            DiodeCircuit instance with validated data
        """
        return cls.model_validate(data)

    @field_validator("cid")
    @classmethod
    def validate_cid_length(cls, v: str) -> str:
        """Validate circuit ID length (1-64 characters).

        Args:
            v: The circuit ID to validate

        Returns:
            The validated CID

        Raises:
            ValueError: If CID length is invalid
        """
        if not v:
            raise ValueError("Circuit ID cannot be empty")
        if len(v) < 1:
            raise ValueError("Circuit ID is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"Circuit ID exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        """Validate circuit name length (1-64 characters).

        Args:
            v: The circuit name to validate

        Returns:
            The validated name

        Raises:
            ValueError: If name length is invalid
        """
        if not v:
            raise ValueError("Circuit name cannot be empty")
        if len(v) < 1:
            raise ValueError("Circuit name is too short (minimum 1 character)")
        if len(v) > 64:
            raise ValueError(f"Circuit name exceeds maximum length of 64 characters (got {len(v)})")
        return v

    @field_validator("commit_rate")
    @classmethod
    def validate_commit_rate(cls, v: Optional[int]) -> Optional[int]:
        """Validate commit rate is in valid range (0-100000000000).

        Args:
            v: The commit rate value to validate

        Returns:
            The validated commit rate

        Raises:
            ValueError: If commit rate is out of range
        """
        if v is None:
            return v
        if v < 0:
            raise ValueError(f"commit_rate must be non-negative (got {v})")
        if v > 100000000000:
            raise ValueError(f"commit_rate exceeds maximum of 100Gbps (got {v})")
        return v

    def to_protobuf(self) -> Circuit:
        """Convert DiodeCircuit to netboxlabs.diode.sdk.ingester.Circuit.

        Returns:
            Circuit protobuf object ready for Diode gRPC transmission
        """
        circuit_args = {
            "cid": self.cid,
        }
        if self.type:
            circuit_args["type"] = self.type
        if self.provider:
            circuit_args["provider"] = self.provider
        if self.provider_account:
            circuit_args["provider_account"] = self.provider_account
        if self.status:
            circuit_args["status"] = self.status
        if self.assignments:
            circuit_args["assignments"] = self.assignments
        if self.install_date:
            circuit_args["install_date"] = self.install_date
        if self.commit_rate is not None:
            circuit_args["commit_rate"] = self.commit_rate
        if self.distance:
            circuit_args["distance"] = self.distance
        if self.distance_unit:
            circuit_args["distance_unit"] = self.distance_unit
        if self.tenant:
            circuit_args["tenant"] = self.tenant
        if self.description:
            circuit_args["description"] = self.description
        if self.comments:
            circuit_args["comments"] = self.comments
        if self.tags:
            circuit_args["tags"] = self.tags
        if self.custom_fields:
            circuit_args["custom_fields"] = self.custom_fields
        if self.metadata:
            circuit_args["metadata"] = self.metadata
        if self.owner:
            circuit_args["owner"] = self.owner

        return Circuit(**circuit_args)


__all__ = ["DiodeCircuit"]

# Phase 1: Core Model - Research

**Researched:** 2026-04-12
**Domain:** Pydantic v2 validation, Diode SDK integration
**Confidence:** HIGH

## Summary

This phase requires building a Pydantic `DiodeDevice` wrapper class that enforces mandatory fields (name, site, device_type, role) and supports all device-level attributes defined in the requirements. The implementation must integrate with the `netboxlabs-diode-sdk` (v1.10.0), which provides a Pythonic wrapper around protobuf messages.

**Primary recommendation:** Create a Pydantic v2 `BaseModel` class with:
1. Required fields annotated with `Field(...)` to enforce mandatory data
2. Custom `from_dict()` class method for dictionary-to-model conversion
3. Model-level validation for cross-field constraints
4. Integration patterns for converting to `netboxlabs.diode.sdk.ingester.Device` protobuf messages

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12.5 | Data validation, schema enforcement | Built-in type hints, field validation, model methods |
| netboxlabs-diode-sdk | 1.10.0 | Protobuf wrapper, gRPC client | Official SDK, provides Device/Entity wrappers |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| google.protobuf | latest | Protobuf message handling | For `ParseDict` to convert dict to protobuf |
| grpcio | >=1.68.1 | gRPC transport | Required by Diode SDK |

**Installation:**
```bash
pip install --break-system-packages pydantic netboxlabs-diode-sdk
```

**Version verification:**
- pydantic: 2.12.5 (2026-03)
- netboxlabs-diode-sdk: 1.10.0 (2026-04-12)
- protobuf: 6.33.6 (transitive dependency)

## Architecture Patterns

### Recommended Project Structure
```
src/netbox_dio/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── device.py          # DiodeDevice class
└── converters/
    ├── __init__.py
    └── device.py          # DiodeDevice to Device conversion
```

### Pattern 1: Pydantic BaseModel with Required Fields
**What:** Use `Field(...)` to mark mandatory fields and enforce validation
**When to use:** All model classes in this project
**Example:**
```python
from pydantic import BaseModel, Field

class DiodeDevice(BaseModel):
    name: str = Field(..., description="Device name (required)")
    site: str = Field(..., description="Site name (required)")
    device_type: str = Field(..., description="Device type model name (required)")
    role: str = Field(..., description="Device role name (required)")
    serial: str | None = Field(default=None, description="Serial number")
    asset_tag: str | None = Field(default=None, description="Asset tag")
    platform: str | None = Field(default=None, description="Platform name")
    status: str | None = Field(default=None, description="Device status")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    business_unit: str | None = Field(default=None, description="Business unit mapping")
```

### Pattern 2: from_dict() Class Method
**What:** Provide a class method that parses nested dictionaries into models
**When to use:** All models that accept dictionary input
**Example:**
```python
@classmethod
def from_dict(cls, data: dict) -> "DiodeDevice":
    """Parse a nested dictionary into a DiodeDevice instance."""
    return cls(**data)
```

### Pattern 3: Model Conversion to Protobuf
**What:** Method to convert Pydantic model to Diode SDK Device protobuf
**When to use:** Before sending data to Diode
**Example:**
```python
def to_protobuf(self) -> Device:
    """Convert to netboxlabs.diode.sdk.ingester.Device."""
    return Device(
        name=self.name,
        serial=self.serial,
        asset_tag=self.asset_tag,
        # ... other fields
    )
```

### Anti-Pitfalls to Avoid
- **Don't use `model_fields` on instances** - deprecated in Pydantic 2.11, use `model_fields` on class
- **Don't rely on Diode SDK for validation** - it accepts optional fields by design
- **Don't use deprecated `construct()` method** - use `model_validate()` instead
- **Don't mix field types** - keep required and optional fields in separate groupings

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data validation | Custom validation functions | Pydantic `Field(...)`, `@field_validator` | Built-in type checking, clear error messages, faster |
| Dict-to-model parsing | Manual `__init__` parsing | Pydantic `model_validate()` or `from_dict(**kwargs)` | Reduces bugs, handles type coercion |
| Protobuf conversion | Manual field mapping | `netboxlabs.diode.sdk.ingester.Device()` | SDK handles complex nested structures |

**Key insight:** The Diode SDK provides well-tested protobuf wrappers that handle complex nested structures (device_type, role, site as separate objects). Custom implementations will miss edge cases and require significant maintenance.

## Common Pitfalls

### Pitfall 1: Pydantic Field Validation
**What goes wrong:** Using `Field(default=None)` for required fields, which makes them optional
**Why it happens:** Confusing "required" with "type-annotated as required"
**How to avoid:** Use `Field(...)` (ellipsis) for required fields, `Field(default=None)` for optional
**Warning signs:** ValidationError not raised when expected, instance created with missing required fields

### Pitfall 2: Diode SDK Field Order
**What goes wrong:** Passing fields in wrong order to Device() constructor
**Why it happens:** Diode Device has many optional fields; mixing up position vs keyword args
**How to avoid:** Always use keyword arguments for Device() construction
**Warning signs:** "Unexpected keyword argument" TypeError

### Pitfall 3: String Fields for Complex Objects
**What goes wrong:** Passing string to device_type/role/site when Diode expects DeviceType/DeviceRole/Site objects
**Why it happens:** Diode SDK automatically converts strings via `convert_to_protobuf()`, but only if using the wrapper class correctly
**How to avoid:** Use `netboxlabs.diode.sdk.ingester.Device()` wrapper, not `ingester_pb2.Device()` directly
**Warning signs:** Protobuf type mismatch errors, "has no attribute" errors on nested objects

### Pitfall 4: business_unit Field Mapping
**What goes wrong:** business_unit is not a native Diode Device field
**Why it happens:** Trying to pass business_unit directly to Device()
**How to avoid:** Map business_unit to custom_fields in the Pydantic model, not to Diode SDK
**Warning signs:** Unexpected keyword 'business_unit' error

## Code Examples

### Device Model with Required Fields
```python
from pydantic import BaseModel, Field
from typing import Any

class DiodeDevice(BaseModel):
    """Pydantic model for Diode Device with mandatory field validation."""
    
    # Required fields - must be provided
    name: str = Field(..., description="The device name")
    site: str = Field(..., description="The site name")
    device_type: str = Field(..., description="The device type model name")
    role: str = Field(..., description="The device role name")
    
    # Optional fields
    serial: str | None = Field(default=None, description="Device serial number")
    asset_tag: str | None = Field(default=None, description="Device asset tag")
    platform: str | None = Field(default=None, description="Device platform")
    status: str | None = Field(default=None, description="Device status (active, offline, planned)")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field values")
    business_unit: str | None = Field(default=None, description="Business unit for mapping to custom_fields")

    class Config:
        validate_assignment = True  # Validate on attribute assignment

    @classmethod
    def from_dict(cls, data: dict) -> "DiodeDevice":
        """Parse a nested dictionary into a DiodeDevice instance."""
        return cls.model_validate(data)

    def to_protobuf(self) -> Device:
        """Convert to netboxlabs.diode.sdk.ingester.Device."""
        from netboxlabs.diode.sdk.ingester import Device
        return Device(
            name=self.name,
            serial=self.serial,
            asset_tag=self.asset_tag,
            platform=self.platform,
            status=self.status,
            device_type=self.device_type,
            role=self.role,
            site=self.site,
            custom_fields=self.custom_fields,
            # Note: business_unit maps to custom_fields
        )
```

### Custom Fields Validation
```python
@field_validator("status")
@classmethod
def validate_status(cls, v):
    """Validate status field against allowed values."""
    if v is None:
        return v
    allowed = {"active", "offline", "planned"}
    if v not in allowed:
        raise ValueError(f"status must be one of {allowed}")
    return v
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual dict parsing | Pydantic v2 BaseModel | 2023-2024 | Type safety, automatic validation, cleaner code |
| Direct protobuf construction | SDK wrapper classes | 2026-02 (Diode SDK v1.10.0) | Simplified API, automatic protobuf conversion |

**Deprecated/outdated:**
- Using `ingester_pb2.Device()` directly without wrapper - harder to work with, no type hints
- Using Pydantic v1 patterns - `construct()` deprecated, use `model_validate()`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Pydantic v2.12.5 is current stable version | Standard Stack | Low - Pydantic evolves slowly, API changes are backward compatible |
| A2 | netboxlabs-diode-sdk 1.10.0 provides stable Device wrapper | Standard Stack | Low - Official SDK, protobuf interface is stable |
| A3 | Field(..., description="...") is the correct pattern for required fields | Architecture Patterns | Low - Well-documented Pydantic pattern |
| A4 | from_dict() should use model_validate() internally | Code Examples | Low - Standard Pydantic v2 pattern |
| A5 | business_unit should map to custom_fields in the Diode Device | Common Pitfalls | Medium - Need user confirmation that this is the desired mapping behavior |

## Open Questions

1. **Should status field be validated against allowed values?**
   - What we know: Diode accepts status as string field
   - What's unclear: Are there specific allowed values (active, offline, planned) or any string?
   - Recommendation: Add validation with allowlist, document the valid values

2. **What is the expected format for business_unit mapping?**
   - What we know: business_unit is a custom requirement, not native to Diode
   - What's unclear: Should business_unit be stored in custom_fields under a specific key (e.g., "Business Unit")?
   - Recommendation: Map to custom_fields["Business Unit"] or similar; needs user confirmation

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.10+ | Runtime | ✓ | 3.11.2 | 3.10 minimum |
| Pydantic | Data validation | ✓ | 2.12.5 | — |
| netboxlabs-diode-sdk | Diode integration | ✓ | 1.10.0 | — |

**Missing dependencies with no fallback:**
- None

**Missing dependencies with fallback:**
- None

## Validation Architecture

> Note: `workflow.nyquist_validation` check required in `.planning/config.json`. Assuming enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `pytest.ini` or `pyproject.toml` |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CORE-01 | DiodeDevice enforces name, site, device_type, role | unit | `pytest tests/models/test_device.py::test_required_fields -x` | ❌ Wave 0 |
| CORE-02 | from_dict() parses nested dictionary | unit | `pytest tests/models/test_device.py::test_from_dict -x` | ❌ Wave 0 |
| CORE-04 | Pydantic validation enforces type correctness | unit | `pytest tests/models/test_device.py::test_type_validation -x` | ❌ Wave 0 |
| DEV-01 | Device supports serial, asset_tag | unit | `pytest tests/models/test_device.py::test_optional_fields -x` | ❌ Wave 0 |
| DEV-02 | Device supports device_type with manufacturer | unit | `pytest tests/models/test_device.py::test_device_type -x` | ❌ Wave 0 |
| DEV-03 | Device supports role assignment | unit | `pytest tests/models/test_device.py::test_role -x` | ❌ Wave 0 |
| DEV-04 | Device supports platform specification | unit | `pytest tests/models/test_device.py::test_platform -x` | ❌ Wave 0 |
| DEV-05 | Device supports site assignment | unit | `pytest tests/models/test_device.py::test_site -x` | ❌ Wave 0 |
| DEV-06 | Device supports status field | unit | `pytest tests/models/test_device.py::test_status -x` | ❌ Wave 0 |
| DEV-07 | Device supports custom_fields | unit | `pytest tests/models/test_device.py::test_custom_fields -x` | ❌ Wave 0 |
| DEV-08 | Device supports business_unit mapping | unit | `pytest tests/models/test_device.py::test_business_unit -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x`
- **Per wave merge:** `pytest tests/`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/models/test_device.py` — covers CORE-01, CORE-02, CORE-04, DEV-01 through DEV-08
- [ ] `tests/conftest.py` — shared fixtures for models
- [ ] Framework install: `pip install --break-system-packages pytest` — if none detected

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A - No auth in this phase |
| V3 Session Management | no | N/A - No sessions in this phase |
| V4 Access Control | no | N/A - No access control in this phase |
| V5 Input Validation | yes | Pydantic field validation, type checking |
| V6 Cryptography | no | N/A - No encryption in this phase |

### Known Threat Patterns for Pydantic/Diode

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Invalid data injection | Tampering | Pydantic type validation, field validation |
| Type confusion | Spoofing | Pydantic type hints, model_validate() |
| Missing required field | Elevation | Field(...) required fields |

## Sources

### Primary (HIGH confidence)
- Pydantic v2.12.5 documentation - BaseModel, Field, model_validator patterns
- netboxlabs-diode-sdk 1.10.0 - Device, Entity wrapper classes
- PyPI package registry - version verification

### Secondary (MEDIUM confidence)
- Pydantic error handling patterns from official docs
- Diode SDK protobuf conversion functions

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH - Versions verified via pip show
- Architecture: HIGH - Pydantic patterns well-documented
- Pitfalls: HIGH - Common issues identified from code inspection

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (30 days for stable libraries)

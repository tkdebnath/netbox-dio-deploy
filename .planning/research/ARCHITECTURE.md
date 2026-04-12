# Architecture Research

**Domain:** Python network automation with Diode SDK wrapper
**Researched:** 2026-04-12
**Confidence:** HIGH

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    NetBox Diode Device Wrapper                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DiodeDevice (Core)                               │    │
│  │  - Device-centric dictionary parsing                                │    │
│  │  - Pydantic validation                                              │    │
│  │  - Diode SDK payload generation                                     │    │
│  └───────────────────────┬─────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │   Components    │  │   Data Layer    │  │       I/O Layer            │  │
│  │                 │  │                 │  │                            │  │
│  │  - devices/     │  │  - Pydantic     │  │  - DiodeClient             │  │
│  │  - interfaces/  │  │  - Model        │  │  - DiodeDryRunClient       │  │
│  │  - vlans/       │  │  - Validation   │  │  - gRPC transmission       │  │
│  │  - prefixes/    │  │  - Error handling│ │  - Environment config      │  │
│  │  - cables/      │  │                 │  │                            │  │
│  └────────┬────────┘  └─────────────────┘  └──────────────────────────────┘  │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                  Diode SDK (netboxlabs-diode-sdk)                   │    │
│  │  - gRPC client                                                      │    │
│  │  - Entity generation                                                │    │
│  │  - protobuf serialization                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **DiodeDevice** | Core model for network devices, parsing dictionaries, generating Diode payloads | Pydantic model with factory methods |
| **devices/** | Device-specific operations, batch operations, error handling | Module with class methods |
| **interfaces/** | Interface parsing, type-specific handling, IP address management | Separate module with interface models |
| **vlans/** | VLAN creation, group management, translation policies | VLAN-specific models and methods |
| **cables/** | Cable creation, termination mapping, connection tracking | Cable models with termination support |
| **prefixes/** | Prefix management, scope assignment, VRF association | Prefix models with scoping |
| **data layer** | Pydantic validation, schema definition, data integrity | Pydantic models with field validation |
| **io layer** | gRPC communication, dry-run mode, environment configuration | DiodeClient wrapper classes |

## Recommended Project Structure

```
src/netbox_dio/
├── __init__.py              # Package exports, version info
├── config.py                # Environment variable parsing, connection config
├── exceptions.py            # Custom exceptions (ValueError, TypeError)
├── models/
│   ├── __init__.py
│   ├── base.py              # Base Pydantic models, common validators
│   ├── device.py            # DiodeDevice main class
│   ├── interface.py         # Interface models (physical, virtual)
│   ├── vlan.py              # VLAN, VLANGroup models
│   ├── prefix.py            # Prefix, VRF models
│   ├── cable.py             # Cable, CableTermination models
│   └── ip_address.py        # IP address models
├── client.py                # DiodeClient wrapper, ingest methods
├── converter.py             # Pydantic model to Diode Entity conversion
└── utils.py                 # Helper functions, slugify, type checks
```

### Structure Rationale

- **`models/`**: Isolates Pydantic data models from operational code. Each domain (device, interface, vlan, etc.) has its own file for maintainability.

- **`converter.py`**: Centralizes the conversion logic from user-friendly Pydantic models to Diode SDK protobuf entities. This is the core translation layer.

- **`client.py`**: Wraps the Diode SDK client for a consistent interface, handling both live and dry-run modes.

- **`config.py`**: Centralizes environment variable configuration for gRPC endpoint, credentials, and TLS settings.

- **`exceptions.py`**: Custom exception hierarchy for clear error messages (e.g., `DeviceValidationError`, `MissingRequiredFieldError`).

## Architectural Patterns

### Pattern 1: Factory Pattern with Pydantic

**What:** Use Pydantic's `__init__` and `@classmethod` to create validated objects from dictionaries.

**When to use:** When converting dictionary-based device definitions (common in network automation) into typed objects.

**Trade-offs:** Pydantic handles validation automatically; conversion overhead is minimal for typical network device counts.

**Example:**
```python
class DiodeDevice(BaseModel):
    name: str
    site: str
    device_type: str
    role: str
    interfaces: List[DeviceInterface] = []
    
    @classmethod
    def from_dict(cls, data: dict) -> "DiodeDevice":
        """Create and validate from dictionary"""
        return cls(**data)
    
    def to_diode_entities(self) -> List[Entity]:
        """Generate Diode SDK Entity objects for gRPC"""
        # Implementation converts to Diode SDK types
        pass

# Usage
device = DiodeDevice.from_dict({
    "name": "router1",
    "site": "site1",
    "device_type": "c9300",
    "role": "router",
    "interfaces": [...]
})
```

### Pattern 2: Adapter Pattern for Diode SDK

**What:** Wrap the Diode SDK's protobuf-based API with Python-native interfaces.

**When to use:** When the underlying library uses a different data model (protobuf) than what's natural for users (dictionaries).

**Trade-offs:** Adds a conversion layer but provides a cleaner user experience. The adapter handles the complexity of mapping dictionary structures to protobuf messages.

**Example:**
```python
class DiodeClient:
    """Wrapper around DiodeDryRunClient/DiodeClient"""
    
    def __init__(self, endpoint: str, client_id: str, client_secret: str):
        self._client = DiodeDryRunClient()
    
    def ingest(self, entities: List[Entity]) -> IngestResponse:
        return self._client.ingest(entities)
    
    def ingest_from_device(self, device: DiodeDevice) -> IngestResponse:
        """High-level method that handles conversion automatically"""
        diode_entities = device.to_diode_entities()
        return self._client.ingest(diode_entities)
```

### Pattern 3: Strategy Pattern for Data Conversion

**What:** Different strategies for converting Pydantic models to Diode protobuf messages, depending on the entity type.

**When to use:** When different entity types (Device, Interface, VLAN, Cable) have different conversion rules.

**Trade-offs:** More complex but allows for clean separation of conversion logic per entity type.

## Data Flow

### Request Flow

```
User Dictionary
    ↓
DiodeDevice.from_dict()  [Pydantic validation]
    ↓
DiodeDevice instance     [Validated Python object]
    ↓
DiodeDevice.to_diode_entities()  [Conversion to Diode SDK]
    ↓
List[Entity]             [Diode protobuf entities]
    ↓
DiodeClient.ingest()     [gRPC transmission]
    ↓
Diode Response           [Success/Failure]
```

### State Management

```
[User Input - Dictionary]
    ↓
[Pydantic Model] ←→ [Validation Rules]  [Runtime type checking]
    ↓
[Diode Entity] ←→ [Protobuf Schema]     [SDK serialization]
    ↓
[Ingest Response] ←→ [Error Handling]    [Result reporting]
```

### Key Data Flows

1. **Input Parsing:** Dictionary → Pydantic model with nested validation
   - Device dictionary contains interfaces, VLANs, etc.
   - Pydantic validates types, required fields, nested structures
   - Errors raise descriptive exceptions

2. **Conversion:** Pydantic model → Diode Entity → Protobuf
   - Each model type has dedicated converter function
   - Device converts to Device protobuf
   - Interfaces convert to Interface protobuf
   - References (site, device_type, role) resolve to name strings

3. **Output:** List[Entity] → gRPC IngestRequest → JSON/Proto
   - DiodeDryRunClient outputs JSON for verification
   - DiodeClient sends to gRPC endpoint
   - Response includes success status and any errors

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k devices | Single-threaded processing, sequential ingest |
| 1k-100k devices | Batch processing, parallel device ingestion, connection pooling |
| 100k+ devices | Async I/O, streaming ingest, circuit breaker for failures |

### Scaling Priorities

1. **First bottleneck:** I/O latency for gRPC calls
   - **Fix:** Batch entities into larger IngestRequests, use async I/O
   - **Optimization:** Connection pooling for DiodeClient

2. **Second bottleneck:** Memory usage for large dictionaries
   - **Fix:** Stream processing, generator-based conversion
   - **Optimization:** Ingest in chunks, track memory usage

## Anti-Patterns

### Anti-Pattern 1: Deeply Nested Protobuf Construction

**What people do:** Manually building nested Protobuf messages for each device and interface

**Why it's wrong:** Extremely verbose, error-prone, hard to maintain. Pydantic provides cleaner syntax and automatic validation.

**Do this instead:** Define Pydantic models that mirror the user's dictionary structure, then use a converter to generate Protobuf messages.

### Anti-Pattern 2: Mixing Validation and I/O Logic

**What people do:** Mixing validation logic with gRPC client logic in the same class

**Why it's wrong:** Hard to test, violates single responsibility. Validation should fail before any network call.

**Do this instead:** Validate first with Pydantic, then convert to Diode entities, then pass to I/O layer.

### Anti-Pattern 3: Silent Error Handling

**What people do:** Catching exceptions and returning None or empty responses

**Why it's wrong:** Makes debugging difficult, user doesn't know what failed.

**Do this instead:** Raise descriptive exceptions with context (field name, value, expected type).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Diode gRPC** | Direct connection, TLS/SSL, client ID/secret auth | Environment variables for config |
| **Dry-run mode** | File output for verification | Use during development, testing |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **Pydantic models → Diode SDK** | Conversion functions | `converter.py` handles mapping |
| **Client → I/O** | Method calls | `client.py` wraps DiodeDryRunClient |
| **Models → Errors** | Exception raising | `exceptions.py` defines hierarchy |

## Sources

- **Diode SDK Source:** `/home/claude/.local/lib/python3.11/site-packages/netboxlabs/diode/sdk/`
- **Pydantic Documentation:** https://pydantic.dev/
- **gRPC Python:** https://grpc.io/docs/languages/python/

---
*Architecture research for: NetBox Diode Device Wrapper*
*Researched: 2026-04-12*

# NetBox Diode Device Wrapper - Architecture

## Overview

A high-level Python wrapper for the NetBox Diode SDK that provides a **Device-Centric** simplified interface for managing network infrastructure data in NetBox. The wrapper parses nested dictionary structures into typed objects and generates Diode payloads for gRPC transmission.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER FACING LAYER                                    │
│  - Pydantic Models (DiodeDevice, DiodeInterface, DiodeVLAN, etc.)            │
│  - Import/Export APIs (from_dict, to_json, to_yaml, from_netbox_api)         │
│  - Client API (DiodeClient.send_single, DiodeClient.send_batch)              │
│  - Batch Processing (BatchProcessor, create_message_chunks)                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONVERSION LAYER                                      │
│  - convert_device() → Entity                                                  │
│  - convert_device_to_entities() → list[Entity]                               │
│  - convert_interface(), convert_vlan(), convert_module() etc.                │
│  - Converter handles nested subcomponents                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ABSTRACTION LAYER (Wrapper)                                │
│  - DiodeClient (wraps netboxlabs-diode-sdk DiodeClient)                     │
│  - ConnectionConfig (env-based configuration)                                │
│  - BatchProcessor (chunking, error aggregation)                              │
│  - Progress Manager (Rich with MockFallback)                                │
│  - Validator Pipeline (extensible validation rules)                          │
│  - Quality Reporter (data metrics)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DIODE SDK LAYER (netboxlabs-diode-sdk)                 │
│  - DiodeClient (gRPC client)                                                 │
│  - Entity, Device, Interface, VLAN, Module, Cable, etc. (protobuf)          │
│  - gRPC transport to NetBox Diode                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 1: User Facing Layer

**Purpose:** Simple, type-safe API for developers

**Components:**

| Module | Classes/Functions | Purpose |
|--------|-------------------|---------|
| `models/` | `DiodeDevice`, `DiodeInterface`, `DiodeVLAN`, `DiodeModule`, `DiodeCable`, etc. | Pydantic models with validation |
| `__init__.py` | `convert_device_to_entities` | Main conversion function |
| `export.py` | `to_json()`, `to_yaml()`, `to_netbox_yaml()` | Export to various formats |
| `importer.py` | `from_dict()`, `import_from_json()`, `from_netbox_api()` | Import from various sources |
| `batch.py` | `BatchProcessor`, `create_message_chunks()` | Batch processing |
| `client.py` | `DiodeClient`, `ConnectionConfig.from_env()` | Send to Diode |

**User API Example:**
```python
from netbox_dio import DiodeDevice, DiodeClient, convert_device_to_entities

# 1. Create device from dict (Pydantic validation)
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core-router",
    "interfaces": [
        {"name": "eth0", "device": "router-01", "type": "physical"}
    ]
})

# 2. Convert to SDK entities
entities = convert_device_to_entities(device)

# 3. Send to Diode
client = DiodeClient.from_env()
client.connect()
client.send_batch(entities)
```

---

### Layer 2: Conversion Layer

**File:** `converter.py` (756 lines)

**Purpose:** Translate Pydantic models to SDK protobuf messages

**Conversion Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `convert_device()` | DiodeDevice | Entity (device) |
| `convert_device_to_entities()` | DiodeDevice | list[Entity] (all nested) |
| `convert_interface()` | DiodeInterface | Entity (interface) |
| `convert_vlan()` | DiodeVLAN | Entity (vlan) |
| `convert_module()` | DiodeModule | Entity (module) |
| `convert_cable()` | DiodeCable | Entity (cable) |
| `convert_prefix()` | DiodePrefix | Entity (prefix) |
| `convert_ip_address()` | DiodeIPAddress | Entity (ip_address) |

**Key Features:**
- Wraps all conversions in `DiodeConversionError` for consistent error handling
- `convert_device_to_entities()` recursively converts all nested subcomponents
- Handles SDK type conversions (e.g., string VLAN refs → VLAN objects)

**Critical Fix:** The original `convert_device_to_entities()` only returned `[convert_device(device)]` but now calls `convert_device_with_subcomponents()` to include all nested objects.

---

### Layer 3: Abstraction Layer

**Purpose:** Hide SDK complexity, add wrapper features

**Components:**

| File | Abstractions Provided |
|------|----------------------|
| `client.py` | `DiodeClient` (wraps SDK's `DiodeClient`), `ConnectionConfig` (env-based setup) |
| `batch.py` | `BatchProcessor` (chunking, error aggregation), `BatchResult` (stats) |
| `caching/` | `CacheBackend` interface, `RedisCacheBackend`, `InMemoryCacheBackend` |
| `validators/` | Extensible validation framework with `RuleRegistry` |
| `quality/` | `QualityMetrics`, `QualityReporter` for data quality |
| `progress/` | `ProgressManager` (Rich UI + MockFallback) |
| `export.py` | Format abstraction (JSON/YAML/NetBox YAML) |
| `importer.py` | Format abstraction (JSON/YAML/NetBox API → dict) |
| `exceptions.py` | Hierarchical error types with context |

**Client Abstraction:**
```python
# User sees simple API
client = DiodeClient.from_env()
client.connect()
client.send_single(device)  # Converts internally

# Wraps SDK's gRPC client
self._client = DiodeSdkClient(target=endpoint, ...)
result = self._client.ingest(entities)
```

---

### Layer 4: Diode SDK Layer

**External Package:** `netboxlabs-diode-sdk>=1.10.0`

**Module:** `netboxlabs.diode.sdk`

**Components Used:**

| SDK Class | Purpose | Wrapper Usage |
|-----------|---------|---------------|
| `DiodeClient` | gRPC client | Wrapped by `client.py` |
| `Entity` | Top-level message wrapper | All conversions return `Entity` |
| `Device` | Device protobuf | Created in converter/models |
| `Interface` | Interface protobuf | Created in converter/models |
| `VLAN`, `Module`, `Cable`, etc. | Other entity types | Created in converter/models |
| `GenericObject` | Cross-reference | Used in cable terminations |
| `ClientConfig` | Connection config | Used by `ConnectionConfig` |

**SDK API Notes:**
- `untagged_vlan` in Interface expects `VLAN` object, not string
- `a_terminations`/`b_terminations` in Cable are `list[GenericObject]`
- All protobuf messages have nested message fields (e.g., `Device.device_type` is a nested `Type` message)

---

## Data Flow

### Primary Use Case: Device → Diode

```
┌──────────────┐
│ Dictionary   │  User input (dict)
│ {device: {...}}
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ DiodeDevice  │  Pydantic model (validation, type coercion)
│ .from_dict() │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ converter.py │  convert_device_to_entities()
│ .to_entities()│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ list[Entity] │  Diode SDK protobuf messages
│ ┌──┐         │
│ │D │         │  Device entity
│ ├──┤         │
│ │I │         │  Interface entity(s)
│ ├──┤         │
│ │V │         │  VLAN entity(s)
│ └──┘         │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ DiodeClient  │  client.py (connect, send_batch)
│ .send_batch()│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Diode SDK    │  nnetboxlabs-diode-sdk
│ DiodeClient  │  .ingest(entities)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ NetBox Diode │  gRPC endpoint
│ (ingestion)  │
└──────────────┘
```

### Batch Processing Flow

```
┌──────────────┐
│ List[Device] │  User's list of DiodeDevice objects
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ BatchProcessor│ .chunk_devices()
│ 1000/chunk   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ For each     │ .process_single_chunk()
│ chunk:       │
│ 1. convert   │
│ 2. send_batch│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ BatchResult  │  summary, errors, timing
└──────────────┘
```

---

## Key Design Principles

### 1. **Device-Centric**
User thinks in terms of "devices" with nested interfaces, VLANs, modules. The wrapper handles all the disaggregation into SDK Entity messages.

### 2. **Pydantic Validation First**
Models are Pydantic BaseModels, enforcing:
- Required fields at parse time
- Type coercion (string "100" → int 100)
- Enum validation (status must be "active", "planned", etc.)
- Custom validation logic

### 3. **SDK Independence**
The wrapper patterns keep the SDK abstracted:
- `client.py` uses SDK `DiodeClient` but doesn't expose it directly
- `converter.py` converts wrapper types to SDK types
- Future SDK upgrades only require model/converter updates

### 4. **Error Context**
All exceptions include:
- Device name/ID
- Error type
- Original data (for debugging)
- Human-readable message

### 5. **Progressive Disclosure**
Simple API (`DiodeDevice.from_dict()`) → Complex patterns (`BatchProcessor`, custom validators) when needed.

---

## File Structure & Complexity

| File | Lines | Responsibility |
|------|-------|----------------|
| `models/` | ~1,500 total | Pydantic data models |
| `converter.py` | 756 | Model → SDK conversion |
| `client.py` | 430 | gRPC client abstraction |
| `batch.py` | 388 | Batch processing |
| `importer.py` | 408 | Import from file/API |
| `export.py` | 280 | Export to file |
| `validators/*.py` | 755 | Validation framework |
| `quality/*.py` | 642 | Quality metrics |
| `caching/*.py` | 766 | Caching layer |
| `progress/manager.py` | 327 | Progress tracking |
| `cli/app.py` | 316 | CLI entrypoint |
| **Total** | **~8,000+** | |

---

## Maintenance Guide

### When SDK Updates

1. Check [DIODE_SDK_USAGE.md](./DIODE_SDK_USAGE.md) for SDK field signatures
2. Verify model field names match SDK expectations
3. Test `to_protobuf()` functions
4. Update converter if field positions/types change

### When Adding New Entity Type

1. Add Pydantic model to `models/<type>.py`
2. Add `to_protobuf()` method
3. Add `convert_<type>()` function in `converter.py`
4. Update `models/__init__.py` exports
5. Add to `convert_device_with_subcomponents()` if nested on Device
6. Write tests

### Inheritance Patterns

**rack_positions with site/location inheritance:**
```python
# Helper method: get_rack_positions_with_inheritance()
# Resolves rack position entries:
# - 'site': defaults to device.site if not specified
# - 'location': defaults to device.location if not specified
```

### Common SDK Gotchas

- `Interface.untagged_vlan` = **VLAN object**, not string
- `Cable.a_terminations` = **list[GenericObject]**, not bare strings
- `GenericObject` uses setters like `object_device=Device(...)`

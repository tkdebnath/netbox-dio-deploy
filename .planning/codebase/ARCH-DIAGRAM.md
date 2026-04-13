# NetBox Diode Wrapper - Architecture Diagram

## High-Level View

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         User Code (Your Application)                      │   │
│  │                                                                           │   │
│  │  from netbox_dio import DiodeDevice, DiodeClient, convert_device...      │   │
│  │                                                                           │   │
│  │  device = DiodeDevice.from_dict({...})           # Simple dict → model   │   │
│  │  entities = convert_device_to_entities(device)   # Model → SDK types    │   │
│  │  client = DiodeClient.from_env()                  # Env config          │   │
│  │  client.send_batch(entities)                        # Transmission      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         USER FACING API                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   models/       │  │   export.py     │  │   importer.py   │                 │
│  │                 │  │                 │  │                 │                 │
│  │ ✓ DiodeDevice   │  │ ✓ to_json()     │  │ ✓ from_dict()   │                 │
│  │ ✓ DiodeInterface│  │ ✓ to_yaml()     │  │ ✓ import_json() │                 │
│  │ ✓ DiodeVLAN     │  │ ✓ to_netbox()   │  │ ✓ import_yaml() │                 │
│  │ ✓ DiodeModule   │  │                 │  │ ✓ from_api()    │                 │
│  │ ✓ DiodeCable    │  │                 │  │                 │                 │
│  │ ...             │  │                 │  │                 │                 │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘                 │
│           │                    │                    │                           │
│           └────────────────────┼────────────────────┘                           │
│                                │                                                │
│                                ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    batch.py & clients.py                              │   │
│  │                                                                           │   │
│  │  ✓ BatchProcessor - automatic 1000-device chunking                    │   │
│  │  ✓ DiodeClient - simplified send_single/send_batch                    │   │
│  │  ✓ ConnectionConfig - env-based gRPC config                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CONVERSION LAYER                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    converter.py                                         │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  convert_device(device) → Entity(device=Device(...))          │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                           │                                              │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  convert_device_to_entities(device) → [Entity, Entity, ...]    │   │   │
│  │  │     ├─ Device entity                                              │   │   │
│  │  │     ├─ All interfaces                                              │   │   │
│  │  │     ├─ All VLANs                                                   │   │   │
│  │  │     ├─ All modules                                                 │   │   │
│  │  │     ├─ All module bays                                             │   │   │
│  │  │     ├─ All cables                                                  │   │   │
│  │  │     └─ All prefixes/IPs                                            │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │  convert_interface() │ convert_vlan() │ convert_module() │ ...  │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          ABSTRACTION LAYER                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   validators/   │  │   quality/      │  │   caching/      │                 │
│  │                 │  │                 │  │                 │                 │
│  │ ✓ RulePipeline  │  │ ✓ QualityMetrics│  │ ✓ CacheBackend  │                 │
│  │ ✓ Custom Rules  │  │ ✓ QualityReport │  │ ✓ RedisCache    │                 │
│  │ ✓ Validation    │  │                 │  │ ✓ MemoryCache   │                 │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │  progress/manager.py                                                  │    │
│  │  ✓ Progress tracking (Rich UI or MockFallback for headless)         │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │              netboxlabs-diode-sdk (v1.10.0)                             │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  SDK protobuf types (Entity, Device, Interface, VLAN, etc.)   │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  DiodeClient (raw gRPC client from SDK)                 ──────▶  │    │   │
│  │  │                                  │                              │    │   │
│  │  │  Diode SDK does NOT provide:                                    │    │   │
│  │  │  - Nested device parsing                                        │    │   │
│  │  │  - Device-centric API                                           │    │   │
│  │  │  - Batch processing logic                                       │    │   │
│  │  │  - Custom validation                                            │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          NETWORK LAYER                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          gRPC protocol                                  │   │
│  │  (Secure, binary, well-defined API contracts)                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                NETBOX DIODE INGESTION ENDPOINT                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  netbox-diode.example.com:50051                                          │   │
│  │  ────────────────────────────────────────────────────────────────────  │   │
│  │  Receives Entity messages and writes to NetBox                           │   │
│  │  vertices/dcim.devices, vertices/dcim.interfaces, etc.                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Simplified Flow (Common Use Case)

```
User Dict                Pydantic SDK
────────                 ────────
────────                 ────────
# User code:
device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "site-a",
    "device_type": "cisco-9300",
    "role": "core",
    "interfaces": [
        {"name": "eth0", "device": "router-01", "type": "physical"}
    ]
})

# Conversion happens internally
entities = convert_device_to_entities(device)
# 1. Convert Device - DiodeDevice → Device protobuf
# 2. Convert Interfaces - iterate device.interfaces → Interface protobuf
# 3. Wrap each in Entity(xxx=...)

# Send
client = DiodeClient.from_env()
client.send_batch(entities)
```

## Rack/Location Inheritance for Clustered Devices

```python
# Primary device (first stack member)
device = DiodeDevice.from_dict({
    "name": "core-switch-stack",
    "site": "dc-east",
    "location": "building-a",          # Primary location
    "device_type": "cisco-c9300",
    "role": "core",
    "rack": "rack-01",
    "position": 10.0,
    "rack_positions": [
        # Entries without site/location inherit from device
        {"rack": "rack-01", "position": 10.0},     # Inherits site=dc-east, loc=building-a
        {"rack": "rack-01", "position": 12.0},     # Inherits site=dc-east, loc=building-a
        # Entries can override site/location
        {"rack": "rack-02", "position": 8.0, "site": "dc-west"},  # Override site
        {"rack": "rack-02", "position": 10.0, "location": "build-b"},  # Override location
    ],
})

# Use helper to get resolved positions
resolved = device.get_rack_positions_with_inheritance()
# Returns list with all site/location fields filled
```

---

## Component Responsibilities

| Component | What It Does | What It Doesn't Do |
|-----------|-------------|-------------------|
| **Pydantic Models** | Validate & coerce data types | Direct SDK interaction |
| **converter.py** | Translate models to SDK types | Network I/O, persistence |
| **client.py** | gRPC connection & send | Data validation |
| **batch.py** | Chunk & retry logic | Entity conversion |
| **Validator Pipeline** | Rule-based validation | Data transformation |
| **quality/** | Metrics calculation | Data modification |

---

## Replacement Scenarios

| Component | Can Be Replaced With | Why You Might |
|-----------|---------------------|---------------|
| `DiodeDevice` | Custom dict parser | If Pydantic is too heavy |
| `converter.py` | Direct SDK calls | For max performance |
| `DiodeClient` | Custom gRPC client | Different auth/metrics |
| `BatchProcessor` | Custom chunking | Different size/grouping |

The wrapper is designed so you can easily drop components while keeping the benefit of Pydantic validation.

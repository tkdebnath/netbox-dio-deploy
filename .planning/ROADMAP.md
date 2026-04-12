# Roadmap: NetBox Diode Device Wrapper

**Created:** 2026-04-12
**Granularity:** standard
**Target:** Python 3.10+

## Phases

- [x] **Phase 1: Core Model** - Pydantic DiodeDevice with mandatory field validation and device attributes
- [ ] **Phase 2: Converter Layer** - Transform Pydantic models to Diode Entity protobuf messages
- [ ] **Phase 3: Device Subcomponents** - Interfaces, VLANs, Modules, Cables, Prefixes, IP addresses
- [ ] **Phase 4: I/O Layer** - DiodeClient wrapper for gRPC transmission with batch support
- [ ] **Phase 5: Validation & Error Handling** - Comprehensive exception handling and edge case coverage

## Phase Details

### Phase 1: Core Model
**Goal**: Build a fully validated Pydantic DiodeDevice class that enforces mandatory fields and supports all device-level attributes
**Depends on**: Nothing (foundation phase)
**Requirements**: CORE-01, CORE-02, CORE-04, CORE-05, DEV-01, DEV-02, DEV-03, DEV-04, DEV-05, DEV-06, DEV-07, DEV-08
**Success Criteria** (what must be TRUE):
  1. User can create a DiodeDevice instance with mandatory fields (name, site, device_type, role) and validation raises TypeError/ValueError for missing fields
  2. User can parse a nested dictionary into a DiodeDevice using from_dict() method
  3. User can configure optional device attributes (serial, asset_tag, platform, status, custom_fields, business_unit)
  4. Pydantic validation enforces type correctness at initialization time
**Plans**: 2 plans
**UI hint**: no

Plans:
- [x] 01-01-PLAN.md — Create DiodeDevice Pydantic model with mandatory fields
- [x] 01-02-PLAN.md — Create test infrastructure (Wave 0)

### Phase 2: Converter Layer
**Goal**: Transform validated Pydantic models into Diode SDK Entity protobuf messages for gRPC transmission
**Depends on**: Phase 1
**Requirements**: CORE-03
**Success Criteria** (what must be TRUE):
  1. User can convert a DiodeDevice to a Diode Entity protobuf message
  2. Converter produces valid protobuf messages compatible with Diode SDK
  3. Nested Pydantic objects (interfaces, VLANs) convert to separate Diode Entity objects (not nested)
**Plans**: TBD
**UI hint**: no

### Phase 3: Device Subcomponents
**Goal**: Implement full support for device subcomponents as first-class Pydantic models
**Depends on**: Phase 1
**Requirements**: INTF-01, INTF-02, INTF-03, INTF-04, INTF-05, INTF-06, VLAN-01, VLAN-02, VLAN-03, VLAN-04, MOD-01, MOD-02, MOD-03, MOD-04, CABLE-01, CABLE-02, CABLE-03, PREFIX-01, PREFIX-02, PREFIX-03, IP-01, IP-02, IP-03
**Success Criteria** (what must be TRUE):
  1. User can define interfaces with type-specific attributes (physical, virtual, LAG, wireless)
  2. User can assign VLANs to interfaces (untagged/tagged)
  3. User can manage module bays with module specifications
  4. User can define cable relationships between device termination points
  5. User can manage IP prefixes with IPv4/IPv6 support
  6. User can assign primary and secondary IP addresses to devices
**Plans**: TBD
**UI hint**: no

### Phase 4: I/O Layer
**Goal**: Implement DiodeClient wrapper for gRPC transmission with environment-based configuration and batch operations
**Depends on**: Phase 2, Phase 3
**Requirements**: CORE-06, CORE-08, BATCH-01, BATCH-02, BATCH-03, BATCH-04
**Success Criteria** (what must be TRUE):
  1. User can configure gRPC connection via environment variables (endpoint, client_id, client_secret)
  2. User can send single device payloads to Diode via the client
  3. User can batch multiple devices and have them automatically chunked (>1000 devices)
  4. Batch operations provide per-device error reporting
  5. User can send batched payloads to Diode via create_message_chunks()
**Plans**: TBD
**UI hint**: no

### Phase 5: Validation & Error Handling
**Goal**: Comprehensive exception-based error handling and edge case coverage
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4
**Requirements**: CORE-07
**Success Criteria** (what must be TRUE):
  1. Invalid data raises ValueError or TypeError with descriptive messages
  2. gRPC connection failures raise specific exceptions with actionable information
  3. Conversion errors provide clear traceback to source data
  4. Batch processing reports individual device failures without stopping entire batch
**Plans**: TBD
**UI hint**: no

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Model | 2/2 | Planned | - |
| 2. Converter Layer | 0/1 | Not started | - |
| 3. Device Subcomponents | 0/5 | Not started | - |
| 4. I/O Layer | 0/3 | Not started | - |
| 5. Validation & Error Handling | 0/2 | Not started | - |

# Requirements: NetBox Diode Device Wrapper

**Defined:** 2026-04-12
**Core Value:** Enable network automation engineers to define network devices as Python dictionaries and push them to NetBox Diode with minimal code, while enforcing data integrity and validation.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Core

- [ ] **CORE-01**: `DiodeDevice` class must enforce mandatory fields (name, site, device_type, role) on initialization
- [ ] **CORE-02**: `DiodeDevice.from_dict()` class method must parse the exact nested dictionary structure provided
- [ ] **CORE-03**: Package must use `netboxlabs-diode-sdk` as the base dependency
- [ ] **CORE-04**: Package must use `pydantic` for schema validation
- [ ] **CORE-05**: Target Python 3.10+
- [x] **CORE-06**: Configuration via environment variables for Diode gRPC connection (endpoint, client_id, client_secret)
- [ ] **CORE-07**: Error reporting via exceptions (ValueError/TypeError) for validation failures
- [x] **CORE-08**: Support for batch operations across multiple device dictionaries

### Device Structure

- [ ] **DEV-01**: Support device name, serial number, and asset tag
- [ ] **DEV-02**: Support device_type with manufacturer reference
- [ ] **DEV-03**: Support device role assignment
- [ ] **DEV-04**: Support platform specification
- [ ] **DEV-05**: Support site assignment
- [ ] **DEV-06**: Support status field (active, offline, planned)
- [ ] **DEV-07**: Support custom fields (arbitrary metadata)
- [ ] **DEV-08**: Support business unit mapping to custom_fields

### Interfaces

- [x] **INTF-01**: Interface parsing with type-specific handling (physical, virtual, LAG, wireless)
- [x] **INTF-02**: Interface description field support
- [x] **INTF-03**: Interface enabled/disabled state
- [x] **INTF-04**: Interface MTU configuration
- [x] **INTF-05**: Interface speed/type specification
- [x] **INTF-06**: Interface VLAN assignment (untagged/tagged)

### VLANs

- [x] **VLAN-01**: VLAN creation with VID and name
- [x] **VLAN-02**: VLAN status management (active, reserved, deprecated)
- [x] **VLAN-03**: VLAN group assignment
- [x] **VLAN-04**: Site assignment for VLANs

### Modules

- [x] **MOD-01**: Module bay parsing and management
- [x] **MOD-02**: Module type specification
- [x] **MOD-03**: Module serial number tracking
- [x] **MOD-04**: Module status management

### Cables

- [x] **CABLE-01**: Cable relationship mapping between devices
- [x] **CABLE-02**: Termination port specification (source/destination)
- [x] **CABLE-03**: Cable type specification

### Prefixes

- [x] **PREFIX-01**: Prefix management with IPv4/IPv6 support
- [x] **PREFIX-02**: Prefix status management
- [x] **PREFIX-03**: Prefix scope assignment (site, site-group, region)

### IP Addresses

- [x] **IP-01**: IP interface management (IP address on interface)
- [x] **IP-02**: Primary IP assignment
- [x] **IP-03**: Secondary IP support

### Batch Operations

- [x] **BATCH-01**: Parse multiple devices from dictionary
- [x] **BATCH-02**: Batch ingestion via Diode SDK
- [x] **BATCH-03**: Automatic chunking for large batches (>1000 devices)
- [x] **BATCH-04**: Error reporting per device in batch

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Features

- [ ] **ADV-01**: Virtual chassis management
- [ ] **ADV-02**: OOB IP management
- [ ] **ADV-03**: LAG/bridge support
- [ ] **ADV-04**: Wireless LAN support
- [ ] **ADV-05**: RF channel configuration
- [ ] **ADV-06**: VRF management
- [ ] **ADV-07**: Cable trace/validation
- [ ] **ADV-08**: Configuration management

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Direct NetBox REST API CRUD | Create dual-path complexity; this wrapper is Diode-only for writes |
| Delete operations | Diode is primarily for data ingestion; use NetBox REST API for deletions |
| Web UI/dashboard | Distracts from core value (automation library) |
| OAuth authentication | Environment variables for credentials are sufficient |
| Full real-time sync | Complex; period sync with conflict resolution is simpler |
| Full NetBox feature parity | Focus on device-centric subset, not every NetBox field |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 1 | Pending |
| CORE-02 | Phase 1 | Pending |
| CORE-03 | Phase 2 | Pending |
| CORE-04 | Phase 1 | Pending |
| CORE-05 | Phase 1 | Pending |
| CORE-06 | Phase 4 | Complete |
| CORE-07 | Phase 5 | Pending |
| CORE-08 | Phase 4 | Complete |
| DEV-01 | Phase 1 | Pending |
| DEV-02 | Phase 1 | Pending |
| DEV-03 | Phase 1 | Pending |
| DEV-04 | Phase 1 | Pending |
| DEV-05 | Phase 1 | Pending |
| DEV-06 | Phase 1 | Pending |
| DEV-07 | Phase 1 | Pending |
| DEV-08 | Phase 1 | Pending |
| INTF-01 | Phase 3 | Complete |
| INTF-02 | Phase 3 | Complete |
| INTF-03 | Phase 3 | Complete |
| INTF-04 | Phase 3 | Complete |
| INTF-05 | Phase 3 | Complete |
| INTF-06 | Phase 3 | Complete |
| VLAN-01 | Phase 3 | Complete |
| VLAN-02 | Phase 3 | Complete |
| VLAN-03 | Phase 3 | Complete |
| VLAN-04 | Phase 3 | Complete |
| MOD-01 | Phase 3 | Complete |
| MOD-02 | Phase 3 | Complete |
| MOD-03 | Phase 3 | Complete |
| MOD-04 | Phase 3 | Complete |
| CABLE-01 | Phase 3 | Complete |
| CABLE-02 | Phase 3 | Complete |
| CABLE-03 | Phase 3 | Complete |
| PREFIX-01 | Phase 3 | Complete |
| PREFIX-02 | Phase 3 | Complete |
| PREFIX-03 | Phase 3 | Complete |
| IP-01 | Phase 3 | Complete |
| IP-02 | Phase 3 | Complete |
| IP-03 | Phase 3 | Complete |
| BATCH-01 | Phase 4 | Complete |
| BATCH-02 | Phase 4 | Complete |
| BATCH-03 | Phase 4 | Complete |
| BATCH-04 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 49 total
- Mapped to phases: 49
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-12*
*Last updated: 2026-04-12 after roadmap creation*
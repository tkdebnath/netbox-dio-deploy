# NetBox Diode Device Wrapper

## What This Is

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox. This package parses nested dictionary structures into typed objects and generates Diode payloads for gRPC transmission.

## Core Value

Enable network automation engineers to define network devices as Python dictionaries and push them to NetBox Diode with minimal code, while enforcing data integrity and validation.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **CORE-01**: `DiodeDevice` class must enforce mandatory fields (name, site, device_type, role) on initialization
- [ ] **CORE-02**: `DiodeDevice.from_dict()` class method must parse the exact nested dictionary structure
- [ ] **CORE-03**: Package must use `netboxlabs-diode-sdk` as the base dependency
- [ ] **CORE-04**: Package must use `pydantic` for schema validation
- [ ] **CORE-05**: Target Python 3.10+
- [ ] **CORE-06**: Configuration via environment variables for Diode gRPC connection
- [ ] **CORE-07**: Error reporting via exceptions (ValueError/TypeError)
- [ ] **CORE-08**: Support for batch operations across multiple device dictionaries
- [ ] **INTF-01**: Interface parsing with type-specific handling
- [ ] **INTF-02**: VLAN parsing and management
- [ ] **MOD-01**: Module bay parsing and management
- [ ] **CABLE-01**: Cable relationship mapping
- [ ] **PREFIX-01**: Prefix management
- [ ] **IP-01**: IP interface management

### Out of Scope

- Direct NetBox API CRUD operations — this wrapper is Diode-only
- Delete operations — initial focus is on create/update via Diode
- Web UI or web-based interface — pure Python library
- OAuth or complex authentication — environment-based gRPC credentials only

## Context

This project addresses the complexity of the raw Diode SDK by providing:
- A device-centric data structure that mirrors how network engineers think about devices
- Automatic payload generation for Diode gRPC
- Validation and error handling at the object level
- Type-safe interfaces, VLANs, modules, and cables as first-class objects

The wrapper will be used in network automation scripts, CI/CD pipelines, and infrastructure-as-code workflows where defining devices as dictionaries is more natural than constructing Diode proto messages directly.

## Constraints

- **Tech Stack**: Must use `netboxlabs-diode-sdk` and `pydantic`
- **Python Version**: 3.10+ (must support f-strings, dataclasses, type hints)
- **Connection**: Environment variables for Diode endpoint/credentials
- **Error Handling**: Exception-based (no silent failures)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Device-centric dictionary structure | Engineers think in devices, not gRPC messages | Intuitive API for network teams |
| Pydantic for validation | Type safety, schema validation, runtime checking | Data integrity enforced at parse time |
| Structured package layout | Subpackages for devices, interfaces, vlans, etc. | Maintainable codebase as features grow |
| Exception-based error reporting | Fails fast, clear error messages | Debug-friendly during development |
| Environment variable config | Standard for containerized/automated envs | Easy integration with CI/CD and Kubernetes |

---
*Last updated: 2026-04-12 after initialization*

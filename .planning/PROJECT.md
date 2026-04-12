# NetBox Diode Device Wrapper

## What This Is

A high-level Python wrapper package for the NetBox Diode SDK that provides a "Device-Centric" simplified interface for managing network infrastructure data in NetBox. This package parses nested dictionary structures into typed objects and generates Diode payloads for gRPC transmission.

## Core Value

Enable network automation engineers to define network devices as Python dictionaries and push them to NetBox Diode with minimal code, while enforcing data integrity and validation.

## Current State

**Shipped:** v1.0 MVP (2026-04-12)

The package is fully functional with:
- Pydantic `DiodeDevice` model with mandatory field validation
- Converter module for Pydantic-to-Protobuf conversion
- Complete subcomponent support (interfaces, VLANs, modules, cables, prefixes, IPs)
- I/O layer with gRPC client and batch processing
- Comprehensive exception hierarchy with 9 error types

**Next Milestone:** v1.1 (2026-04-12)

New features for v1.1:
- CLI tool for importing/exporting device data from JSON/YAML files
- Models for racks, PDUs, power circuits, and power feeds
- Export to JSON, YAML, and NetBox YAML format for easy data exchange
- Import existing NetBox data via API for migration/backup workflows

## Requirements

### Validated

- ✓ **CORE-06**: Configuration via environment variables for Diode gRPC connection — v1.0
- ✓ **CORE-07**: Error reporting via exceptions (ValueError/TypeError) — v1.0
- ✓ **CORE-08**: Support for batch operations across multiple device dictionaries — v1.0
- ✓ **INTF-01** to **INTF-06**: Interface parsing with type-specific handling — v1.0
- ✓ **VLAN-01** to **VLAN-04**: VLAN parsing and management — v1.0
- ✓ **MOD-01** to **MOD-04**: Module bay parsing and management — v1.0
- ✓ **CABLE-01** to **CABLE-03**: Cable relationship mapping — v1.0
- ✓ **PREFIX-01** to **PREFIX-03**: Prefix management with IPv4/IPv6 support — v1.0
- ✓ **IP-01** to **IP-03**: IP interface management — v1.0

### Active

- [ ] **CLI-01**: Command-line interface for importing/exporting device data from JSON/YAML files
- [ ] **CLI-02**: Support for dry-run mode with output to stdout or file
- [ ] **CLI-03**: Batch processing with configurable chunk size via CLI
- [ ] **RACK-01**: Rack model with position, type, and serial attributes
- [ ] **RACK-02**: Rack unit (RU) allocation tracking
- [ ] **POWER-01**: PDU model with outlet configuration
- [ ] **POWER-02**: Power circuit model with voltage and amperage
- [ ] **POWER-03**: Power feed model with phase and capacity
- [ ] **EXPORT-01**: Export to JSON format with optional pretty-printing
- [ ] **EXPORT-02**: Export to YAML format (NetBox-compatible)
- [ ] **EXPORT-03**: Export to NetBox YAML format with device templates
- [ ] **IMPORT-01**: Import from NetBox API with filter support
- [ ] **IMPORT-02**: Import from existing JSON/YAML files
- [ ] **IMPORT-03**: Import with validation against schema

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
- CLI tool for easy integration with shell scripts and automation tools
- Rack and power models for comprehensive infrastructure modeling
- Multiple export formats for data exchange and backup

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
*Last updated: 2026-04-12 after v1.0 milestone*

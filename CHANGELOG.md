# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive quality metrics module with completeness and validity scoring
- Exportable mixin for JSON/YAML serialization on all model types
- NetBox YAML export format support
- QualityReporter for human-readable quality reports

### Changed
- Replaced monkey-patched export methods with proper mixin classes
- Eliminated dead `convert_device_with_power()` function

### Fixed
- Resolved circular import issues in quality module
- Standardized import styles across quality package

## [0.1.0] - 2026-04-12

### Added
- Core Pydantic v2 models for all network device types (Device, Interface, VLAN, Module, ModuleBay, Cable, Prefix, IPAddress, Rack, PDU, Circuit, PowerFeed)
- DiodeClient wrapper with gRPC transmission support
- Batch processing with automatic chunking (>1000 devices)
- CLI tool with import/export/dry-run/batch commands
- Comprehensive exception hierarchy (9 exception classes)
- Validation framework with configurable rules and severity levels
- JSON, YAML, and NetBox YAML export formats
- JSON and YAML import from files and stdin
- Data quality metrics with completeness and validity scoring
- Rack location inheritance for clustered devices

### Features
- Environment variable configuration for gRPC client
- Dry-run mode for testing without actual transmission
- Per-device error reporting in batch operations
- Type-safe interfaces for all network object types

[unreleased]: https://github.com/netboxlabs/diode-device-wrapper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/netboxlabs/diode-device-wrapper/releases/tag/v0.1.0

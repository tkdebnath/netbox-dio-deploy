# Roadmap: NetBox Diode Device Wrapper

**Created:** 2026-04-12
**Granularity:** standard
**Target:** Python 3.10+

## Milestones

- [x] **v1.0 MVP** — Phases 1-5 (shipped 2026-04-12)
- [ ] **v1.1** — CLI tool, Racks & Power, Export/Import (Phase 7 done, Phase 8 planned)

## Phases

<details>
<summary><strong>✅ v1.0 MVP (Phases 1-5) — SHIPPED 2026-04-12</strong></summary>

### Phase 1: Core Model
**Goal**: Build a fully validated Pydantic DiodeDevice class that enforces mandatory fields and supports all device-level attributes
**Depends on**: Nothing (foundation phase)
**Plans**: 2 plans
- [x] 01-01-PLAN.md — Create DiodeDevice Pydantic model with mandatory fields
- [x] 01-02-PLAN.md — Create test infrastructure (Wave 0)

### Phase 2: Converter Layer
**Goal**: Transform validated Pydantic models into Diode SDK Entity protobuf messages for gRPC transmission
**Depends on**: Phase 1
**Plans**: 1 plan
- [x] 02-01-PLAN.md — Converter module with device-to-Entity conversion and test suite

### Phase 3: Device Subcomponents
**Goal**: Implement full support for device subcomponents as first-class Pydantic models
**Depends on**: Phase 1
**Plans**: 1 plan
- [x] 03-01-PLAN.md — Create Pydantic models for interfaces, VLANs, modules, cables, prefixes, and IP addresses with converter functions

### Phase 4: I/O Layer
**Goal**: Implement DiodeClient wrapper for gRPC transmission with environment-based configuration and batch operations
**Depends on**: Phase 2, Phase 3
**Plans**: 1 plan
- [x] 04-01-PLAN.md — DiodeClient with environment config, batch processor, create_message_chunks()

### Phase 5: Validation & Error Handling
**Goal**: Comprehensive exception-based error handling and edge case coverage
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4
**Plans**: 1 plan
- [x] 05-01-PLAN.md — Exception hierarchy, validation, conversion, I/O, batch error handling

</details>

### Phase 6: CLI Module
**Goal**: Command-line interface for importing/exporting device data
**Depends on**: Phase 1-5
**Requirements**: CLI-01, CLI-02, CLI-03
**Plans**: TBD

### Phase 7: Racks & Power
**Goal**: Models for racks, PDUs, power circuits, and power feeds
**Depends on**: Phase 1-5
**Requirements**: RACK-01, RACK-02, POWER-01, POWER-02, POWER-03
**Plans**: 1 plan
- [x] 07-01-PLAN.md — Create Pydantic models for racks, PDUs, circuits, power feeds with converter functions

### Phase 8: Export/Import
**Goal**: Export to multiple formats and import from NetBox API/files
**Depends on**: Phase 1-5
**Requirements**: EXPORT-01, EXPORT-02, EXPORT-03, IMPORT-01, IMPORT-02, IMPORT-03
**Plans**: 1 plan
- [x] 08-01-PLAN.md — Export to JSON/YAML, import from NetBox API/files

| 7. Racks & Power | 1/1 | Completed | 2026-04-12 |
| 8. Export/Import | 1/1 | Completed | 2026-04-12 |

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Model | 2/2 | Completed | 2026-04-12 |
| 2. Converter Layer | 1/1 | Completed | 2026-04-12 |
| 3. Device Subcomponents | 1/1 | Completed | 2026-04-12 |
| 4. I/O Layer | 1/1 | Completed | 2026-04-12 |
| 5. Validation & Error Handling | 1/1 | Completed | 2026-04-12 |
| 6. CLI Module | 0/6 | Planned    |  |
| 7. Racks & Power | 1/1 | Completed | 2026-04-12 |
| 8. Export/Import | 1/1 | Completed | 2026-04-12 |

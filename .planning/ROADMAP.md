# Roadmap: NetBox Diode Device Wrapper

**Created:** 2026-04-12
**Granularity:** standard
**Target:** Python 3.10+

## Milestones

- [x] **v1.0 MVP** — Phases 1-5 (shipped 2026-04-12)

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

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Model | 2/2 | Completed | 2026-04-12 |
| 2. Converter Layer | 1/1 | Completed | 2026-04-12 |
| 3. Device Subcomponents | 1/1 | Completed | 2026-04-12 |
| 4. I/O Layer | 1/1 | Completed | 2026-04-12 |
| 5. Validation & Error Handling | 1/1 | Completed | 2026-04-12 |

# Milestones

## v1.1 CLI, Racks & Power, Export/Import (Shipped: 2026-04-12)

**Phases completed:** 3 phases, 8 plans, 6 tasks

**Key accomplishments:**

- Pydantic models for racks, PDUs, power circuits, and power feeds with Diode SDK protobuf conversion
- Phase:

---

## v1.0 MVP (Shipped: 2026-04-12)

**Phases completed:** 5 phases, 6 plans, 28 tasks

**Key accomplishments:**

- Test scaffolding for DiodeDevice model with 11 test functions and 4 pytest fixtures
- Pydantic model for Diode Device with mandatory field validation and protobuf conversion
- Converter module transforming Pydantic DiodeDevice to Diode Entity protobuf messages for gRPC transmission
- Complete set of Pydantic models and conversion functions for device subcomponents
- Comprehensive exception hierarchy with 9 classes, enhanced validation with field-level context, converter error wrapping with source data, I/O layer error categorization, and batch error aggregation

---

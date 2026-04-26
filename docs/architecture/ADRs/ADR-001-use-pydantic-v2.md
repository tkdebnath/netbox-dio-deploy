# ADR-001: Use Pydantic v2 for Model Validation

**Date:** 2026-04-12
**Status:** Accepted
**Context:** We need a robust way to validate and serialize network device data. Options included: custom validation logic, dataclasses, Pydantic v1, Pydantic v2, or protobuf directly.

**Decision:** Use Pydantic v2 for all model validation and serialization. Pydantic v2 provides better performance than v1, native support for Python 3.10+ type hints, and seamless integration with dataclasses. It also generates JSON schema automatically, which aids in API documentation.

**Consequences:**
- Benefits: Fast validation, excellent serialization, auto-generated schemas, modern Python syntax support
- Trade-offs: Adds a dependency (pydantic>=2.12.0), but this is already a transitive dependency of the Diode SDK
- Migration: Future Pydantic v3 migrations will be straightforward due to v2's stability

**Alternatives Considered:**
- Dataclasses: Less validation, no schema generation
- Protobuf directly: Too verbose, no validation
- Custom validation: High maintenance, error-prone

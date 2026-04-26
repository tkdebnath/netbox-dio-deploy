# ADR-002: Converter Layer Design for Protobuf Conversion

**Date:** 2026-04-12
**Status:** Accepted
**Context:** The Diode SDK uses protobuf messages for gRPC transmission. We need to convert our Pydantic models to protobuf messages efficiently.

**Decision:** Implement a converter layer that maps Pydantic model fields to protobuf message fields. Each model type has a dedicated conversion function. The main entry point is `convert_device_to_entities()` which converts a DiodeDevice and all its subcomponents into a list of Entity protobuf messages.

**Consequences:**
- Benefits: Clear separation of concerns, easy to test each converter function independently, simple to add new model types
- Trade-offs: Manual field mapping required, but this gives precise control over protobuf field population
- Error handling: Each converter wraps exceptions in DiodeConversionError with full context

**Implementation:**
- `convert_device()` - Converts Device model to Entity
- `convert_interface()` - Converts Interface model to Entity
- `convert_vlan()` - Converts VLAN model to Entity
- `convert_module()` - Converts Module model to Entity
- `convert_module_bay()` - Converts ModuleBay model to Entity
- `convert_cable()` - Converts Cable model to Entity
- `convert_prefix()` - Converts Prefix model to Entity
- `convert_ip_address()` - Converts IPAddress model to Entity
- `convert_device_to_entities()` - Main entry, converts device + all subcomponents

**Alternatives Considered:**
- Single monolithic converter: Harder to test, single point of failure
- Dynamic field mapping: Less control over output, harder to debug

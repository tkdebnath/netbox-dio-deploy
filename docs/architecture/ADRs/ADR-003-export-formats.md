# ADR-003: Export Formats and Serialization

**Date:** 2026-04-12
**Status:** Accepted
**Context:** Users need to export device data in multiple formats for different use cases: JSON for API integration, YAML for human readability, and NetBox YAML for direct NetBox import.

**Decision:** Support three export formats with dedicated functions:
- `to_json()` - JSON serialization with pretty print option
- `to_yaml()` - YAML serialization for human-readable output
- `to_netbox_yaml()` - NetBox-compatible YAML format for direct import

All export functions work on either raw dictionaries or Pydantic model objects. The export module uses mixin classes (ExportableMixin, NetBoxYamlMixin) applied at import time to all relevant model classes, avoiding monkey-patching issues.

**Consequences:**
- Benefits: Multiple export formats, clean API, easy to extend with new formats
- Trade-offs: Some formats require format-specific model preparation (e.g., NetBox YAML needs special field handling)
- Testing: All export formats have comprehensive test coverage

**Implementation:**
```python
from netbox_dio import export_devices, to_json, to_yaml, to_netbox_yaml

# Simple export functions
json_output = to_json(devices)
yaml_output = to_yaml(devices, pretty=True)
netbox_output = to_netbox_yaml(devices)

# Unified export function
export_devices(devices, format="json")  # json, yaml, or netbox-yaml
```

**Alternatives Considered:**
- Single format with content-type negotiation: Requires HTTP context
- Custom serialization protocol: Unnecessary complexity for this use case

# Feature Landscape

**Domain:** Network automation wrapper for NetBox Diode SDK
**Researched:** 2026-04-12
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Device-centric dictionary parsing** | Engineers think in devices, not protobufs | LOW | Core value proposition - parse nested dicts to typed objects |
| **Mandatory field validation** | Data integrity is critical for network infrastructure | LOW | Name, site, device_type, role must be required |
| **Interface creation/manipulation** | Devices have interfaces - can't manage devices without them | MEDIUM | Support type, speed, mode, VLAN assignment |
| **VLAN management** | Network segmentation requires VLANs | LOW | Create, assign VLANs to interfaces |
| **Cable relationships** | Physical network topology needs cable mapping | HIGH | Requires port naming conventions and bidirectional matching |
| **Prefix management** | IP address planning requires prefixes | MEDIUM | Support IPv4/IPv6 prefixes with scope assignment |
| **IP address assignment** | Devices need IPs on interfaces | MEDIUM | Primary IPs, secondary IPs, IPAM integration |
| **Device type/manufacturer support** | Consistent device classification | LOW | Support manufacturer and model specification |
| **Site/region/location hierarchy** | Network geography matters | LOW | Site, location, rack assignment |
| **Status management** | State tracking (active, offline, planned) | LOW | Device, interface, VLAN status fields |
| **Tag system** | Flexible categorization | LOW | Tags on all entities for searching/filtering |
| **Custom fields** | Extensibility for vendor-specific data | MEDIUM | Support arbitrary metadata on entities |
| **Batch operations** | CI/CD and automation need bulk processing | MEDIUM | Support lists of devices for efficient processing |
| **Environment-based configuration** | Standard for containers/CI/CD | LOW | gRPC endpoint/credentials via environment variables |
| **Exception-based error handling** | Fail fast, clear errors | LOW | ValueError/TypeError for validation issues |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Structured object hierarchy** | Type-safe, validated data structures | MEDIUM | Pydantic models for devices, interfaces, VLANs, cables |
| **Module bay support** | Chassis module installation tracking | MEDIUM | Support line cards, fan trays, power supplies |
| **Virtual chassis management** | Stackable device handling | MEDIUM | VC position, priority, master election |
| **OOB IP management** | Out-of-band network separation | LOW | Separate management interface configuration |
| **LAG/bridge support** | Link aggregation and switching | MEDIUM | LACP, bridge domains, port channels |
| **Wireless LAN support** | WiFi infrastructure | MEDIUM | SSID, channel, power, role |
| **RF channel configuration** | Radio frequency management | HIGH | Channel frequency, width, power for wireless |
| **VRF management** | Routing table isolation | MEDIUM | VRF assignment to prefixes and interfaces |
| **Module support** | Pluggable module support | MEDIUM | SFP, QSFP transceivers and modules |
| **Cable trace/relationship validation** | Physical path verification | HIGH | Validate cable connections between devices |
| **Configuration management** | Device config capture | HIGH | Store and manage device configurations |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Direct NetBox API CRUD** | Familiar workflow for NetBox users | Creates dual-path complexity and sync issues | Use Diode for writes, REST API only for reads if needed |
| **Delete operations** | Standard CRUD pattern | Diode is primarily for data ingestion; deletes are rare in network automation | Use NetBox REST API for deletions, not Diode |
| **Web UI/dashboard** | Visual interface seems natural | Distracts from core value (automation library) | CLI tool or separate project if needed later |
| **OAuth/authentication** | Security is important | Over-engineering for internal automation tools | Environment variables for credentials are sufficient |
| **Full real-time sync** | Keep systems in sync | Complex to implement correctly; state drift is inevitable | Periodic sync with conflict resolution instead |
| **Full NetBox feature parity** | "Everything NetBox has" | Scope creep; Diode has different capabilities | Focus on device-centric subset, not every NetBox field |

## Feature Dependencies

```
Device
    ├──requires──> Site
    ├──requires──> DeviceType
    │   └──requires──> Manufacturer
    ├──requires──> Role
    ├──contains──> Interfaces
    │   ├──requires──> Interface Type
    │   ├──requires──> Device (parent)
    │   ├──can-have──> VLANs (untagged/tagged)
    │   ├──can-have──> Prefixes (IP addresses)
    │   └──can-have──> Modules
    ├──contains──> Module Bays
    │   └──can-contain──> Modules
    └──can-have──> Cables
        └──requires──> Two endpoints (A and Z)

VLAN
    ├──requires──> Site
    └──can-have──> Group

Prefix
    ├──requires──> VRF (optional)
    └──requires──> Scope (site/site-group/region)
```

### Dependency Notes

- **Device requires Site/DeviceType/Role:** These are core identifying attributes - cannot create a device without them
- **DeviceType requires Manufacturer:** A device type belongs to a manufacturer
- **Interface requires Device:** Interfaces belong to devices
- **Cables require two endpoints:** Cables connect two devices - implementation must handle this bidirectional requirement
- **IP prefixes require scope:** Prefixes must be assigned to a site, site-group, or region in NetBox

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] **Device class with mandatory fields** — Core value proposition, enables device-centric workflow
- [ ] **Dictionary-to-object parsing** — Converts engineer-friendly dicts to typed objects
- [ ] **Interface support** — Most common device component, essential for network config
- [ ] **Site/DeviceType/Role entities** — Required parent objects for devices
- [ ] **VLAN support** — Basic network segmentation
- [ ] **Batch operations** — CI/CD friendly bulk processing
- [ ] **Environment-based config** — Standard containerized deployment
- [ ] **Exception-based validation** — Fail fast with clear errors

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Cable relationships** — Physical network topology
- [ ] **Prefix management** — IP address planning
- [ ] **IP address assignment** — Primary/secondary IPs on interfaces
- [ ] **Module bay/module support** — Chassis modules
- [ ] **Virtual chassis** — Stackable devices
- [ ] **OOB IP support** — Out-of-band management
- [ ] **Custom fields** — Vendor-specific metadata

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Full configuration management** — Device config capture
- [ ] **Advanced RF configuration** — Wireless infrastructure
- [ ] **Cable trace/validation** — Physical path verification
- [ ] **Bridge/VLAN translation** — Complex switching topologies
- [ ] **Web UI** — Visual interface for ad-hoc editing

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Device class with validation | HIGH | LOW | P1 |
| Dictionary parsing | HIGH | LOW | P1 |
| Interface support | HIGH | MEDIUM | P1 |
| Site/DeviceType/Role | MEDIUM | LOW | P1 |
| VLAN support | MEDIUM | LOW | P1 |
| Batch operations | HIGH | MEDIUM | P1 |
| Environment config | MEDIUM | LOW | P1 |
| Exception handling | MEDIUM | LOW | P1 |
| Cable relationships | HIGH | HIGH | P2 |
| Prefix management | HIGH | MEDIUM | P2 |
| IP assignment | HIGH | MEDIUM | P2 |
| Module support | MEDIUM | MEDIUM | P2 |
| Virtual chassis | MEDIUM | MEDIUM | P2 |
| Custom fields | MEDIUM | MEDIUM | P2 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Existing Tools | Our Approach |
|---------|----------------|--------------|
| Device management | pynetbox, netbox-script, custom scripts | Device-centric dictionary parsing with Pydantic validation |
| Interface management | Manual protobuf construction | Typed Interface objects with type-specific handling |
| VLAN handling | Direct NetBox API | Integrated VLAN objects with site assignment |
| Cable connections | Manual port matching | Cable objects with endpoint resolution |
| Configuration | NetBox REST API, Nornir, napalm | Device payloads via Diode (create/update only) |
| Validation | Hand-written checks | Pydantic schema validation at parse time |
| Batch processing | Loops over API calls | Built-in chunking via Diode SDK |

## Sources

- NetBox Diode SDK v1.10.0 (netboxlabs-diode-sdk)
- Pydantic v2 documentation
- Project requirements in `.planning/PROJECT.md`
- NetBox data model documentation

---
*Feature research for: Network automation wrapper for NetBox Diode SDK*
*Researched: 2026-04-12*

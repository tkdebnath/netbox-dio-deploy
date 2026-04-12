# Research: Racks & Power Models

**Phase:** 07-racks-power  
**Date:** 2026-04-12  
**Target:** Python 3.10+

## Overview

This document provides the research foundation for implementing Rack, PDU, Power Circuit, and Power Feed models for the NetBox Diode Device Wrapper.

## Diode SDK Model Reference

The following table maps NetBox Diode requirements to available Diode SDK protobuf types:

| Requirement | Diode SDK Type | Key Fields | Notes |
|-------------|----------------|------------|-------|
| Rack | `Rack` | name, site, serial, asset_tag, rack_type, role, u_height, position | Supports mounting depth, weight, airflow, location |
| PDU | `PowerPanel` + `PowerFeed` | name, site, phase, amperage, voltage | PDU modeled as PowerPanel with PowerFeed |
| Power Circuit | `Circuit` | cid, name, type, provider, assignments | Circuit type from CircuitType |
| Power Feed | `PowerFeed` | name, phase, supply, amperage, voltage, capacity | PowerPanel reference required |

## Model Structure Definitions

### 1. DiodeRack

Based on `netboxlabs.diode.sdk.ingester.Rack`

**Required fields:**
- `name` - The rack name (e.g., "R1", "RACK-A1")
- `site` - The site name where rack is located
- `rack_type` - The rack type (e.g., "42u", "45u")

**Optional fields:**
- `serial` - Rack serial number
- `asset_tag` - Rack asset tag
- `role` - Rack role (e.g., "main-rack", "patch-panel")
- `u_height` - Number of RU (Rack Units) available
- `starting_unit` - Starting RU number (typically 1 or 48)
- `position` - Physical position in data center
- `description` - Rack description
- `status` - Status (active, planned, retired)
- `location` - Location within site
- `airflow` - Airflow direction (front-to-rear, rear-to-front)
- `form_factor` - Rack form factor
- `weight` / `weight_unit` - Rack weight specifications
- `mounting_depth` - Mounting depth in mm
- `outer_height` / `outer_depth` / `outer_width` - Physical dimensions
- `outer_unit` - Dimension unit
- `max_weight` - Maximum weight capacity
- `desc_units` - Whether units are numbered top-to-bottom
- `comments` - Additional comments
- `custom_fields` - Custom field values
- `metadata` - Metadata dictionary
- `owner` - Owner reference
- `tags` - List of tags
- `tenant` - Tenant reference

**Validation rules:**
- u_height should be positive (typically 24-48)
- Starting unit should be 1 or 48
- position should be positive integer
- name: 1-64 characters
- serial/asset_tag: 0-64 characters

### 2. DiodePDU

PDU is modeled using Diode SDK `PowerPanel` and `PowerFeed`:
- `PowerPanel` represents the power distribution panel
- `PowerFeed` represents individual power feeds from the panel

**Required fields (PowerPanel):**
- `name` - PDU name
- `site` - Site name

**Required fields (PowerFeed - for outlets):**
- `name` - Power outlet name
- `device` - Parent device reference
- `type` - Outlet type (e.g., "iec-309", "l14-30")

**Optional fields:**
- `serial` - PDU serial number
- `asset_tag` - PDU asset tag
- `role` - PDU role
- `status` - Status
- `amperage` - Maximum amperage
- `phase` - Phase type (single-phase, 2-phase, 3-phase)
- `voltage` - Voltage rating
- `power_port` - Parent power port (for daisy-chaining)
- `feed_leg` - Circuit leg (A, B, C)
- `color` - Outlet color code
- `description`, `comments`, `tags`, `custom_fields`, `metadata`, `owner`

**Validation rules:**
- amperage: 1-500 (typical 15-125A)
- voltage: 100-600 (typical 120V, 208V, 240V, 480V)
- phase: "single-phase", "2-phase", "3-phase"
- outlet type: standard IEC or NEMA types

### 3. DiodeCircuit

Based on `netboxlabs.diode.sdk.ingester.Circuit`

**Required fields:**
- `cid` - Circuit ID (unique identifier)
- `name` - Circuit name

**Optional fields:**
- `type` - Circuit type from CircuitType
- `provider` - Provider reference
- `provider_account` - Provider account reference
- `status` - Status (active, planned,退役)
- `assignments` - Circuit assignments (terminations)
- `install_date` - Installation date
- `commit_rate` - Commit rate in bps
- `distance` / `distance_unit` - Physical distance
- `tenant` - Tenant reference
- `description`, `comments`, `tags`, `custom_fields`, `metadata`, `owner`

**Validation rules:**
- cid: 1-64 characters, unique per provider
- name: 1-64 characters
- commit_rate: 0-100000000000 (0-100Gbps)

### 4. DiodePowerFeed

Based on `netboxlabs.diode.sdk.ingester.PowerFeed`

**Required fields:**
- `name` - Power feed name
- `power_panel` - Reference to PowerPanel

**Optional fields:**
- `phase` - Phase type (single-phase, 2-phase, 3-phase)
- `supply` - Supply type (ac, dc)
- `voltage` - Voltage (100-600V)
- `amperage` - Amperage (1-500A)
- `capacity` - Capacity in kVA
- `rack` - Rack reference
- `status` - Status
- `description`, `comments`, `tags`, `custom_fields`, `metadata`, `owner`

**Validation rules:**
- voltage: 100-600V
- amperage: 1-500A
- phase: "single-phase", "2-phase", "3-phase"
- capacity: 0-2000 kVA

## Implementation Pattern

Following existing patterns from `module.py`, `interface.py`, `vlan.py`:

1. Create model with Pydantic BaseModel
2. Define required fields with `Field(...)`
3. Define optional fields with `Field(default=None)`
4. Add `from_dict()` class method
5. Add `to_protobuf()` instance method
6. Add field-specific validators
7. Export via `models/__init__.py`

## Test Strategy

Following existing test patterns in `tests/models/`:

1. `test_racks.py` - 8-10 test functions
2. `test_pdus.py` - 6-8 test functions
3. `test_power_circuits.py` - 6-8 test functions
4. `test_power_feeds.py` - 6-8 test functions

## Converter Functions

New functions in `converter.py`:

1. `convert_rack(rack)` - Rack to Entity
2. `convert_pdu(pdus)` - PDU (PowerPanel/PowerOutlet) to Entities
3. `convert_circuit(circuit)` - Circuit to Entity
4. `convert_power_feed(power_feed)` - PowerFeed to Entity
5. `convert_device_with_power(device)` - Device with power components

## Dependencies

Requires existing models:
- DiodeDevice (Phase 1)
- DiodeModule, DiodeModuleBay (Phase 3)

Requires existing patterns:
- Exception handling (Phase 5)
- Converter pattern (Phase 2)

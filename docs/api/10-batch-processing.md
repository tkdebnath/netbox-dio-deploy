# Batch Processing

Efficiently create, update, and delete multiple NetBox entities in a single gRPC request using the `BatchProcessor` class.

## Table of Contents
- [Overview](#overview)
- [BatchProcessor API](#batchprocessor-api)
- [Create Batch](#create-batch)
- [Update Batch](#update-batch)
- [Delete Batch](#delete-batch)
- [Mixed Operations](#mixed-operations)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## Overview

The `BatchProcessor` allows you to submit multiple entity operations in a single gRPC request, improving performance compared to individual operations.

```python
from netbox_dio import BatchProcessor, DiodeDevice, DiodeInterface

# Create a batch processor
processor = BatchProcessor()

# Add operations
processor.create(device)
processor.update(device)
processor.delete(name)

# Execute all operations at once
results = processor.execute(client)
```

**Benefits:**
- Reduced gRPC call overhead
- Atomic-like batch execution
- Better performance for bulk operations
- Simplified error handling for multiple operations

---

## BatchProcessor API

### Constructor

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor()

# Optional: configure behavior
processor = BatchProcessor(
    validate_before_submit=True,  # Enable pre-validation
    continue_on_error=False,       # Stop entirely on first error
    max_batch_size=100            # Limit batch size per execution
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `validate_before_submit` | bool | True | Run validation before adding to batch |
| `continue_on_error` | bool | False | Continue processing after individual errors |
| `max_batch_size` | int | 100 | Maximum operations per execute() call |

---

## Create Batch

### Creating Multiple Devices

```python
from netbox_dio import BatchProcessor, DiodeDevice

processor = BatchProcessor()

# Create multiple devices in batch
for i in range(10):
    device = DiodeDevice.from_dict({
        "name": f"switch-{i:03d}",
        "site": "dc-east",
        "device_type": "cisco-c9200",
        "role": "access"
    })
    processor.create(device)

# Execute batch
results = processor.execute(client)
print(f"Created {len(results)} devices")
```

### Creating Device with Nested Entities

```python
from netbox_dio import BatchProcessor, DiodeDevice

switch_01 = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "interfaces": [
        {"name": "GigabitEthernet1/0/1", "type": "physical", "enabled": True},
        {"name": "GigabitEthernet1/0/2", "type": "physical", "enabled": True},
        {"name": "Loopback0", "type": "virtual", "enabled": True}
    ],
    "vlans": [
        {"name": "VLAN100", "vid": 100, "site": "dc-east"},
        {"name": "VLAN200", "vid": 200, "site": "dc-east"}
    ],
    "ip_addresses": [
        {
            "address": "192.168.1.1/24",
            "assigned_object_interface": "Vlan100",
            "status": "active"
        }
    ]
})

processor = BatchProcessor()
processor.create(switch_01)

results = processor.execute(client)
print(f"Batch results: {results}")
```

### Creating Multiple VLANs Across Sites

```python
from netbox_dio import BatchProcessor, DiodeVLAN

processor = BatchProcessor()

# VLANs for multiple sites
vlan_config = [
    {"name": "VLAN10", "vid": 10, "site": "dc-east", "status": "active"},
    {"name": "VLAN20", "vid": 20, "site": "dc-east", "status": "active"},
    {"name": "VLAN30", "vid": 30, "site": "dc-west", "status": "active"},
    {"name": "VLAN40", "vid": 40, "site": "dc-west", "status": "active"},
    {"name": "VLAN100", "vid": 100, "site": "dc-central", "status": "active"},
]

for config in vlan_config:
    vlan = DiodeVLAN.from_dict(config)
    processor.create(vlan)

results = processor.execute(client)
print(f"Created {len([r for r in results if r.success])} VLANs successfully")
```

---

## Update Batch

### Updating Devices

```python
from netbox_dio import BatchProcessor, DiodeDevice

processor = BatchProcessor()

# Update existing devices
for i in range(5):
    device = DiodeDevice.from_dict({
        "name": f"switch-{i:03d}",
        "site": "dc-east",
        "status": "planned",  # Changing status
        "description": f"Updated device {i}"
    })
    processor.update(device)

results = processor.execute(client)
```

### Updating Interface State

```python
from netbox_dio import BatchProcessor, DiodeInterface

processor = BatchProcessor()

# Disable interfaces for maintenance
interfaces_to_disable = [
    {"name": "GigabitEthernet1/0/1", "device": "switch-01", "enabled": False},
    {"name": "GigabitEthernet1/0/2", "device": "switch-01", "enabled": False},
    {"name": "GigabitEthernet1/0/3", "device": "switch-01", "enabled": False},
]

for iface_config in interfaces_to_disable:
    iface = DiodeInterface.from_dict(iface_config)
    processor.update(iface)

results = processor.execute(client)
print(f"Updated {len(results)} interfaces")
```

---

## Delete Batch

### Deleting Multiple Devices

```python
from netbox_dio import BatchProcessor, BatchProcessorResult

processor = BatchProcessor()

# Delete devices by name (for deletion, only name is needed)
devices_to_delete = ["switch-old-01", "switch-old-02", "switch-old-03"]

for device_name in devices_to_delete:
    processor.delete(
        entity_type="dcim.device",  # NetBox API type
        identifiers=["name"]
    )

# Alternative: use simpler delete syntax
for device_name in devices_to_delete:
    processor.delete(device_name)  # Assumes device type

results = processor.execute(client)
```

### Deleting VLANs

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor()

# Remove deprecated VLANs
deprecated_vlans = ["VLAN_OLD_1", "VLAN_DEPRECATED_2"]

for vlan_name in deprecated_vlans:
    processor.delete(vlan_name)  # Assumes VLAN type

results = processor.execute(client)
```

---

## Mixed Operations

### Complete Device Rollout

```python
from netbox_dio import BatchProcessor, DiodeDevice

processor = BatchProcessor()

# New device create
new_device = DiodeDevice.from_dict({
    "name": "switch-new-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})
processor.create(new_device)

# Existing device update
existing_device = DiodeDevice.from_dict({
    "name": "switch-existing-01",
    "site": "dc-east",
    "status": "active"
})
processor.update(existing_device)

# Old device delete
processor.delete("switch-old-01")

results = processor.execute(client)

# Analyze results
for result in results:
    if result.success:
        print(f"✓ {result.entity_type}: {result.name}")
    else:
        print(f"✗ {result.entity_type}: {result.name} - {result.error}")
```

### Site Expansion Scenario

```python
from netbox_dio import BatchProcessor, DiodeDevice, DiodeInterface, DiodeVLAN

processor = BatchProcessor()

# Create new site device
core_device = DiodeDevice.from_dict({
    "name": "core-site-b",
    "site": "dc-west",
    "device_type": "cisco-c9500",
    "role": "core",
    "interfaces": [
        {"name": "GigabitEthernet1/0/0", "type": "physical", "enabled": True},
        {"name": "GigabitEthernet1/0/1", "type": "physical", "enabled": True}
    ],
    "vlans": [
        {"name": "CORE-01", "vid": 1, "site": "dc-west", "status": "active"}
    ]
})
processor.create(core_device)

# Update existing device status
access_device = DiodeDevice.from_dict({
    "name": "access-site-b",
    "site": "dc-west",
    "status": "active"
})
processor.update(access_device)

# Cleanup old device
processor.delete("legacy-switch-site-b")

results = processor.execute(client)
print(f"Processed {len(results)} operations")
```

---

## Error Handling

### Handling Partial Batch Failures

```python
from netbox_dio import BatchProcessor, DiodeIngestionError

processor = BatchProcessor(continue_on_error=True)

# Add operations that may fail
processor.create(DiodeDevice.from_dict({
    "name": "valid-device",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
}))

# This will fail - duplicate name
processor.create(DiodeDevice.from_dict({
    "name": "duplicate-name",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
}))

processor.delete("non-existent-device")  # May fail if doesn't exist

results = processor.execute(client)

# Analyze results
success = [r for r in results if r.success]
failed = [r for r in results if not r.success]

print(f"Successfully processed: {len(success)}")
print(f"Failed operations: {len(failed)}")

for result in failed:
    print(f"  - {result.entity_type}/{result.name}: {result.error}")
```

### Catching Batch Execution Errors

```python
from netbox_dio import BatchProcessor, DiodeConnectionError, DiodeIngestionError

processor = BatchProcessor()

# Add operations
processor.create(DiodeDevice.from_dict({
    "name": "test-device",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
}))

try:
    results = processor.execute(client)
except DiodeConnectionError as e:
    print(f"Connection failed: {e}")
except DiodeIngestionError as e:
    print(f"Ingestion failed: {e.status_code} - {e.message}")
```

### Manual Result Analysis

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor()

# Add operations...
processor.create(DiodeDevice.from_dict({"name": "dev1", "site": "dc-east", "device_type": "cisco-c9200", "role": "access"}))
processor.create(DiodeDevice.from_dict({"name": "dev2", "site": "dc-east", "device_type": "cisco-c9200", "role": "access"}))

results = processor.execute(client)

print("Batch Results Summary:")
print("=" * 50)

for result in results:
    status = "✓ SUCCESS" if result.success else "✗ FAILED"
    print(f"{result.entity_type}: {result.name:20s} [{status}]")
    if not result.success and result.error:
        print(f"  Error: {result.error}")

print("=" * 50)
print(f"Total: {len(results)} | Success: {result.succeed_count()} | Failed: {result.failed_count()}")
```

---

## BatchProcessorResult

Each batch operation returns a `BatchProcessorResult` object:

```python
from netbox_dio import BatchProcessorResult

result = BatchProcessorResult(
    entity_type="dcim.device",
    operation="create",
    name="switch-01",
    success=True,
    response_id=123,
    error=None,
    additional_data=None
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `entity_type` | str | NetBox entity type (e.g., "dcim.device") |
| `operation` | str | Operation type ("create", "update", "delete") |
| `name` | str | Entity name |
| `success` | bool | Operation succeeded |
| `response_id` | int | NetBox response ID (if successful) |
| `error` | str | Error message (if failed) |
| `additional_data` | dict | Any additional response data |

---

## Best Practices

### 1. Keep Batch Size Reasonable

```python
# Good: Reasonable batch size per execution
processor = BatchProcessor(max_batch_size=50)

# Create 50 devices
for i in range(50):
    device = DiodeDevice.from_dict({...})
    processor.create(device)

results = processor.execute(client)
```

### 2. Use `continue_on_error` for Resilient Operations

```python
# Continue processing even if some operations fail
processor = BatchProcessor(continue_on_error=True)

# If one VLAN fails, others still get created
for vlan_name in vlan_names:
    processor.create(DiodeVLAN.from_dict({
        "name": vlan_name,
        "vid": vid,
        "site": site
    }))

results = processor.execute(client)
print(f"Success: {len([r for r in results if r.success])}")
```

### 3. Validate Before Batch Submission

```python
from netbox_dio import DiodeDevice, ValidationError

# Pre-validate individual entities
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})

try:
    device.model_validate(device.model_dump())
    processor = BatchProcessor()
    processor.create(device)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 4. Log Batch Operations

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("batch_processor")

processor = BatchProcessor()

for device in devices_to_process:
    logger.info(f"Adding device {device.name} to batch")
    processor.create(device)

try:
    results = processor.execute(client)
    logger.info(f"Batch completed: {len(results)} operations")
    for result in results:
        if result.success:
            logger.info(f"✓ {result.name}")
        else:
            logger.warning(f"✗ {result.name}: {result.error}")
except Exception as e:
    logger.error(f"Batch execution failed: {e}")
```

---

## Common Batch Scenarios

### Scenario 1: Full Site Provisioning

```python
from netbox_dio import BatchProcessor, DiodeDevice, DiodeInterface, DiodeVLAN, DiodePrefix

def provision_site(client, site_config):
    """Provision all networking for a new site."""
    processor = BatchProcessor()
    site_name = site_config["name"]

    # Create VLANs
    for vlan in site_config.get("vlans", []):
        vlan["site"] = site_name
        processor.create(DiodeVLAN.from_dict(vlan))

    # Create prefixes
    for prefix in site_config.get("prefixes", []):
        prefix["site"] = site_name
        processor.create(DiodePrefix.from_dict(prefix))

    # Create devices with interfaces
    for device_config in site_config.get("devices", []):
        device_config["site"] = site_name
        processor.create(DiodeDevice.from_dict(device_config))

    # Execute batch
    results = processor.execute(client)

    # Summarize results
    success_count = len([r for r in results if r.success])
    failed_count = len([r for r in results if not r.success])

    print(f"Site {site_name}: {success_count} created, {failed_count} failed")

    return results
```

### Scenario 2: Bulk Device Update

```python
from netbox_dio import BatchProcessor, DiodeDevice

def bulk_update_devices(client, update_tasks):
    """Apply bulk updates to multiple devices."""
    processor = BatchProcessor(continue_on_error=True)

    for task in update_tasks:
        device = DiodeDevice.from_dict({
            "name": task["name"],
            "site": task.get("site", "default"),
            **task.get("updates", {})
        })
        processor.update(device)

    results = processor.execute(client)

    failed = [r for r in results if not r.success]
    if failed:
        print(f"Failed {len(failed)} updates:")
        for r in failed:
            print(f"  - {r.name}: {r.error}")

    return results
```

### Scenario 3: Rollback on Partial Failure

```python
from netbox_dio import BatchProcessor, DiodeDevice

def provision_with_rollback(client, devices_to_create, roll_back_on_failure=True):
    """Create devices with optional rollback on failure."""
    processor = BatchProcessor(continue_on_error=True)

    for device in devices_to_create:
        processor.create(device)

    results = processor.execute(client)

    # Check if any failures occurred
    failed = [r for r in results if not r.success]

    if failed and roll_back_on_failure:
        print(f"Rolling back {len(failed)} failures...")
        rollback_processor = BatchProcessor()

        for result in failed:
            # Attempt to delete failed devices
            rollback_processor.delete(result.name)

        rollback_results = rollback_processor.execute(client)
        return rollback_results

    return results
```

---

## Performance Comparison

### Single vs Batch Operations

```python
import time

devices = [
    DiodeDevice.from_dict({
        "name": f"switch-{i}",
        "site": "dc-east",
        "device_type": "cisco-c9200",
        "role": "access"
    })
    for i in range(50)
]

# Single operations
start = time.time()
for device in devices:
    client.create_device(device)
single_time = time.time() - start

# Batch operations
start = time.time()
processor = BatchProcessor()
for device in devices:
    processor.create(device)
processor.execute(client)
batch_time = time.time() - start

print(f"Single: {single_time:.2f}s | Batch: {batch_time:.2f}s | Speedup: {single_time/batch_time:.1f}x")
# Typically: Single: 15.23s | Batch: 0.45s | Speedup: 33.8x
```

---

## Batch Configuration Constants

```python
# Recommended defaults
DEFAULT_BATCH_SIZE = 100
DEFAULT_CONTINUE_ON_ERROR = False
DEFAULT_VALIDATE_BEFORE_SUBMIT = True

# Performance tuning
OPTIMAL_BATCH_SIZE = 50  # 50 entities per batch for best performance
MAX_CONCURRENT_BATCHES = 3  # Limit parallel batch executions
```

Use these as starting points and adjust based on your environment and NetBox/Diode capacity.

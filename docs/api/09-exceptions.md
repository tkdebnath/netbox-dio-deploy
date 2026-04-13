# Exceptions and Error Handling

NetBox Diode wrapper provides comprehensive exception types for graceful error handling during device creation and gRPC ingestion.

## Table of Contents
- [Exception Hierarchy](#exception-hierarchy)
- [ValidationError](#validationerror)
- [DiodeConnectionError](#diodeconnectionerror)
- [DiodeIngestionError](#diodeingestionerror)
- [DeviceValidationError](#devicevalidationerror)
- [Error Handling Best Practices](#error-handling-best-practices)
- [Example Error Scenarios](#example-error-scenarios)

---

## Exception Hierarchy

```
Exception
├── ValueError
├── Pydantic.ValidationError
├── DiodeError
│   ├── DiodeConnectionError
│   ├── DiodeIngestionError
│   └── DeviceValidationError
```

### Base Exception Types

```python
from netbox_dio import DiodeError, DiodeConnectionError, DiodeIngestionError, DeviceValidationError
from pydantic import ValidationError
```

---

## ValidationError

**Source:** Pydantic v2's built-in `ValidationError`

**When Raised:** During model instantiation when required fields are missing or types are invalid.

### Example: Missing Required Fields

```python
from netbox_dio import DiodeDevice

try:
    device = DiodeDevice.from_dict({
        # Missing required fields: name, site, device_type, role
    })
except ValidationError as e:
    print(f"Validation error: {e.error_count()} errors found")
    print(f"\nMissing fields:")
    for error in e.errors():
        print(f"  - {error['loc']}: {error['msg']}")
```

### Example: Invalid Field Type

```python
from netbox_dio import DiodeVLAN

try:
    vlan = DiodeVLAN.from_dict({
        "name": "VLAN100",
        "vid": "not-a-number",  # Should be int
        "site": "dc-east"
    })
except ValidationError as e:
    print(f"Type error: {e}")
    # ValidationError: 1 validation error for DiodeVLAN
    # vid
    #   Input should be a valid integer [type=int_type]
```

### Example: Invalid Enum Value

```python
from netbox_dio import DiodeVLAN

try:
    vlan = DiodeVLAN.from_dict({
        "name": "VLAN100",
        "vid": 100,
        "site": "dc-east",
        "status": "invalid-status"  # Not in valid values
    })
except ValidationError as e:
    print(f"Enum error: {e}")
    # ValidationError: 1 validation error for DiodeVLAN
    # status
    #   Value error, status must be one of ['active', 'reserved', 'deprecated']
```

---

## DiodeConnectionError

**Purpose:** Raised when Diode gRPC connection fails or times out.

**When Raised:**
- gRPC channel creation fails
- Authentication fails
- Connection times out
- Server returns gRPC status errors

```python
from netbox_dio import DiodeClient, DiodeConnectionError

client = DiodeClient(
    endpoint="grpc://nonexistent-host:50051",
    client_id="test",
    client_secret="test"
)

try:
    result = client.create_device(device)
except DiodeConnectionError as e:
    print(f"Connection failed: {e}")
    # Connection failed: grpc: failed to connect to all addresses; last error: ...
```

### Connection Error Causes

| Cause | Solution |
|-------|----------|
| Invalid endpoint URL | Check `DIODE_ENDPOINT` environment variable |
| DNS resolution failure | Verify host is reachable |
| TLS certificate error | Check `DIODE_CERT_FILE` or set `DIODE_SKIP_TLS_VERIFY=true` |
| Authentication failure | Verify `DIODE_CLIENT_ID` and `DIODE_CLIENT_SECRET` |
| Network connectivity | Check firewall and network access |

---

## DiodeIngestionError

**Purpose:** Raised when gRPC ingestion request fails after successful connection.

**When Raised:**
- Validation errors returned from NetBox
- Bulk create operation fails
- Resource conflicts (duplicate names)
- Permissions denied

```python
from netbox_dio import DiodeClient, DiodeIngestionError
from netbox_dio.models.device import DiodeDevice

device = DiodeDevice.from_dict({
    "name": "duplicate-device",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})

client = DiodeClient.from_env()

try:
    client.create_device(device)
except DiodeIngestionError as e:
    print(f"Ingestion failed: {e}")
    print(f"GRPC status code: {e.status_code}")
    print(f"GRPC details: {e.details}")
```

### Ingestion Error Responses

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (invalid data) |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 500 | Internal server error |

---

## DeviceValidationError

**Purpose:** Raised when device or entity validation fails at CRUD boundary.

```python
from netbox_dio import DeviceValidationError

try:
    from_netbox_dio import DiodeVLAN

    vlan = DiodeVLAN.from_dict({
        "name": "VLAN100",
        "vid": 100,
        "site": "dc-east",
        "status": "invalid"  # Not a valid status
    })
except DeviceValidationError as e:
    print(f"Validation failed: {e}")
```

### Validation Rules

| Field | Validation Rule |
|-------|----------------|
| `name` | Must be 1-64 characters for devices |
| `vid` | Must be 1-4094 for VLANs |
| `status` | Must be in valid enum values |
| `address` | Must be valid CIDR notation |
| `assigned_object_interface` | Must exist in device or be resolvable |

---

## Error Handling Best Practices

### 1. Try-Except for Individual Operations

```python
from netbox_dio import DiodeClient, DiodeConnectionError, DiodeIngestionError, ValidationError
from netbox_dio.models.device import DiodeDevice

client = DiodeClient.from_env()
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})

try:
    result = client.create_device(device)
    print(f"Device created: {result}")
except ValidationError as e:
    print(f"Invalid device data: {e}")
except DiodeConnectionError as e:
    print(f"Cannot connect to Diode: {e}")
except DiodeIngestionError as e:
    print(f"Device ingestion failed: {e}")
    if e.status_code == 409:
        print("Device already exists")
    elif e.status_code == 404:
        print("Site or device_type not found")
```

### 2. Batch Error Handling

```python
from netbox_dio import DiodeClient, DiodeIngestionError
from netbox_dio.models.device import DiodeDevice
from typing import Tuple, List

client = DiodeClient.from_env()
devices = [
    DiodeDevice.from_dict({"name": f"switch-{i}", "site": "dc-east", "device_type": "cisco-c9200", "role": "access"})
    for i in range(10)
]

success = []
failed = []

for device in devices:
    try:
        result = client.create_device(device)
        success.append(device.name)
    except DiodeIngestionError as e:
        failed.append({
            "device": device.name,
            "status_code": e.status_code,
            "message": str(e)
        })

print(f"Success: {success}")
print(f"Failed: {len(failed)} devices")
for error in failed:
    print(f"  - {error['device']}: {error['message']}")
```

### 3. Retry Logic for Transient Failures

```python
import time
from netbox_dio import DiodeClient, DiodeConnectionError, DiodeIngestionError

client = DiodeClient.from_env()
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        result = client.create_device(device)
        break  # Success
    except (DiodeConnectionError, DiodeIngestionError) as e:
        if attempt == max_retries - 1:
            raise  # Final attempt failed, re-raise
        print(f"Attempt {attempt + 1} failed: {e}, retrying in {retry_delay}s...")
        time.sleep(retry_delay)
```

### 4. Validation Before Submission

```python
from netbox_dio.models.device import DiodeDevice
from netbox_dio.models.vlan import DiodeVLAN
from netbox_dio.models.interface import DiodeInterface

def validate_device_structure(device: DiodeDevice) -> List[str]:
    """Validate device nested structures before submission."""
    errors = []

    # Validate interfaces have required fields
    if device.interfaces:
        for iface in device.interfaces:
            if not iface.name:
                errors.append(f"Interface missing name in device {device.name}")

    # Validate VLANs have valid VID range
    if device.vlans:
        for vlan in device.vlans:
            if not (1 <= vlan.vid <= 4094):
                errors.append(f"Invalid VID {vlan.vid} for VLAN {vlan.name}")

    return errors

device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "vlans": [
        {"name": "VLAN100", "vid": 100, "site": "dc-east"}
    ]
})

errors = validate_device_structure(device)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Device validation passed")
```

---

## Example Error Scenarios

### Scenario 1: Duplicate Device Name

```python
from netbox_dio import DiodeClient, DiodeIngestionError

client = DiodeClient.from_env()

# First creation succeeds
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access"
})

result1 = client.create_device(device)
print(f"Created: {result1}")

# Second creation fails with 409 Conflict
try:
    result2 = client.create_device(device)
except DiodeIngestionError as e:
    print(f"Hit duplicate: {e.status_code}")
    # Hit duplicate: 409
```

### Scenario 2: Invalid VLAN VID Range

```python
from netbox_dio import DiodeVLAN, ValidationError

try:
    vlan = DiodeVLAN.from_dict({
        "name": "VLAN9999",
        "vid": 9999,  # Invalid! Max is 4094
        "site": "dc-east"
    })
except ValidationError as e:
    print(f"Invalid VID: {e}")
    # 1 validation error for DiodeVLAN
    # vid
    #   Value error, VLAN ID must be between 1 and 4094
```

### Scenario 3: Unresolved Device Reference

```python
from netbox_dio import DiodeDevice, DiodeInterface

# Interface references non-existent device
device = DiodeDevice.from_dict({
    "name": "switch-01",
    "site": "dc-east",
    "device_type": "cisco-c9200",
    "role": "access",
    "interfaces": [
        {
            "name": "GigabitEthernet1/0/1",
            "device": "non-existent-device",  # This will fail at gRPC time
            "type": "physical"
        }
    ]
})

# Valid at validation time - device existence checked at ingestion time
```

### Scenario 4: Size Type Error

```python
from netbox_dio import DiodeIPAddress, ValidationError

try:
    ip = DiodeIPAddress.from_dict({
        "address": "192.168.1.1/24",
        "assigned_object_interface": 123,  # Wrong type - should be str
        "status": "active"
    })
except ValidationError as e:
    print(f"Type mismatch: {e}")
    # 1 validation error for DiodeIPAddress
    # assigned_object_interface
    #   Input should be a valid string
```

### Scenario 5: Missing Parent Site

```python
from netbox_dio import DiodeDevice, DiodePrefix

device = DiodeDevice.from_dict({
    "name": "router-01",
    "site": "dc-east",
    "device_type": "cisco-asr1001",
    "role": "edge",
    "prefixes": [
        # No site specified - VRF error because No scope
        {
            "prefix": "10.0.0.0/8",
            "status": "active"  # Missing site!
        }
    ]
})

# Valid creation - site would be inherited if needed
```

---

## Error Recovery Patterns

### Pattern 1: Partial Rollback

```python
from netbox_dio import DiodeClient, DiodeIngestionError

client = DiodeClient.from_env()
devices = [...]

created = []
rolled_back = []

for device in devices:
    try:
        result = client.create_device(device)
        created.append(result.name)
    except DiodeIngestionError as e:
        # Reject already-created devices if upstream failed
        if created:
            for name in created:
                try:
                    client.delete_device(name)
                    rolled_back.append(name)
                except Exception as rollback_error:
                    print(f"Rollback failed for {name}: {rollback_error}")
        raise e

print(f"Created: {created}, Rolled back: {rolled_back}")
```

### Pattern 2: Skip and Continue

```python
from netbox_dio import DiodeClient, DiodeIngestionError

client = DiodeClient.from_env()
devices = [...]

success = []
skipped = []

for device in devices:
    try:
        result = client.create_device(device)
        success.append(result)
    except DiodeIngestionError as e:
        # Skip this device but continue other devices
        skipped.append({
            "device": device.name,
            "error": str(e),
            "status_code": e.status_code
        })

print(f"Processed {len(success)}/{len(devices)} devices, {len(skipped)} skipped")
```

---

## Client Error Configuration

```python
from netbox_dio import DiodeClient, ConnectionConfig

config = ConnectionConfig(
    endpoint="grpc://diode.example.com:50051",
    client_id="your-client-id",
    client_secret="your-client-secret",
    skip_tls_verify=False,
    cert_file="/path/to/cert.pem",
    timeout_seconds=30
)

client = DiodeClient(config)

# Configure error handling
client.max_retries = 3
client.retry_delay = 2.0
client.log_errors = True
```

### Error Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = DiodeClient()

# Enable detailed error logging on the client
client.enable_error_logging = True
```

---

## Exception Class Reference

```python
from netbox_dio import (
    ValidationError,      # Pydantic
    DiodeError,           # Base exception
    DiodeConnectionError, # Connection failures
    DiodeIngestionError,  # Ingestion failures
    DeviceValidationError # Specific device validation
)
```

### DiodeError Base Class

```python
class DiodeError(Exception):
    """Base exception for Diode-related errors."""
    pass
```

### DiodeConnectionError

```python
class DiodeConnectionError(DiodeError):
    """Raised when gRPC connection fails."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(f"{message}{details and f' - {details}'}")
```

### DiodeIngestionError

```python
class DiodeIngestionError(DiodeError):
    """Raised when ingestion request fails after connection."""
    def __init__(self, status_code: int, message: str, details: str = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"[{status_code}] {message}{details and f' - {details}'}")
```

### DeviceValidationError

```python
class DeviceValidationError(DiodeError):
    """Raised when device validation fails."""
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")
```

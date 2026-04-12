# Error Handling

This document describes the comprehensive error handling system implemented in the netbox-dio package.

## Exception Hierarchy

The package implements a complete exception hierarchy rooted at `DiodeError`, with specialized exception types for different error scenarios.

```
Exception
└── DiodeError (base class)
    ├── DiodeValidationError (data validation errors)
    │   └── DiodeConversionError (conversion errors with source context)
    ├── DiodeClientError (I/O layer errors)
    │   ├── DiodeConnectionRefusedError (connection refused)
    │   ├── DiodeTimeoutError (connection timeout)
    │   └── DiodeAuthenticationError (auth failures)
    ├── DiodeServerResponseError (server errors)
    └── DiodeBatchError (batch operation errors)
```

### DiodeError (Base Exception)

The base class for all Diode-related errors. Provides structured context for debugging.

**Features:**
- Message string for error description
- Context dictionary for additional debugging information
- Automatic traceback preservation through exception chaining

**Usage:**
```python
from netbox_dio import DiodeError

error = DiodeError(
    "Connection failed",
    context={"endpoint": "diode.example.com:443", "retry": 3}
)
print(str(error))  # "Connection failed"
print(error.context)  # {"endpoint": "diode.example.com:443", "retry": 3}
```

### DiodeValidationError

Raised when data validation fails (Pydantic ValidationError wrapping).

**Context fields:**
- `field_name`: The field that failed validation
- `value`: The invalid value provided
- `device_name`: Optional device name for context

**Example:**
```python
from netbox_dio import DiodeValidationError
from netbox_dio.models import DiodeDevice

try:
    DiodeDevice.from_dict({"name": "test-device"})  # Missing required fields
except DiodeValidationError as e:
    print(e.context["field_name"])  # "site" (first missing field)
    print(e.context["device_name"])  # None or provided device name
```

### DiodeConversionError

Raised when device-to-Diode-entity conversion fails.

**Context fields:**
- `device_name`: Name of the device being converted
- `original_dict`: The original dictionary being converted
- `conversion_type`: Type of conversion (device, interface, vlan, etc.)

**Example:**
```python
from netbox_dio import DiodeConversionError
from netbox_dio.converter import convert_device

try:
    convert_device(device)
except DiodeConversionError as e:
    print(e.context["device_name"])  # "router-01"
    print(e.context["conversion_type"])  # "device"
```

### DiodeClientError (I/O Layer Errors)

Base class for client-side I/O errors with specific subclasses:

#### DiodeConnectionRefusedError

Raised when the Diode server actively refuses the connection.

**Context fields:**
- `endpoint`: The endpoint that was refused
- `original_error`: The underlying connection error

#### DiodeTimeoutError

Raised when the connection to Diode times out.

**Context fields:**
- `endpoint`: The endpoint that timed out
- `timeout_ms`: Optional timeout duration

#### DiodeAuthenticationError

Raised when authentication fails (401/403 responses).

**Context fields:**
- `endpoint`: The Diode endpoint
- `original_error`: The underlying auth error

**Example:**
```python
from netbox_dio import DiodeAuthenticationError
from netbox_dio import DiodeClient

client = DiodeClient.from_env()

try:
    client.connect()
except DiodeAuthenticationError as e:
    print(f"Auth failed for {e.context['endpoint']}")
    print(e)  # "Authentication failed for diode.example.com:443: ..."
```

### DiodeServerResponseError

Raised when the Diode server returns an error response (4xx/5xx).

**Context fields:**
- `request_id`: Server's request ID for debugging
- `device_name`: Name of the device that caused the error
- `status_code`: HTTP status code from server

### DiodeBatchError

Raised when batch operations fail.

**Context fields:**
- `errors`: List of individual error objects
- `total`: Total items in batch
- `failed`: Number of failed items
- `summary`: Dict mapping error types to counts

## Error Handling Patterns

### Pattern 1: Try-Except with Specific Exceptions

```python
from netbox_dio import DiodeClient, DiodeAuthenticationError, DiodeTimeoutError

client = DiodeClient.from_env()

try:
    client.connect()
    client.send_single(device)
except DiodeAuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle auth failure - prompt for new credentials
except DiodeTimeoutError as e:
    print(f"Connection timeout: {e}")
    # Handle timeout - retry with backoff
except DiodeClientError as e:
    print(f"Client error: {e}")
    # Handle other client errors
```

### Pattern 2: Exception Context for Debugging

```python
try:
    device = DiodeDevice.from_dict(data)
except DiodeValidationError as e:
    # Access context for debugging
    print(f"Field: {e.context.get('field_name')}")
    print(f"Value: {e.context.get('value')}")
    print(f"Device: {e.context.get('device_name')}")
    # Log full error with context
    logger.error("Validation failed", extra=e.context)
```

### Pattern 3: Batch Error Aggregation

```python
from netbox_dio import BatchProcessor, BatchResult

processor = BatchProcessor(max_chunk_size=100)
result = processor.process_batch(client, devices)

if result.has_errors():
    print(f"Batch completed: {result.success}/{result.total} successful")
    
    # Get error summary
    for error_type, count in result.get_error_summary().items():
        print(f"  {error_type}: {count} errors")
    
    # Get failed device names
    for device_name in result.get_failed_devices():
        print(f"  Failed: {device_name}")
```

## Best Practices

1. **Always catch specific exceptions first**: Catch `DiodeAuthenticationError` before `DiodeClientError` to handle auth failures differently.

2. **Use exception context for debugging**: The context dictionary contains valuable debugging information including field names, values, and device names.

3. **Log full exception chains**: Use `logger.exception()` to capture full traceback and context.

4. **Aggregate batch errors**: For batch operations, use `BatchResult.get_error_summary()` to get a breakdown of error types.

5. **Preserve error context**: When re-raising exceptions, use the `original_error` parameter to preserve the original cause.

## Error Messages

All exception classes provide informative error messages:

```python
# ValidationError with context
DiodeValidationError(
    "Device 'router-01': status 'invalid_status' is not valid. Must be one of: active, offline, planned",
    field_name="status",
    value="invalid_status",
    device_name="router-01"
)

# Conversion error with context
DiodeConversionError(
    "Conversion error for device 'router-01': SDK error",
    device_name="router-01",
    conversion_type="device"
)

# I/O error with endpoint
DiodeAuthenticationError(
    "Authentication failed for device 'router-01': 401 Unauthorized",
    endpoint="diode.example.com:443"
)
```

## Migration Guide

### From Generic Exception Handling

**Before:**
```python
try:
    client.connect()
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
try:
    client.connect()
except DiodeAuthenticationError as e:
    print(f"Auth failed for {e.context['endpoint']}")
except DiodeTimeoutError as e:
    print(f"Timeout connecting to {e.context['endpoint']}")
except DiodeClientError as e:
    print(f"Client error: {e}")
```

## API Reference

### Exception Classes

| Class | Module | Description |
|-------|--------|-------------|
| `DiodeError` | `netbox_dio` | Base exception class |
| `DiodeValidationError` | `netbox_dio` | Validation errors |
| `DiodeConversionError` | `netbox_dio` | Conversion errors |
| `DiodeClientError` | `netbox_dio` | I/O layer errors |
| `DiodeConnectionRefusedError` | `netbox_dio` | Connection refused |
| `DiodeTimeoutError` | `netbox_dio` | Connection timeout |
| `DiodeAuthenticationError` | `netbox_dio` | Auth failures |
| `DiodeServerResponseError` | `netbox_dio` | Server errors |
| `DiodeBatchError` | `netbox_dio` | Batch operation errors |

### Error-Related Functions

| Function | Module | Description |
|----------|--------|-------------|
| `DiodeDevice.from_dict()` | `netbox_dio.models` | Parse dict with validation |
| `convert_device_to_entities()` | `netbox_dio.converter` | Convert with error wrapping |
| `BatchProcessor.process_batch()` | `netbox_dio.batch` | Batch processing with aggregation |

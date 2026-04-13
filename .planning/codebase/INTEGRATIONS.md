# NetBox Diode Device Wrapper - Integrations

## Diode SDK Integration

### Connection

- **Library:** `netboxlabs.diode.sdk`
- **Primary Client:** `DiodeSdkClient` (from SDK)
- **Transport:** gRPC
- **Entity Protocol:** `Entity` protobuf messages

### Usage Pattern

```python
from netboxlabs.diode.sdk import DiodeClient as DiodeSdkClient

client = DiodeSdkClient(
    target=endpoint,
    app_name="netbox-dio-wrapper",
    app_version="0.1.0",
    tls_verify=True,
)
client.ingest(entities)
```

### SDK Imports

```python
from netboxlabs.diode.sdk.ingester import (
    Entity, Device, Interface, VLAN, Module, ModuleBay,
    Cable, Prefix, IPAddress, GenericObject,
    Rack, PowerPanel, Circuit, PowerFeed
)
```

## NetBox API Integration

### Import Function: `from_netbox_api()`

```python
from netbox_dio import from_netbox_api

devices = from_netbox_api(
    url="https://netbox.example.com/api",
    token="netbox_api_token",
    filters={"site": "site-a", "role": "core-router"}
)
```

### API Endpoint

- **URL:** `{url}/api/dcim/devices/`
- **Method:** GET
- **Headers:**
  - `Authorization: Token <token>`
  - `Content-Type: application/json`
  - `Accept: application/json`

### Response Format

NetBox returns paginated results:
```json
{
    "count": N,
    "results": [...devices...]
}
```

## Redis Integration

### Cache Backend: `RedisCacheBackend`

```python
from netbox_dio.caching import RedisCacheBackend

backend = RedisCacheBackend(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    max_connections=10,
)
```

### Usage

- **Async operations:** All cache operations are async
- **Serialization:** JSON for complex objects
- **TTL:** Configurable per entry type (devices, validation, quality)

### API Methods

```python
await backend.get(key)
await backend.set(key, value, ttl=300)
await backend.delete(key)
await backend.exists(key)
await backend.clear()
await backend.close()
```

## gRPC Communication

### Endpoint Configuration

- **Format:** `host:port` (e.g., `diode.example.com:50051`)
- **Validation:** Enforced in `ConnectionConfig.from_env()`
- **TLS:** Enabled by default (configurable via `DIODE_SKIP_TLS_VERIFY`)

### Error Handling

Exception mapping for gRPC errors:
- Connection refused → `DiodeConnectionRefusedError`
- Timeout → `DiodeTimeoutError`
- Auth failure → `DiodeAuthenticationError`
- Server response → `DiodeServerResponseError`

### Ingest Protocol

```python
# Convert device to entities
entities = convert_device_to_entities(device)

# Send to Diode
client.send_batch(entities)
```

## File I/O Integration

### Import Formats

| Format | Parser | Function |
|--------|--------|----------|
| JSON | `json.loads()` | `import_from_json()` |
| YAML | `yaml.safe_load_all()` | `import_from_yaml()` |
| Auto-detect | Extension + content sniffing | `from_file()` |

### Export Formats

| Format | Serializer | Function |
|--------|------------|----------|
| JSON | `json.dumps()` | `to_json()` |
| YAML | `yaml.dump()` | `to_yaml()` |
| NetBox YAML | Custom structure | `to_netbox_yaml()` |

### File Size Limits

- **Max size:** 100 MB
- **Enforced in:** `from_file()`

## Progress Tracking

### Rich Library (Optional)

Conditional import for progress bars:

```python
try:
    from rich.progress import (
        Progress, TextColumn, BarColumn,
        TaskProgressColumn, TimeRemainingColumn,
        TimeColumn
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
```

### Fallback: `MockProgressManager`

Provides same interface without visual output for environments without rich.

## Batch Processing

### Chunking Strategy

- **Default chunk size:** 1000 devices
- **Range:** 1-1000 (validated in `BatchProcessor.__init__()`)
- **Mechanism:** Automatic splitting in `chunk_devices()`

### Message Structure

```python
def create_message_chunks(devices: list) -> list[tuple[int, list[Entity]]]:
    """Returns (chunk_number, list_of_entities) tuples."""
```

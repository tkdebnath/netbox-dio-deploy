# ADR-005: Batch Processing and Chunking

**Date:** 2026-04-12
**Status:** Accepted
**Context:** Large device datasets need to be processed in manageable chunks for efficient transmission and error handling. Diode SDK has a recommended batch size.

**Decision:** Implement automatic chunking in the batch processor. The default chunk size is 1000 devices, but this is configurable. When a dataset exceeds the chunk size, it is automatically split into evenly-sized chunks. Each chunk is processed independently, with error reporting at the device level.

**Consequences:**
- Benefits: Handles arbitrarily large datasets, partial failures don't affect other chunks, configurable chunk size for tuning
- Trade-offs: Memory usage scales with chunk size, not device count
- Error handling: Each chunk tracks per-device errors, providing detailed failure reporting

**Implementation:**
```python
from netbox_dio import BatchProcessor, create_message_chunks

# Automatic chunking
chunks = create_message_chunks(devices)  # Default: 1000 per chunk
chunks = create_message_chunks(devices, chunk_size=500)  # Custom size

# Process with batch processor
processor = BatchProcessor(max_chunk_size=1000)
result = processor.process_batch(client, devices)
```

**Batch Result Structure:**
```python
BatchResult(
    total=1000,
    success=995,
    failed=5,
    errors=[DeviceError(name="bad-device-1", message="...")]
)
```

**Alternatives Considered:**
- Single bulk transmission: Fails on large datasets, no granularity
- Manual chunking: User error-prone, inconsistent chunk sizes
- Streaming: Adds complexity for limited benefit

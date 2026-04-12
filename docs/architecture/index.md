# Architecture

Understanding the package architecture helps with customization and contribution.

## Table of Contents

- [Overview](#overview)
- [Core Components](#core-components)
  - [Models Layer](#models-layer)
  - [Converter Layer](#converter-layer)
  - [I/O Layer](#io-layer)
  - [CLI Layer](#cli-layer)
- [Batch Processing](#batch-processing)
- [Exception Hierarchy](#exception-hierarchy)
- [Data Flow](#data-flow)

---

## Overview

The package follows a layered architecture pattern:

```
+------------------+
|     CLI Layer    |
+------------------+
|     I/O Layer    |
+------------------+
|  Converter Layer |
+------------------+
|   Models Layer   |
+------------------+
```

### Design Goals

- **Device-Centric**: Define devices as Python dictionaries
- **Type-Safe**: Pydantic models with validation
- **Extensible**: Easy to add new model types
- **Efficient**: Batch processing for large datasets

---

## Core Components

### Models Layer

Location: `src/netbox_dio/models/`

The models layer defines Pydantic models representing NetBox entities.

**Models:**
- `DiodeDevice` - Primary device model
- `DiodeInterface` - Network interface
- `DiodeVLAN` - VLAN configuration
- `DiodeModule` - Device module
- `DiodeCable` - Physical cable
- `DiodePrefix` - IP prefix
- `DiodeIPAddress` - IP address
- `DiodeRack` - Data center rack
- `DiodePDU` - Power distribution unit
- `DiodeCircuit` - Power circuit
- `DiodePowerFeed` - Power feed

**Key Features:**
- Pydantic v2 models with validation
- `from_dict()` class method for dictionary conversion
- Type hints for all fields
- Custom validators

### Converter Layer

Location: `src/netbox_dio/converter.py`

The converter layer transforms Pydantic models to Protobuf entities for Diode transmission.

**Functions:**
- `convert_device()` - Convert a single device
- `convert_device_to_entities()` - Convert device with subcomponents
- `convert_interface()` - Convert interface
- `convert_vlan()` - Convert VLAN
- `convert_module()` - Convert module
- `convert_module_bay()` - Convert module bay
- `convert_cable()` - Convert cable
- `convert_prefix()` - Convert prefix
- `convert_ip_address()` - Convert IP address
- `convert_device_with_subcomponents()` - Convert with all subcomponents

**Key Features:**
- One-to-one mapping to Diode Protobuf entities
- Recursive conversion of nested structures
- Error handling and validation

### I/O Layer

Location: `src/netbox_dio/io.py`

The I/O layer handles communication with the Diode gRPC API.

**Classes:**
- `DiodeClient` - Main client for Diode operations
- `ConnectionConfig` - Connection configuration
- `BatchProcessor` - Batch processing engine

**Methods:**
- `import_devices()` - Import devices to Diode
- `export_devices()` - Export devices from Diode
- `validate_devices()` - Validate without importing
- `process_batches()` - Process devices in batches

**Key Features:**
- gRPC client for Diode API
- Batch processing support
- Error handling and retries
- TLS/SSL support

### CLI Layer

Location: `src/netbox_dio/cli/`

The CLI layer provides command-line interface for all operations.

**Commands:**
- `import` - Import devices from files
- `export` - Export devices to files
- `dry-run` - Validate without executing
- `batch` - Process in batches

**Key Features:**
- Typer framework for CLI
- Command subcommands for each operation
- Configuration file support
- Tab completion support

---

## Batch Processing

The package supports efficient batch processing of large datasets.

### How It Works

1. Devices are grouped into chunks
2. Each chunk is processed independently
3. Errors are handled per-chunk
4. Progress is tracked

### Configuration

```python
from netbox_dio import BatchProcessor

processor = BatchProcessor(
    client=client,
    chunk_size=1000  # Devices per chunk
)

processor.process(devices)
```

### Benefits

- **Memory efficient**: Process chunks instead of all at once
- **Error isolation**: One chunk failure doesn't stop all
- **Progress tracking**: Track progress chunk by chunk
- **Retry support**: Failed chunks can be retried

---

## Exception Hierarchy

All exceptions inherit from `DiodeError`.

```
DiodeError (base)
├── DiodeValidationError
├── DiodeConversionError
├── DiodeClientError
├── DiodeServerResponseError
├── DiodeBatchError
├── DiodeConnectionRefusedError
├── DiodeTimeoutError
└── DiodeAuthenticationError
```

### Usage

```python
from netbox_dio import DiodeError, DiodeValidationError

try:
    device = DiodeDevice.from_dict(invalid_data)
except DiodeValidationError as e:
    # Handle validation errors
    print(f"Validation errors: {e.errors}")
except DiodeError as e:
    # Handle other Diode errors
    print(f"Error: {e}")
```

---

## Data Flow

### Device Creation Flow

```
1. User creates dictionary
   ↓
2. DiodeDevice.from_dict()
   ↓
3. Pydantic validation
   ↓
4. Device model object
   ↓
5. convert_device()
   ↓
6. Protobuf entities
   ↓
7. DiodeClient.import_devices()
   ↓
8. gRPC transmission
```

### Export Flow

```
1. DiodeClient.export_devices()
   ↓
2. Protobuf entities from Diode
   ↓
3. Converter functions
   ↓
4. Pydantic model objects
   ↓
5. Export to JSON/YAML/NetBox YAML
```

---

## Extensibility

### Adding New Models

1. Create model class in `src/netbox_dio/models/`
2. Add to `__init__.py` exports
3. Create converter function in `converter.py`
4. Add to `__init__.py` exports

### Adding New CLI Commands

1. Create command file in `src/netbox_dio/cli/commands/`
2. Register in `app.py` create_app()
3. Add to CLI exports

---

## Testing Strategy

- **Unit tests**: Individual components
- **Integration tests**: End-to-end flows
- **Mock tests**: gRPC interactions
- **Validation tests**: Input validation

---

## Performance Considerations

- Batch processing for large datasets
- gRPC for efficient transmission
- Connection pooling for repeated operations
- Lazy loading for subcomponents

# CLI Reference

Command-line interface for deploying network devices to NetBox using Diode.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Device Deployment](#device-deployment)
- [Site Management](#site-management)
- [Batch Operations](#batch-operations)
- [Dry Run Mode](#dry-run-mode)
- [Error Handling](#error-handling)

---

## Overview

The NetBox Diode CLI (`netbox-dio`) provides a command-line interface for deploying network infrastructure to NetBox Diode via gRPC.

**Features:**
- Create devices with nested interfaces, VLANs, and IP addresses
- Bulk site provisioning
- Dry-run mode for validation
- JSON/YAML input support
- GPRC encryption and authentication

**Package name:** `netbox-dio`

---

## Installation

### From pip

```bash
pip install netbox-dio
```

### From source

```bash
git clone <repo-url>
cd netbox-dio-deploy
pip install -e .
```

### Environment Setup

```bash
export DIODE_ENDPOINT="grpc://diode.example.com:50051"
export DIODE_CLIENT_ID="your-client-id"
export DIODE_CLIENT_SECRET="your-client-secret"
```

---

## Basic Commands

### Help

```bash
netbox-dio --help
netbox-dio device --help
netbox-dio site --help
```

### Version

```bash
netbox-dio --version
```

### Configuration

```bash
netbox-dio config --help
netbox-dio config show
netbox-dio config set endpoint <url>
netbox-dio config set client_id <id>
netbox-dio config set dry_run true
```

---

## Device Deployment

### Create Device from File

```bash
netbox-dio device create device.json
```

**Input file format (device.json):**
```json
{
  "name": "switch-01",
  "site": "dc-east",
  "device_type": "cisco-c9200",
  "role": "access",
  "interfaces": [
    {
      "name": "GigabitEthernet1/0/1",
      "type": "physical",
      "enabled": true,
      "mode": "access",
      "untagged_vlan": "VLAN100"
    }
  ],
  "vlans": [
    {
      "name": "VLAN100",
      "vid": 100,
      "site": "dc-east",
      "status": "active"
    }
  ]
}
```

### Create Device from JSON String

```bash
echo '{"name": "router-01", "site": "dc-west", "device_type": "cisco-asr1001", "role": "edge"}' \| netbox-dio device create
```

### Create Device Explicitly Named

```bash
netbox-dio device create --name switch-01 \
  --site dc-east \
  --device-type cisco-c9200 \
  --role access \
  --status active \
  --position 10 \
  --rack rack-01
```

### Update Device

```bash
netbox-dio device update device.json
```

### Update Device by Name

```bash
netbox-dio device update switch-01 \
  --status planned \
  --description "Maintenance window"
```

### Delete Device

```bash
netbox-dio device delete switch-01
```

### Delete Multiple Devices

```bash
netbox-dio device delete switch-01 switch-02 switch-03
```

### Dry Run Device Creation

```bash
echo '{"name": "switch-01", "site": "dc-east", "device_type": "cisco-c9200", "role": "access"}' \| \
netbox-dio device create --dry-run
```

**Dry-run output:**
```
VERIFIED: device-1
  - interfaces: 5
  - vlans: 3
  - modules: 2
Generated JSON validation passed
```

### Create Device with Progress Bar

```bash
netbox-dio device create device.json --progress
```

---

## CLI Device Creation Examples

### Minimal Device

```bash
netbox-dio device create <<EOF
{
  "name": "minimal-switch",
  "site": "dc-east",
  "device_type": "cisco-c9200",
  "role": "access"
}
EOF
```

### Full Device with Interfaces

```bash
netbox-dio device create <<'EOF'
{
  "name": "core-router",
  "site": "dc-central",
  "device_type": "cisco-asr1002",
  "role": "core",
  "rack": "core-rack",
  "position": 10.0,
  "serial": "FCW12345678",
  "interfaces": [
    {
      "name": "GigabitEthernet0/0/0",
      "type": "physical",
      "enabled": true,
      "speed": 1000,
      "duplex": "full",
      "vrf": "main"
    },
    {
      "name": "Loopback0",
      "type": "virtual",
      "enabled": true,
      "description": "Management interface"
    }
  ],
  "ip_addresses": [
    {
      "address": "10.0.0.1/32",
      "status": "active",
      "assigned_object_interface": "Loopback0",
      "dns_name": "core-router.example.com"
    }
  ],
  "cables": [
    {
      "type": "cat6",
      "status": "connected",
      "a_termination": {
        "device": "core-router",
        "interface": {"name": "GigabitEthernet0/0/0"}
      },
      "b_termination": {
        "device": "firewall-01",
        "interface": {"name": "GigabitEthernet0/0/0"}
      }
    }
  ]
}
EOF
```

### Switch Stack Device

```bash
netbox-dio device create <<EOF
{
  "name": "stack-switches",
  "site": "dc-east",
  "device_type": "cisco-c9300",
  "role": "core",
  "cluster": "stack-01",
  "rack": "rack-01",
  "position": 10.0,
  "rack_positions": [
    {"rack": "rack-01", "position": 10.0},
    {"rack": "rack-01", "position": 12.0},
    {"rack": "rack-01", "position": 14.0}
  ]
}
EOF
```

### Chassis with Modules

```bash
netbox-dio device create <<EOF
{
  "name": "c9500-chassis",
  "site": "dc-central",
  "device_type": "cisco-c9500-chassis",
  "role": "core",
  "modules": [
    {
      "module_type": "sup-140",
      "slot": 1,
      "serial": "FCW2123A0QX",
      "status": "active"
    },
    {
      "module_type": "fabric-3",
      "slot": 2,
      "serial": "FCW2123A0QY",
      "status": "active"
    }
  ],
  "module_bays": [
    {"slot": 1, "module": "sup-140"},
    {"slot": 2, "module": "fabric-3"}
  ]
}
EOF
```

---

## Site Management

### Create Site with Infrastructure

```bash
netbox-dio site create <<EOF
{
  "name": "new-site",
  "facility": "Building A, Floor 2",
  "description": "New data center location",
  "vlans": [
    {"name": "VLAN100", "vid": 100, "status": "active"},
    {"name": "VLAN200", "vid": 200, "status": "active"}
  ],
  "devices": [
    {"name": "core-switch", "device_type": "cisco-c9500", "role": "core"}
  ]
}
EOF
```

### Show Site Summary

```bash
netbox-dio site show dc-east
netbox-dio site show --all
```

### List Sites

```bash
netbox-dio site list
netbox-dio site list --format json
netbox-dio site list --format yaml
```

---

## Batch Operations

### Bulk Device Creation

```bash
for i in {1..10}; do
  cat <<EOF
{
  "name": "switch-$i",
  "site": "dc-east",
  "device_type": "cisco-c9200",
  "role": "access"
}
EOF
done | netbox-dio device create-batch
```

### Batch with JSONL Format

```bash
# Create devices.jsonl
echo '{"name":"switch-01","site":"dc-east","device_type":"cisco-c9200","role":"access"}' > devices.jsonl
echo '{"name":"switch-02","site":"dc-east","device_type":"cisco-c9200","role":"access"}' >> devices.jsonl
echo '{"name":"switch-03","site":"dc-east","device_type":"cisco-c9200","role":"access"}' >> devices.jsonl

# Process all at once
netbox-dio device batch devices.jsonl
```

### Batch Create with Progress

```bash
netbox-dio device batch devices.jsonl --progress --summary
```

### Batch with Dry Run

```bash
netbox-dio device batch devices.jsonl --dry-run
```

---

## Error Handling

### Verbose Error Output

```bash
netbox-dio device create device.json --verbose
```

### Output Detailed Error

```bash
netbox-dio device create device.json -e
```

### Error Recovery

```bash
netbox-dio device create device.json --on-error continue
```

### Retry Failed Operations

```bash
netbox-dio device create devices.jsonl --retry
```

---

## Output Formats

### JSON Output

```bash
netbox-dio device show switch-01 --format json
netbox-dio site list --format json
```

### YAML Output

```bash
netbox-dio device show switch-01 --format yaml
```

### Human-Readable

```bash
netbox-dio device show switch-01 --format text
```

### CSV Output

```bash
netbox-dio site list --format csv
```

---

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DIODE_ENDPOINT` | gRPC endpoint URL | Required |
| `DIODE_CLIENT_ID` | OAuth2 client ID | - |
| `DIODE_CLIENT_SECRET` | OAuth2 client secret | - |
| `DIODE_CERT_FILE` | TLS certificate path | - |
| `DIODE_SKIP_TLS_VERIFY` | Skip TLS verification | false |
| `DIODE_TIMEOUT` | gRPC timeout (seconds) | 30 |

### CLI Configuration File

```bash
# Create config
netbox-dio config init

# Edit config
netbox-dio config edit
```

**Config file format (~/.netbox-dio/config.yaml):**
```yaml
endpoint: "grpc://diode.example.com:50051"
client_id: "your-client-id"
client_secret: "your-client-secret"
skip_tls_verify: false
timeout: 30
dry_run: false
```

---

## Common Patterns

### Pattern 1: Create Device with Interface

```bash
netbox-dio device create <<'EOF'
{
  "name": "access-switch-01",
  "site": "dc-east",
  "device_type": "cisco-c9200",
  "role": "access",
  "interfaces": [
    {
      "name": "GigabitEthernet1/0/1",
      "type": "physical",
      "enabled": true,
      "mode": "access",
      "untagged_vlan": "VLAN100"
    },
    {
      "name": "GigabitEthernet1/0/24",
      "type": "physical",
      "enabled": true,
      "mode": "trunk",
      "vlans": [10, 20, 100]
    }
  ],
  "vlans": [
    {"name": "VLAN100", "vid": 100, "site": "dc-east", "status": "active"}
  ]
}
EOF
```

### Pattern 2: Update VLAN Role

```bash
netbox-dio vlan update VLAN100 --role management --site dc-east
```

### Pattern 3: Remove All Interfaces from Device

```bash
netbox-dio device update switch-01 --remove-interfaces
```

### Pattern 4: Add VLAN to Existing Device

```bash
netbox-dio device append switch-01 --vlan VLAN100
```

### Pattern 5: Create Network Stack (Device + VLANs + IP)

```bash
netbox-dio device create <<'EOF'
{
  "name": "router-01",
  "site": "dc-east",
  "device_type": "cisco-iosv",
  "role": "edge",
  "interfaces": [
    {"name": "GigabitEthernet0/0/0", "type": "physical"},
    {"name": "GigabitEthernet0/0/1", "type": "physical"},
    {"name": "Loopback0", "type": "virtual"}
  ],
  "vlans": [
    {"name": "WAN-01", "vid": 10, "site": "dc-east"},
    {"name": "LAN-01", "vid": 20, "site": "dc-east"}
  ],
  "ip_addresses": [
    {"address": "10.0.0.1/32", "assigned_object_interface": "Loopback0"},
    {"address": "192.168.1.1/24", "assigned_object_interface": "Vlan10"}
  ]
}
EOF
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | Connection error |
| 4 | Permission denied |
| 5 | Resource not found |

---

## Troubleshooting

### Check Connection

```bash
netbox-dio connectivity check
```

### Validate Input

```bash
netbox-dio validate device.json
```

### Debug Mode

```bash
netbox-dio device create device.json --debug
```

### Clean State

```bash
netbox-dio config reset
netbox-dio device delete --force switch-01
```

---

## CLI Help Reference

```
netbox-dio [OPTIONS] COMMAND [ARGS]...

Options:
  --endpoint TEXT     gRPC endpoint
  --client-id TEXT    OAuth2 client ID
  --client-secret TEXT    OAuth2 client secret
  --tls-profile TEXT  TLS configuration profile
  --timeout INTEGER   Request timeout in seconds
  --dry-run           Validate without executing
  --verbose           Verbose output
  --debug             Debug mode
  --format FORMAT     Output format (json, yaml, text)
  --help              Show this message

Commands:
  device    Device management
  interface Interface management
  vlan      VLAN management
  ip        IP address management
  prefix    Prefix management
  module    Module management
  cable     Cable management
  site      Site management
  config    Configuration management
  validate  Validate input files

Examples:
  netbox-dio device create device.json
  netbox-dio device list --site dc-east
  netbox-dio vlan create-vlans batch.jsonl
  netbox-dio validate device.json --strict
```

---

## Quick Start

### 1. Install and Configure

```bash
pip install netbox-dio
export DIODE_ENDPOINT="grpc://10.0.0.1:50051"
export DIODE_CLIENT_ID="client"
export DIODE_CLIENT_SECRET="secret"
```

### 2. Create Sample Device

```bash
cat > device.json <<'EOF'
{
  "name": "switch-01",
  "site": "dc-east",
  "device_type": "cisco-c9200",
  "role": "access",
  "interfaces": [
    {"name": "GigabitEthernet1/0/1", "type": "physical"}
  ]
}
EOF
```

### 3. Deploy

```bash
netbox-dio device create device.json
```

### 4. Verify

```bash
netbox-dio device show switch-01
```

---

## Best Practices

### 1. Always Use Dry-Run First

```bash
netbox-dio device create device.json --dry-run
```

### 2. Validate JSON Before Deploy

```bash
cat device.json | netbox-dio validate -
```

### 3. Use JSONL for Bulk Operations

```bash
# devices.jsonl - one device per line
{"name":"switch-01","site":"dc-east","device_type":"cisco-c9200","role":"access"}
{"name":"switch-02","site":"dc-east","device_type":"cisco-c9200","role":"access"}
```

### 4. Monitor Progress

```bash
netbox-dio device batch devices.jsonl --progress --summary
```

### 5. Error Handling

```bash
netbox-dio device batch devices.jsonl --on-error continue --retry
```

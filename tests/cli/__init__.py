"""CLI test package for NetBox Diode Device Wrapper.

This package contains tests for the command-line interface module that provides
import/export functionality for device data to/from NetBox Diode.

Requirements:
    CLI-01: CLI tool for importing device data from files
    CLI-02: CLI tool for exporting device data to multiple formats
    CLI-03: CLI tool for dry-run mode and batch processing

Test Modules:
    test_basic_structure: Verifies CLI module structure and command registration
    test_import_commands: Tests file import functionality (JSON, YAML, stdin)
    test_export_commands: Tests file export functionality (JSON, YAML, NetBox YAML)
    test_dry_run: Tests dry-run mode for safe validation without API calls
    test_batch: Tests batch processing with configurable chunk sizes
    test_integration: End-to-end integration tests combining multiple features
"""

import pytest

# Import test modules for automatic discovery
from . import test_basic_structure
from . import test_import_commands
from . import test_export_commands
from . import test_dry_run
from . import test_batch
from . import test_integration

"""Test suite for error handling and validation.

This package contains tests for:
- Exception hierarchy and inheritance
- Validation error messages
- Conversion error handling
- I/O layer error handling
- Batch error aggregation
"""

import pytest

# Pytest markers for organizing error tests
pytest.register_assert_rewrite("tests.errors")

# Marker for error handling tests
def pytest_configure(config):
    """Register custom pytest markers for error tests."""
    config.addinivalue_line("markers", "errors: tests for error handling functionality")
    config.addinivalue_line("markers", "validation: tests for data validation")
    config.addinivalue_line("markers", "conversion: tests for data conversion")
    config.addinivalue_line("markers", "io: tests for I/O layer errors")
    config.addinivalue_line("markers", "batch: tests for batch error aggregation")

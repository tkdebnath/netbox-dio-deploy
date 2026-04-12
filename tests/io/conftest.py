# Pytest fixtures for I/O tests
# This file provides shared test data for I/O layer tests

import pytest
import os


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment variables before each test."""
    # Store current env
    env_backup = {}
    for key in list(os.environ.keys()):
        if key.startswith("DIODE_"):
            env_backup[key] = os.environ.pop(key)

    yield

    # Restore env
    os.environ.update(env_backup)

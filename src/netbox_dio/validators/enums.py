"""Severity enum for validation results.

This module defines the Severity enum used by the validation framework.
"""

from enum import Enum


class Severity(Enum):
    """Severity levels for validation results.

    | Severity | Description | Impact on Device |
    |----------|-------------|------------------|
    | ERROR | Validation fails, device should not be sent to Diode | Blocks transmission |
    | WARNING | Issue detected but device may still be valid | Logs warning |
    | INFO | Informational message, no validation issue | Logs for debugging |
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

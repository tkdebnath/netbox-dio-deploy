"""Quality metrics module for Diode devices.

This module provides data quality metrics calculations and reporting
for network infrastructure devices.

Usage:
    from netbox_dio import DiodeDevice, QualityReporter

    # Create a device
    device = DiodeDevice.from_dict({
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router"
    })

    # Calculate quality metrics
    reporter = QualityReporter()
    metrics = reporter.calculate_metrics(device)

    # Generate a report
    report = reporter.generate_report(device, metrics)
    print(report)
"""

from .metrics import QualityMetrics, FieldQuality, CompletenessCalculator, ValidityCalculator
from .reporter import QualityReporter

__all__ = [
    "QualityMetrics",
    "FieldQuality",
    "CompletenessCalculator",
    "ValidityCalculator",
    "QualityReporter",
]

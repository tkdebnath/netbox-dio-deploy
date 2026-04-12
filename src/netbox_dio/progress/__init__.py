"""Progress tracking module for batch operations.

This module provides progress bar visualization and tracking for
large batch operations using the rich library.

Usage:
    from netbox_dio.progress import ProgressManager

    with ProgressManager(total=1000, description="Processing") as progress:
        for i in range(1000):
            progress.increment()
            # Process device i
"""

from .manager import ProgressManager, MockProgressManager

__all__ = ["ProgressManager", "MockProgressManager"]

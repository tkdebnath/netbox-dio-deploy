"""Progress manager for batch operations with rich progress bars.

This module provides a high-level interface for visual progress
tracking during batch device processing operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

try:
    from rich.progress import (
        Progress,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
        TimeColumn,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from rich.console import Console
    RICH_CONSOLE_AVAILABLE = True
except ImportError:
    RICH_CONSOLE_AVAILABLE = False


@dataclass
class ProgressStats:
    """Statistics for a progress tracking session."""

    total: int
    completed: int = 0
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    current_rate: float = 0.0  # items per second
    estimated_remaining_ms: Optional[float] = None

    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.started_at is None:
            return 0.0
        end = self.finished_at or time.time()
        return (end - self.started_at) * 1000

    @property
    def throughput_sps(self) -> float:
        """Get throughput in items per second."""
        if self.elapsed_ms == 0:
            return 0.0
        return (self.completed / self.elapsed_ms) * 1000

    def update(self, completed: int, rate: float, remaining_ms: Optional[float] = None) -> None:
        """Update progress statistics.

        Args:
            completed: Number of items completed
            rate: Current processing rate (items/second)
            remaining_ms: Estimated remaining time in milliseconds
        """
        self.completed = completed
        self.current_rate = rate
        self.estimated_remaining_ms = remaining_ms


class ProgressManager:
    """Manage progress bars for batch operations.

    Provides both visual progress bars (when rich is available)
    and statistics tracking for batch processing operations.

    Usage:
        >>> with ProgressManager(total=1000, description="Processing") as pm:
        ...     for i in range(1000):
        ...         pm.update(i + 1)
        ...         # Process device i

    Attributes:
        total: Total number of items to process
        description: Progress bar description
        completed: Number of items processed
        started_at: Start timestamp (seconds since epoch)
        finished_at: Finish timestamp (seconds since epoch)
        stats: ProgressStats dataclass with computed metrics
    """

    def __init__(
        self,
        total: int,
        description: str = "Processing",
        show_bar: bool = True,
    ) -> None:
        """Initialize the progress manager.

        Args:
            total: Total number of items to process
            description: Description text for the progress bar
            show_bar: Whether to display the visual progress bar
        """
        self.total = max(1, total)  # Ensure at least 1 for division
        self.description = description
        self.show_bar = show_bar
        self._progress = None
        self._task_id = None
        self._started_at: Optional[float] = None
        self._finished_at: Optional[float] = None
        self._completed = 0
        self._last_update_time: Optional[float] = None
        self._last_update_count: int = 0
        self._current_rate: float = 0.0

        # Initialize rich progress if available
        if RICH_AVAILABLE and show_bar:
            self._progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=None),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                TimeColumn(),
                transient=True,
            )
            self._task_id = self._progress.add_task(
                description=description,
                total=total,
            )

    @property
    def completed(self) -> int:
        """Get the number of completed items."""
        return self._completed

    @property
    def started_at(self) -> Optional[float]:
        """Get the start timestamp."""
        return self._started_at

    @property
    def finished_at(self) -> Optional[float]:
        """Get the finish timestamp."""
        return self._finished_at

    @property
    def stats(self) -> ProgressStats:
        """Get current progress statistics."""
        return ProgressStats(
            total=self.total,
            completed=self._completed,
            started_at=self._started_at,
            finished_at=self._finished_at,
            current_rate=self._current_rate,
            estimated_remaining_ms=self._estimate_remaining_ms(),
        )

    def _estimate_remaining_ms(self) -> Optional[float]:
        """Estimate remaining time in milliseconds."""
        if self._completed == 0 or self._current_rate <= 0:
            return None
        remaining = self.total - self._completed
        return (remaining / self._current_rate) * 1000

    def start(self) -> None:
        """Start the progress bar."""
        if self._progress:
            self._progress.start()
        self._started_at = time.time()
        self._last_update_time = self._started_at
        self._last_update_count = 0

    def update(self, completed: int) -> None:
        """Update progress to the specified value.

        Args:
            completed: The number of items completed
        """
        self._completed = min(completed, self.total)

        # Calculate throughput (always, regardless of rich availability)
        current_time = time.time()
        if self._last_update_time:
            elapsed = current_time - self._last_update_time
            if elapsed > 0:
                items_since_last = self._completed - self._last_update_count
                self._current_rate = items_since_last / elapsed
        self._last_update_time = current_time
        self._last_update_count = self._completed

        if not self._progress:
            return

        self._progress.update(self._task_id, completed=self._completed)

    def increment(self, delta: int = 1) -> None:
        """Increment progress by delta.

        Args:
            delta: Number of items to increment (default 1)
        """
        self.update(self._completed + delta)

    def finish(self) -> None:
        """Complete and hide the progress bar."""
        if self._progress:
            self._progress.update(self._task_id, completed=self.total)
            self._progress.stop()
        self._completed = self.total
        self._finished_at = time.time()

    def __enter__(self) -> "ProgressManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.finish()


class MockProgressManager:
    """Mock progress manager for testing without rich.

    Provides the same interface as ProgressManager but without
    visual output, useful for unit testing.
    """

    def __init__(self, total: int, description: str = "Processing") -> None:
        """Initialize the mock progress manager.

        Args:
            total: Total number of items to process
            description: Description text (for reference)
        """
        self.total = max(1, total)
        self.description = description
        self._started_at: Optional[float] = None
        self._finished_at: Optional[float] = None
        self._completed = 0
        self._current_rate: float = 0.0

    @property
    def completed(self) -> int:
        """Get the number of completed items."""
        return self._completed

    @property
    def started_at(self) -> Optional[float]:
        """Get the start timestamp."""
        return self._started_at

    @property
    def finished_at(self) -> Optional[float]:
        """Get the finish timestamp."""
        return self._finished_at

    @property
    def stats(self) -> ProgressStats:
        """Get current progress statistics."""
        return ProgressStats(
            total=self.total,
            completed=self._completed,
            started_at=self._started_at,
            finished_at=self._finished_at,
            current_rate=self._current_rate,
            estimated_remaining_ms=self._estimate_remaining_ms(),
        )

    def _estimate_remaining_ms(self) -> Optional[float]:
        """Estimate remaining time in milliseconds.

        Returns:
            Estimated remaining time in milliseconds, or None if not enough data
        """
        if self._completed == 0 or self._current_rate <= 0:
            return None
        remaining = self.total - self._completed
        return (remaining / self._current_rate) * 1000

    def start(self) -> None:
        """Start the progress tracking."""
        self._started_at = time.time()

    def update(self, completed: int) -> None:
        """Update progress to the specified value.

        Args:
            completed: The number of items completed
        """
        self._completed = min(completed, self.total)
        current_time = time.time()
        if self._started_at:
            elapsed = current_time - self._started_at
            if elapsed > 0:
                self._current_rate = self._completed / elapsed

    def increment(self, delta: int = 1) -> None:
        """Increment progress by delta.

        Args:
            delta: Number of items to increment (default 1)
        """
        self.update(self._completed + delta)

    def finish(self) -> None:
        """Complete the progress tracking."""
        self._completed = self.total
        self._finished_at = time.time()

    def __enter__(self) -> "MockProgressManager":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.finish()

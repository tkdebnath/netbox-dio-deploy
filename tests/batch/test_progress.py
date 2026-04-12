"""Tests for the progress manager.

This module tests the ProgressManager class for visual progress tracking.
"""

import pytest

from netbox_dio.progress import ProgressManager, MockProgressManager


class TestMockProgressManager:
    """Tests for the MockProgressManager."""

    def test_creation(self):
        """Test creating a mock progress manager."""
        pm = MockProgressManager(total=1000, description="Test")
        assert pm.total == 1000
        assert pm.description == "Test"
        assert pm.completed == 0
        assert pm.started_at is None
        assert pm.finished_at is None

    def test_start(self):
        """Test starting the progress manager."""
        pm = MockProgressManager(total=1000)
        pm.start()
        assert pm.started_at is not None
        assert pm.finished_at is None

    def test_update(self):
        """Test updating progress."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(500)
        assert pm.completed == 500

    def test_increment(self):
        """Test incrementing progress."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.increment(100)
        assert pm.completed == 100

    def test_finish(self):
        """Test finishing progress."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(500)
        pm.finish()
        assert pm.finished_at is not None
        assert pm.completed == 1000

    def test_stats(self):
        """Test getting progress stats."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(500)
        stats = pm.stats
        assert stats.total == 1000
        assert stats.completed == 500
        assert stats.percentage == 50.0

    def test_stats_with_time(self):
        """Test stats calculation with time."""
        import time
        pm = MockProgressManager(total=1000)
        pm.start()
        time.sleep(0.1)
        pm.update(100)
        stats = pm.stats
        assert stats.completed == 100
        assert stats.estimated_remaining_ms is not None
        assert stats.throughput_sps > 0


class TestMockProgressManagerContextManager:
    """Tests for progress manager as context manager."""

    def test_context_manager(self):
        """Test using progress manager as context manager."""
        with MockProgressManager(total=1000, description="Test") as pm:
            pm.update(500)
            assert pm.completed == 500
            assert pm.started_at is not None
        assert pm.finished_at is not None

    def test_context_manager_with_increment(self):
        """Test incrementing inside context manager."""
        with MockProgressManager(total=1000) as pm:
            for _ in range(10):
                pm.increment(10)
            assert pm.completed == 100


class TestMockProgressManagerThroughput:
    """Tests for progress manager throughput calculation."""

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        import time
        pm = MockProgressManager(total=1000)
        pm.start()
        time.sleep(0.1)
        pm.update(100)
        stats = pm.stats
        assert stats.throughput_sps > 0

    def test_throughput_units(self):
        """Test that throughput is in correct units."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(100)
        stats = pm.stats
        # Throughput should be items per second
        assert isinstance(stats.throughput_sps, float)
        assert stats.throughput_sps >= 0


class TestProgressManagerContextManager:
    """Tests for ProgressManager context manager behavior."""

    def test_context_manager_lifecycle(self):
        """Test the complete lifecycle using context manager."""
        with ProgressManager(total=100, description="Test") as pm:
            assert pm.started_at is not None
            pm.update(50)
            assert pm.completed == 50
        assert pm.finished_at is not None


class TestProgressManagerStats:
    """Tests for progress stats calculations."""

    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        with ProgressManager(total=200) as pm:
            pm.update(50)
            assert pm.stats.percentage == 25.0

    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        import time
        with ProgressManager(total=1000) as pm:
            time.sleep(0.1)
            pm.update(100)
            assert pm.stats.elapsed_ms >= 100  # At least 100ms

    def test_remaining_time(self):
        """Test remaining time estimation."""
        import time
        with ProgressManager(total=1000) as pm:
            time.sleep(0.1)
            pm.update(100)
            stats = pm.stats
            # Should estimate some remaining time
            assert stats.estimated_remaining_ms is not None
            assert stats.estimated_remaining_ms > 0

    def test_estimate_accuracy(self):
        """Test estimation accuracy."""
        with ProgressManager(total=1000) as pm:
            pm.update(500)
            stats = pm.stats
            # Should have some estimate
            assert stats.estimated_remaining_ms is not None


class TestMockProgressManagerConsistency:
    """Tests for mock progress manager consistency."""

    def test_completion_consistency(self):
        """Test that completion is consistent."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(100)
        assert pm.completed == 100
        pm.update(200)
        assert pm.completed == 200

    def test_stats_after_finish(self):
        """Test stats after finish."""
        pm = MockProgressManager(total=1000)
        pm.start()
        pm.update(500)
        pm.finish()
        stats = pm.stats
        assert stats.completed == 1000
        assert stats.finished_at is not None

    def test_multiple_updates(self):
        """Test multiple sequential updates."""
        pm = MockProgressManager(total=1000)
        pm.start()
        for i in range(1, 11):
            pm.update(i * 100)
            assert pm.completed == i * 100

    def test_increment_sequence(self):
        """Test sequential increments."""
        pm = MockProgressManager(total=1000)
        pm.start()
        for _ in range(10):
            pm.increment(100)
        assert pm.completed == 1000

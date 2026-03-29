import threading

from src.config.settings import Settings
from src.core.circuit_breaker import CircuitBreaker


class TestCircuitBreakerEdgeCases:
    def test_multiple_failures_reset(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_open is True
        cb.record_success()
        assert cb.is_open is False

    def test_concurrent_access(self):
        cb = CircuitBreaker(failure_threshold=10)

        def writer():
            for _ in range(100):
                cb.record_failure()

        def reader():
            for _ in range(100):
                _ = cb.can_execute()

        threads = [threading.Thread(target=writer) for _ in range(2)] + [
            threading.Thread(target=reader) for _ in range(2)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert cb._failures > 0


class TestSettingsMetrics:
    def test_increment_metric(self):
        initial = Settings.get_metrics()["frames_processed"]
        Settings.increment_metric("frames_processed", 5)
        assert Settings.get_metrics()["frames_processed"] == initial + 5

    def test_uptime_is_positive(self):
        metrics = Settings.get_metrics()
        assert metrics["uptime_seconds"] >= 0

    def test_get_metrics_returns_dict(self):
        m = Settings.get_metrics()
        assert "frames_processed" in m
        assert "vlm_calls" in m
        assert "alerts_triggered" in m
        assert "uptime_seconds" in m

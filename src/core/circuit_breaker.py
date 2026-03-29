import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    _failures: int = field(default=0, init=False)
    _last_failure: float = field(default=0.0, init=False)
    _is_open: bool = field(default=False, init=False)

    def record_failure(self) -> None:
        self._failures += 1
        self._last_failure = time.time()
        if self._failures >= self.failure_threshold:
            self._is_open = True
            logger.warning(
                f"Circuit breaker OPEN after {self._failures} failures "
                f"(recovery in {self.recovery_timeout}s)"
            )

    def record_success(self) -> None:
        self._failures = 0
        self._is_open = False

    def can_execute(self) -> bool:
        if not self._is_open:
            return True
        if time.time() - self._last_failure > self.recovery_timeout:
            logger.info("Circuit breaker HALF-OPEN — allowing test request")
            self._is_open = False
            self._failures = 0
            return True
        return False

    @property
    def is_open(self) -> bool:
        return self._is_open

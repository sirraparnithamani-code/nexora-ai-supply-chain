"""Base agent class and execution context timing utilities."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Generator

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all specialized supply chain agents."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name.lower().replace(' ', '_')}")

    @contextmanager
    def measure_latency(self) -> Generator[dict[str, float], None, None]:
        """Measure execution wall-clock time in milliseconds."""
        timer: dict[str, float] = {"elapsed_ms": 0.0}
        start = time.perf_counter()
        try:
            yield timer
        finally:
            elapsed = (time.perf_counter() - start) * 1000.0
            timer["elapsed_ms"] = round(elapsed, 2)
            self.logger.info(f"{self.agent_name} executed in {timer['elapsed_ms']} ms")

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent reasoning cycle."""
        pass

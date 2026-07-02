"""
Observability Module.
Provides decorators and utilities for profiling execution time and tracking metrics.
"""

import time
import logging
from functools import wraps
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsRegistry:
    _timings: Dict[str, float] = {}

    @classmethod
    def record_time(cls, name: str, elapsed: float):
        if name not in cls._timings:
            cls._timings[name] = 0.0
        cls._timings[name] += elapsed

    @classmethod
    def print_report(cls):
        logger.info("=== Performance Report ===")
        total = sum(cls._timings.values())
        for name, elapsed in cls._timings.items():
            logger.info(f"{name:.<30} {elapsed * 1000:.2f} ms")
        logger.info(f"{'Total':.<30} {total * 1000:.2f} ms")
        logger.info("==========================")

def time_it(name: str):
    """Decorator to profile a function and log to MetricsRegistry."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            MetricsRegistry.record_time(name, elapsed)
            return result
        return wrapper
    return decorator

"""FORGE INFINITY Benchmark Package."""
from backend.benchmark.benchmark_suite import (
    BENCHMARK_BASELINES,
    run_comparative_benchmark,
    run_live_speed_test,
)

__all__ = [
    "BENCHMARK_BASELINES",
    "run_comparative_benchmark",
    "run_live_speed_test",
]

"""
Benchmark: validate_value with pre-compiled TypeAdapter vs creating one each time.
Run: python bench_validate.py
"""

import time
from typing import Annotated
from enum import Enum
from datetime import date, time as time_type

from pydantic import Field, TypeAdapter

from pytypeinput.analyzer import analyze_type
from pytypeinput.validate import validate_value


# ─── Setup ───────────────────────────────────────────────────────────

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


PARAMS = {
    "int_constrained": analyze_type(Annotated[int, Field(ge=0, le=100)], "age", 25),
    "float_constrained": analyze_type(Annotated[float, Field(gt=0.0, lt=1.0)], "ratio", 0.5),
    "str_pattern": analyze_type(Annotated[str, Field(min_length=1, max_length=50)], "name", "test"),
    "str_plain": analyze_type(str, "label", "hello"),
    "int_plain": analyze_type(int, "count", 10),
    "float_plain": analyze_type(float, "score", 3.14),
    "bool_plain": analyze_type(bool, "flag", True),
    "date_field": analyze_type(date, "birthday", date(2000, 1, 1)),
    "time_field": analyze_type(time_type, "alarm", time_type(8, 30)),
    "enum_field": analyze_type(Color, "color", Color.RED),
}

TEST_VALUES_PYTHON = {
    "int_constrained": 42,
    "float_constrained": 0.75,
    "str_pattern": "hello world",
    "str_plain": "test",
    "int_plain": 7,
    "float_plain": 2.71,
    "bool_plain": False,
    "date_field": date(2024, 6, 15),
    "time_field": time_type(14, 30),
    "enum_field": Color.BLUE,
}

TEST_VALUES_JSON = {
    "int_constrained": "42",
    "float_constrained": "0.75",
    "str_pattern": "hello world",
    "str_plain": "test",
    "int_plain": "7",
    "float_plain": "2.71",
    "bool_plain": "true",
    "date_field": "2024-06-15",
    "time_field": "14:30:00",
    "enum_field": "blue",
}


# ─── Baseline: create TypeAdapter each time ──────────────────────────

def validate_no_cache(meta, value):
    """Simulate creating TypeAdapter on every call."""
    if value is None:
        return None

    t = meta.param_type

    if isinstance(value, str) and t is int:
        value = int(value)
    elif isinstance(value, str) and t is float:
        value = float(value)
    elif isinstance(value, str) and t is bool:
        value = value.lower() in ("true", "1", "yes")
    elif isinstance(value, str) and t is date:
        value = date.fromisoformat(value)
    elif isinstance(value, str) and t is time_type:
        value = time_type.fromisoformat(value)
    elif isinstance(value, str) and isinstance(t, type) and issubclass(t, Enum):
        for m in t:
            if m.value == value:
                value = m
                break

    if meta.constraints is not None:
        adapter = TypeAdapter(Annotated[meta.param_type, meta.constraints])
        adapter.validate_python(value)

    return value


# ─── Bench ───────────────────────────────────────────────────────────

def bench(label, fn, params, values, iterations=100_000):
    # Warmup
    for key in params:
        fn(params[key], values[key])

    start = time.perf_counter()
    for _ in range(iterations):
        for key in params:
            fn(params[key], values[key])
    elapsed = time.perf_counter() - start

    total_calls = iterations * len(params)
    per_call_us = (elapsed / total_calls) * 1_000_000

    print(f"{label}")
    print(f"  {total_calls:,} calls in {elapsed:.2f}s")
    print(f"  {per_call_us:.2f} µs/call")
    print()
    return elapsed


if __name__ == "__main__":
    N = 50_000

    print("=" * 60)
    print(f"Benchmark: {N:,} iterations × {len(PARAMS)} params")
    print("=" * 60)
    print()

    # Python native values
    t1 = bench("validate_value (cached TypeAdapter) — Python values",
               validate_value, PARAMS, TEST_VALUES_PYTHON, N)
    t2 = bench("validate_no_cache (new TypeAdapter each time) — Python values",
               validate_no_cache, PARAMS, TEST_VALUES_PYTHON, N)

    print(f"  → Cached is {t2/t1:.1f}x faster with Python values")
    print()

    # JSON string values
    t3 = bench("validate_value (cached TypeAdapter) — JSON values",
               validate_value, PARAMS, TEST_VALUES_JSON, N)
    t4 = bench("validate_no_cache (new TypeAdapter each time) — JSON values",
               validate_no_cache, PARAMS, TEST_VALUES_JSON, N)

    print(f"  → Cached is {t4/t3:.1f}x faster with JSON values")
    print()

    # Per-type breakdown
    print("=" * 60)
    print("Per-type breakdown (cached, Python values, 100k calls)")
    print("=" * 60)
    for key in PARAMS:
        meta = PARAMS[key]
        val = TEST_VALUES_PYTHON[key]
        start = time.perf_counter()
        for _ in range(100_000):
            validate_value(meta, val)
        elapsed = time.perf_counter() - start
        us = (elapsed / 100_000) * 1_000_000
        print(f"  {key:25s} {us:.2f} µs/call")
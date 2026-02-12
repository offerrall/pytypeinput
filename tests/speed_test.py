"""
Benchmark: measures analyze_type performance.
Run with: python benchmark.py
"""
import inspect
import time
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time as time_type
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.types import (
    Label, Description, Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword, Dropdown,
    OptionalEnabled,
    Color, Email, ImageFile, DocumentFile,
)

EMPTY = inspect.Parameter.empty
ITERATIONS = 10_000


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Size(Enum):
    S = 1
    M = 2
    L = 3


def get_colors():
    return ["red", "green", "blue"]


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

SIMPLE = {
    "int":       (int, "n", EMPTY),
    "str":       (str, "s", EMPTY),
    "float":     (float, "f", EMPTY),
    "bool":      (bool, "b", EMPTY),
    "date":      (date, "d", EMPTY),
    "time":      (time_type, "t", EMPTY),
    "int=42":    (int, "n", 42),
    "str='hi'":  (str, "s", "hi"),
}

MEDIUM = {
    "int+ge": (
        Annotated[int, Field(ge=0)], "n", EMPTY
    ),
    "str+len": (
        Annotated[str, Field(min_length=1, max_length=100)], "s", EMPTY
    ),
    "int+slider": (
        Annotated[int, Field(ge=0, le=100), Slider(), Step(5)], "v", EMPTY
    ),
    "str+password": (
        Annotated[str, Field(min_length=8), IsPassword()], "p", EMPTY
    ),
    "enum": (
        Priority, "p", EMPTY
    ),
    "literal": (
        Literal["a", "b", "c"], "x", EMPTY
    ),
    "str|None": (
        str | None, "s", "hi"
    ),
    "Color": (
        Color, "c", EMPTY
    ),
    "Email": (
        Email, "e", EMPTY
    ),
    "list[int]": (
        list[int], "nums", EMPTY
    ),
    "int+default": (
        Annotated[int, Field(ge=0, le=100)], "n", 50
    ),
    "enum+default": (
        Priority, "p", Priority.HIGH
    ),
}

COMPLEX = {
    "5-level slider": (
        Annotated[
            Annotated[
                Annotated[
                    Annotated[
                        Annotated[int, Field(ge=0)],
                        Field(le=100)
                    ],
                    Slider()
                ],
                Step(5)
            ],
            Label("Deep"), Description("Very deep")
        ],
        "v", EMPTY
    ),
    "full slider|None+def": (
        Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)] | None,
        "v", 50
    ),
    "full password": (
        Annotated[str, Label("PW"), Description("D"), Field(min_length=8, max_length=64), IsPassword(), Placeholder("***")],
        "p", EMPTY
    ),
    "full textarea": (
        Annotated[str, Label("Bio"), Description("D"), Field(max_length=5000), Rows(10), Placeholder("...")],
        "b", EMPTY
    ),
    "dropdown+label": (
        Annotated[str, Label("Color"), Placeholder("..."), Dropdown(get_colors)],
        "c", EMPTY
    ),
    "list[slider]+constr": (
        Annotated[list[Annotated[int, Field(ge=0, le=100), Slider(), Step(2)]], Field(min_length=1, max_length=20)],
        "vals", EMPTY
    ),
    "list[enum]+default": (
        list[Priority],
        "p", [Priority.LOW, Priority.HIGH]
    ),
    "list[email]+constr": (
        Annotated[list[Annotated[Email, Label("Mail")]], Field(min_length=1, max_length=10)],
        "emails", EMPTY
    ),
    "override all": (
        Annotated[
            Annotated[int, Field(ge=0, le=100), Slider(), Step(5), Label("Old"), Description("Old")],
            Field(ge=10, le=50), Step(1), Label("New"), Description("New")
        ],
        "v", 25
    ),
    "list[composed]|None": (
        Annotated[
            list[Annotated[Annotated[int, Field(ge=0, le=100), Slider(), Step(2)], Label("Val")]],
            Field(min_length=1, max_length=20)
        ] | None,
        "vals", EMPTY
    ),
    "color+label|None": (
        Annotated[Color, Label("Primary"), Description("Pick")] | None,
        "c", "#FF0000"
    ),
    "list[img]+constr": (
        Annotated[list[Annotated[ImageFile, Label("Photo")]], Field(min_length=1, max_length=5)],
        "imgs", EMPTY
    ),
    "list[str]+default": (
        list[Annotated[str, Field(min_length=1, max_length=30)]],
        "tags", ["hello", "world", "test"]
    ),
}


# =============================================================================
# RUNNER
# =============================================================================

def run_bench(cases: dict) -> dict:
    results = {}
    for name, (ann, n, default) in cases.items():
        for _ in range(100):
            analyze_type(ann, n, default)

        start = time.perf_counter()
        for _ in range(ITERATIONS):
            analyze_type(ann, n, default)
        elapsed = time.perf_counter() - start

        fps = ITERATIONS / elapsed

        results[name] = {
            "total_ms": round(elapsed * 1000, 2),
            "per_call_us": round((elapsed / ITERATIONS) * 1_000_000, 2),
            "calls_per_sec": round(fps),
            "fps": f"{fps:,.0f}" if fps >= 1000 else f"{fps:,.1f}",
        }
    return results


def print_section(label: str, results: dict):
    avg_us = sum(r["per_call_us"] for r in results.values()) / len(results)
    avg_cps = sum(r["calls_per_sec"] for r in results.values()) / len(results)

    print(f"\n  {label}")
    print(f"  {'─' * 72}")
    print(f"  {'Type':<30} {'μs/call':>10} {'calls/s':>12} {'fps':>12}")
    print(f"  {'─' * 72}")
    for name, data in results.items():
        print(f"  {name:<30} {data['per_call_us']:>10} {data['calls_per_sec']:>12,} {data['fps']:>12}")
    print(f"  {'─' * 72}")
    print(f"  {'AVG':<30} {round(avg_us, 2):>10} {round(avg_cps):>12,} {f'{avg_cps:,.0f}':>12}")


def main():
    print(f"\n{'═' * 76}")
    print(f"  PyTypeInput Benchmark — {ITERATIONS:,} iterations per type")
    print(f"{'═' * 76}")

    simple = run_bench(SIMPLE)
    medium = run_bench(MEDIUM)
    complex_ = run_bench(COMPLEX)

    print_section("SIMPLE (bare types)", simple)
    print_section("MEDIUM (1-2 layers)", medium)
    print_section("COMPLEX (deep composition)", complex_)

    s_avg = sum(r["per_call_us"] for r in simple.values()) / len(simple)
    m_avg = sum(r["per_call_us"] for r in medium.values()) / len(medium)
    c_avg = sum(r["per_call_us"] for r in complex_.values()) / len(complex_)

    s_fps = sum(r["calls_per_sec"] for r in simple.values()) / len(simple)
    m_fps = sum(r["calls_per_sec"] for r in medium.values()) / len(medium)
    c_fps = sum(r["calls_per_sec"] for r in complex_.values()) / len(complex_)

    print(f"\n  {'═' * 50}")
    print(f"  SUMMARY")
    print(f"  {'─' * 50}")
    print(f"  {'':30} {'μs/call':>10} {'fps':>10}")
    print(f"  {'─' * 50}")
    print(f"  {'Simple avg':<30} {round(s_avg, 2):>10} {f'{s_fps:,.0f}':>10}")
    print(f"  {'Medium avg':<30} {round(m_avg, 2):>10} {f'{m_fps:,.0f}':>10}")
    print(f"  {'Complex avg':<30} {round(c_avg, 2):>10} {f'{c_fps:,.0f}':>10}")
    print(f"  {'─' * 50}")
    print(f"  Ratio medium/simple:  {round(m_avg / s_avg, 1)}x slower, {round(s_fps / m_fps, 1)}x less fps")
    print(f"  Ratio complex/simple: {round(c_avg / s_avg, 1)}x slower, {round(s_fps / c_fps, 1)}x less fps")
    print(f"  {'═' * 50}\n")


if __name__ == "__main__":
    main()
import inspect
import pytest
from typing import Union, Annotated, Literal
from datetime import date, time
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.extractors.validate_optional_02 import extract_optional
from pytypeinput.param import OptionalMetadata
from pytypeinput.types import OptionalEnabled, OptionalDisabled


EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


NOT_OPTIONAL = [
    str, int, float, bool, date, time,
    Annotated[str, Field(min_length=3)],
    list[str], list[int],
    Priority,
    Literal["a", "b", "c"],
]

OPTIONAL_DISABLED_NO_DEFAULT = [
    str | None,
    int | None,
    float | None,
    bool | None,
    date | None,
    time | None,
    None | str,
    None | int,
    Union[str, None],
    Union[None, str],
    Union[list[str], None],
    list[str] | None,
    Annotated[str, Field(min_length=3)] | None,
    Priority | None,
    Literal["a", "b"] | None,
    Literal[1, 2, 3] | None,
]

OPTIONAL_DISABLED_DEFAULT_NONE = [
    str | None,
    int | None,
    float | None,
    bool | None,
    list[str] | None,
    Priority | None,
]

OPTIONAL_ENABLED = [
    (str | None,                "hello"),
    (str | None,                ""),
    (int | None,                42),
    (int | None,                -10),
    (int | None,                0),
    (int | None,                -0),
    (float | None,              3.14),
    (float | None,              -2.5),
    (float | None,              0.0),
    (float | None,              -0.0),
    (bool | None,               True),
    (bool | None,               False),
    (list[str] | None,          ["a", "b"]),
    (list[str] | None,          []),
    (Priority | None,           Priority.LOW),
    (Status | None,             Status.INACTIVE),
    (Literal["a", "b"] | None,  "a"),
    (date | None,               date.today()),
    (date | None,               date.min),
    (time | None,               time(14, 30)),
    (time | None,               time(0, 0)),
    (Union[str, None],          "test"),
    (None | str,                "hello"),
]

MARKER_ENABLED = [
    (str | OptionalEnabled,         EMPTY),
    (str | OptionalEnabled,         None),
    (str | OptionalEnabled,         "hello"),
    (str | OptionalEnabled,         ""),
    (int | OptionalEnabled,         EMPTY),
    (list[str] | OptionalEnabled,   EMPTY),
]

MARKER_DISABLED = [
    (str | OptionalDisabled,            EMPTY),
    (str | OptionalDisabled,            None),
    (str | OptionalDisabled,            "hello"),
    (str | OptionalDisabled,            ""),
    (Priority | OptionalDisabled,       Priority.HIGH),
]

INVALID_TYPES = [
    (None,                  "cannot be only None"),
    (type(None),            "cannot be only None"),
    (str | int | None,      "more than 2 types"),
    (str | int | float,     "more than 2 types"),
]


def analyze_optional(annotation, default=EMPTY):
    validate_type(annotation)
    return extract_optional(annotation, default)


@pytest.mark.parametrize("annotation", NOT_OPTIONAL)
def test_not_optional(annotation):
    _, meta = analyze_optional(annotation)
    assert meta is None


@pytest.mark.parametrize("annotation", OPTIONAL_DISABLED_NO_DEFAULT)
def test_optional_no_default_is_disabled(annotation):
    _, meta = analyze_optional(annotation)
    assert meta == OptionalMetadata(enabled=False)


@pytest.mark.parametrize("annotation", OPTIONAL_DISABLED_DEFAULT_NONE)
def test_optional_default_none_is_disabled(annotation):
    _, meta = analyze_optional(annotation, None)
    assert meta == OptionalMetadata(enabled=False)


@pytest.mark.parametrize("annotation, default", OPTIONAL_ENABLED)
def test_optional_with_value_is_enabled(annotation, default):
    _, meta = analyze_optional(annotation, default)
    assert meta == OptionalMetadata(enabled=True)


@pytest.mark.parametrize("annotation, default", MARKER_ENABLED)
def test_optional_enabled_marker(annotation, default):
    _, meta = analyze_optional(annotation, default)
    assert meta == OptionalMetadata(enabled=True)


@pytest.mark.parametrize("annotation, default", MARKER_DISABLED)
def test_optional_disabled_marker(annotation, default):
    _, meta = analyze_optional(annotation, default)
    assert meta == OptionalMetadata(enabled=False)


@pytest.mark.parametrize("annotation, match", INVALID_TYPES)
def test_invalid_raises(annotation, match):
    with pytest.raises(TypeError, match=match):
        analyze_optional(annotation)

import pytest
from typing import Union, Annotated, Literal
from datetime import date, time
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.types import OptionalEnabled, OptionalDisabled


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


PRIMITIVES = [str, int, float, bool, date, time]

ANNOTATED_TYPES = [
    Annotated[str, Field(min_length=3)],
    Annotated[str, Field(min_length=3, max_length=20)],
    Annotated[Annotated[str, Field(min_length=3)], Field(max_length=20)],
]

LIST_TYPES = [
    list[str],
    list[int],
    list[Annotated[str, Field(min_length=3)]],
]

ENUM_AND_LITERAL = [
    Priority,
    Literal["a", "b", "c"],
    Literal[1, 2, 3],
]

OPTIONAL_TYPES = [
    str | None, int | None, float | None, bool | None, date | None, time | None,
    None | str, None | int,
    Union[str, None], Union[None, str],
    list[str] | None, list[int] | None,
    Annotated[str, Field(min_length=3)] | None,
    Priority | None, Literal["a", "b"] | None,
    str | OptionalEnabled, int | OptionalEnabled,
    str | OptionalDisabled, int | OptionalDisabled,
    list[str] | OptionalEnabled, Priority | OptionalDisabled,
]

ALL_VALID = PRIMITIVES + ANNOTATED_TYPES + LIST_TYPES + ENUM_AND_LITERAL + OPTIONAL_TYPES

NONE_ONLY = [None, type(None)]

UNION_THREE_PLUS = [
    (str | int | None, 3),
    (str | int | float | None, 4),
    (str | int | float | bool | None, 5),
    (Union[str, int, None], 3),
    (str | int | float, 3),
]

UNION_TWO_NO_NONE = [
    str | int,
    str | float,
    int | bool,
    list[str] | list[int],
    Annotated[str, Field(min_length=3)] | Annotated[int, Field(ge=0)],
    str | date,
    Union[str, int],
]


@pytest.mark.parametrize("annotation", ALL_VALID)
def test_valid_types(annotation):
    validate_type(annotation)


@pytest.mark.parametrize("annotation", NONE_ONLY)
def test_none_only_invalid(annotation):
    with pytest.raises(TypeError, match="cannot be only None"):
        validate_type(annotation)


@pytest.mark.parametrize("annotation, count", UNION_THREE_PLUS)
def test_union_three_plus_invalid(annotation, count):
    with pytest.raises(TypeError, match=f"more than 2 types, got {count}"):
        validate_type(annotation)


@pytest.mark.parametrize("annotation", UNION_TWO_NO_NONE)
def test_union_two_without_none_invalid(annotation):
    with pytest.raises(TypeError, match="must include None"):
        validate_type(annotation)

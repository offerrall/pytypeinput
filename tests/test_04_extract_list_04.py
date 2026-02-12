import inspect
import pytest
from typing import Any, Annotated, Literal
from datetime import date, time
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.extractors.validate_optional_02 import extract_optional
from pytypeinput.extractors.extract_param_ui_03 import extract_param_ui
from pytypeinput.extractors.extract_list_04 import extract_list
from pytypeinput.param import ListMetadata
from pytypeinput.types import (
    Label, Description, Slider, Step, Placeholder, PatternMessage,
    IsPassword, Rows, Dropdown,
    Color, Email, ImageFile, File,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


def get_colors():
    return ["red", "blue", "green"]


NOT_A_LIST = [
    str, int, float, bool, date, time,
    Annotated[str, Field(min_length=3)],
    Annotated[int, Field(ge=0)],
    Annotated[int, Field(ge=0), Slider()],
    Annotated[str, Placeholder("...")],
    Annotated[str, IsPassword()],
    Annotated[str, Rows(5)],
    Annotated[float, Step(0.5)],
    Annotated[str, Dropdown(get_colors)],
    Annotated[str, Field(pattern=r'^\d+$'), PatternMessage("err")],
    Color, Email, ImageFile, File,
    Priority,
    Literal["a", "b", "c"],
    Literal[1, 2, 3],
]


PLAIN_LISTS = [
    list[str],
    list[int],
    list[float],
    list[bool],
    list[date],
    list[time],
    list[Priority],
    list[Annotated[str, Field(min_length=3)]],
    list[Annotated[int, Field(ge=0)]],
    list[Annotated[int, Field(ge=0), Slider()]],
    list[Annotated[str, Placeholder("...")]],
    list[Annotated[float, Step(0.5)]],
    list[Color],
    list[Email],
    list[ImageFile],
    list[File],
]


CONSTRAINED_LISTS = [
    (Annotated[list[str], Field(min_length=1)], {"min_length": 1, "max_length": None}),
    (Annotated[list[int], Field(min_length=0)], {"min_length": 0, "max_length": None}),
    (Annotated[list[str], Field(max_length=10)], {"min_length": None, "max_length": 10}),
    (Annotated[list[int], Field(max_length=100)], {"min_length": None, "max_length": 100}),
    (Annotated[list[str], Field(min_length=1, max_length=10)], {"min_length": 1, "max_length": 10}),
    (Annotated[list[int], Field(min_length=0, max_length=100)], {"min_length": 0, "max_length": 100}),
    (Annotated[list[Annotated[str, Field(min_length=3)]], Field(min_length=1)], {"min_length": 1, "max_length": None}),
    (Annotated[list[Annotated[int, Field(ge=0), Slider()]], Field(max_length=5)], {"min_length": None, "max_length": 5}),
    (Annotated[list[Color], Field(min_length=1)], {"min_length": 1, "max_length": None}),
    (Annotated[list[Email], Field(min_length=1, max_length=10)], {"min_length": 1, "max_length": 10}),
]


NESTED_LISTS = [
    list[list[str]],
    list[list[int]],
    list[list[float]],
    Annotated[list[list[str]], Field(min_length=1)],
    Annotated[list[list[int]], Field(max_length=5)],
    list[Annotated[list[str], Field(min_length=1)]],
    list[Annotated[list[int], Field(max_length=5)]],
    list[list[list[str]]],
]


BAD_METADATA = [
    (Annotated[list[str], Slider()],                "Slider"),
    (Annotated[list[str], Placeholder("X")],        "Placeholder"),
    (Annotated[list[str], Step(1)],                 "Step"),
    (Annotated[list[str], IsPassword()],            "IsPassword"),
    (Annotated[list[str], Rows(5)],                 "Rows"),
    (Annotated[list[str], PatternMessage("err")],   "PatternMessage"),
    (Annotated[list[str], Dropdown(get_colors)],    "Dropdown"),
]


BAD_CONSTRAINTS = [
    Annotated[list[str], Field(ge=0)],
    Annotated[list[str], Field(le=100)],
    Annotated[list[str], Field(gt=0)],
    Annotated[list[str], Field(lt=10)],
    Annotated[list[str], Field(pattern=r'^\d+$')],
    Annotated[list[int], Field(ge=0, min_length=1)],
    Annotated[list[str], Field(pattern=r'^\d+$', max_length=10)],
]


def analyze_list(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    annotation, _ = extract_param_ui(annotation)
    return extract_list(annotation)


@pytest.mark.parametrize("annotation", NOT_A_LIST)
def test_not_a_list(annotation):
    _, meta = analyze_list(annotation)
    assert meta is None


@pytest.mark.parametrize("annotation", PLAIN_LISTS)
def test_plain_list(annotation):
    _, meta = analyze_list(annotation)
    assert meta is not None
    assert isinstance(meta, ListMetadata)
    assert meta.min_length is None
    assert meta.max_length is None


@pytest.mark.parametrize("annotation, expected", CONSTRAINED_LISTS)
def test_constrained_list_has_constraints(annotation, expected):
    _, meta = analyze_list(annotation)
    assert meta is not None
    assert isinstance(meta, ListMetadata)
    assert meta.min_length == expected["min_length"]
    assert meta.max_length == expected["max_length"]


@pytest.mark.parametrize("annotation", NESTED_LISTS)
def test_nested_list_raises(annotation):
    with pytest.raises(TypeError, match="Nested lists"):
        analyze_list(annotation)


@pytest.mark.parametrize("annotation, bad_type", BAD_METADATA)
def test_bad_metadata_raises(annotation, bad_type):
    with pytest.raises(TypeError, match=f"Invalid metadata on list: {bad_type}"):
        analyze_list(annotation)


@pytest.mark.parametrize("annotation", BAD_CONSTRAINTS)
def test_bad_field_constraints_raises(annotation):
    with pytest.raises(TypeError, match="Invalid list constraint"):
        analyze_list(annotation)
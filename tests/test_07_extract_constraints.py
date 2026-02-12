import inspect
import pytest
from typing import Annotated, Literal
from datetime import date, time
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.extractors.validate_optional_02 import extract_optional
from pytypeinput.extractors.extract_param_ui_03 import extract_param_ui
from pytypeinput.extractors.extract_list_04 import extract_list
from pytypeinput.extractors.extract_item_ui_05 import extract_item_ui
from pytypeinput.extractors.extract_choices_06 import extract_choices
from pytypeinput.extractors.extract_constraints_07 import extract_constraints
from pytypeinput.param import ConstraintsMetadata
from pytypeinput.types import (
    Slider, Step, Placeholder, Dropdown,
    Color, Email, ImageFile, File,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


def get_colors():
    return ["red", "blue", "green"]


NO_CONSTRAINTS = [
    str, int, float, bool, date, time,
    Priority,
    Literal["a", "b", "c"],
]


SINGLE_FIELD = [
    (Annotated[str, Field(min_length=3)], {"min_length": 3}),
    (Annotated[str, Field(min_length=0)], {"min_length": 0}),
    (Annotated[str, Field(max_length=20)], {"max_length": 20}),
    (Annotated[str, Field(max_length=100)], {"max_length": 100}),
    (Annotated[str, Field(min_length=3, max_length=20)], {"min_length": 3, "max_length": 20}),
    (Annotated[int, Field(ge=0)], {"ge": 0}),
    (Annotated[int, Field(ge=-10)], {"ge": -10}),
    (Annotated[float, Field(ge=0.0)], {"ge": 0.0}),
    (Annotated[int, Field(le=100)], {"le": 100}),
    (Annotated[float, Field(le=1.0)], {"le": 1.0}),
    (Annotated[int, Field(gt=0)], {"gt": 0}),
    (Annotated[float, Field(gt=0.0)], {"gt": 0.0}),
    (Annotated[int, Field(lt=100)], {"lt": 100}),
    (Annotated[float, Field(lt=1.0)], {"lt": 1.0}),
    (Annotated[int, Field(ge=0, le=100)], {"ge": 0, "le": 100}),
    (Annotated[float, Field(ge=0.0, le=1.0)], {"ge": 0.0, "le": 1.0}),
    (Annotated[int, Field(gt=0, lt=100)], {"gt": 0, "lt": 100}),
    (Annotated[str, Field(pattern=r'^\d+$')], {"pattern": r'^\d+$'}),
    (Annotated[str, Field(pattern=r'^[a-z]+$')], {"pattern": r'^[a-z]+$'}),
    (Annotated[str, Field(min_length=1, pattern=r'^\d+$')], {"min_length": 1, "pattern": r'^\d+$'}),
]


_Base_min3 = Annotated[str, Field(min_length=3)]
_Base_ge0 = Annotated[int, Field(ge=0)]
_Base_ge0_le100 = Annotated[int, Field(ge=0, le=100)]
_Base_min3_max20 = Annotated[str, Field(min_length=3, max_length=20)]
_Base_pattern = Annotated[str, Field(pattern=r'^\d+$')]


COMPOSITION = [
    (Annotated[_Base_min3, Field(max_length=20)], {"min_length": 3, "max_length": 20}),
    (Annotated[_Base_ge0, Field(le=100)], {"ge": 0, "le": 100}),
    (Annotated[_Base_min3, Field(pattern=r'^[a-z]+$')], {"min_length": 3, "pattern": r'^[a-z]+$'}),
    (Annotated[Annotated[Annotated[int, Field(ge=0)], Field(le=100)], Field(gt=-1)],
     {"ge": 0, "le": 100, "gt": -1}),
]


LAST_WINS = [
    (Annotated[_Base_min3, Field(min_length=5)], {"min_length": 5}),
    (Annotated[_Base_min3_max20, Field(max_length=50)], {"min_length": 3, "max_length": 50}),
    (Annotated[_Base_ge0, Field(ge=10)], {"ge": 10}),
    (Annotated[_Base_ge0_le100, Field(le=50)], {"ge": 0, "le": 50}),
    (Annotated[_Base_ge0_le100, Field(ge=10, le=50)], {"ge": 10, "le": 50}),
    (Annotated[_Base_pattern, Field(pattern=r'^[a-z]+$')], {"pattern": r'^[a-z]+$'}),
    (Annotated[_Base_min3_max20, Field(min_length=10)], {"min_length": 10, "max_length": 20}),
    (Annotated[Annotated[_Base_min3, Field(min_length=5)], Field(min_length=10)], {"min_length": 10}),
    (Annotated[Annotated[_Base_ge0, Field(ge=5)], Field(ge=10)], {"ge": 10}),
    (Annotated[_Base_ge0_le100, Field(le=50)], {"ge": 0, "le": 50}),
    (Annotated[_Base_min3, Field(min_length=5, max_length=20)], {"min_length": 5, "max_length": 20}),
]


SPECIAL_TYPES_CONSTRAINTS = [
    Color,
    ImageFile,
    File,
    Email,
]


SPECIAL_COMPOSITION = [
    (Annotated[Color, Field(min_length=7)], {"pattern", "min_length"}),
    (Annotated[Email, Field(min_length=5)], {"pattern", "min_length"}),
]


ALL_WITH_CONSTRAINTS = SINGLE_FIELD + COMPOSITION + LAST_WINS


def analyze_constraints(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    annotation, _ = extract_param_ui(annotation)
    annotation, _ = extract_list(annotation)
    annotation, _ = extract_item_ui(annotation)
    annotation, _ = extract_choices(annotation)
    return extract_constraints(annotation)


def constraints_to_dict(meta: ConstraintsMetadata) -> dict:
    result = {}
    for attr in ("ge", "le", "gt", "lt", "min_length", "max_length", "pattern"):
        value = getattr(meta, attr)
        if value is not None:
            result[attr] = value
    return result


@pytest.mark.parametrize("annotation", NO_CONSTRAINTS)
def test_no_constraints(annotation):
    _, meta = analyze_constraints(annotation)
    assert meta is None


@pytest.mark.parametrize("annotation, expected", ALL_WITH_CONSTRAINTS)
def test_has_constraints(annotation, expected):
    _, meta = analyze_constraints(annotation)
    assert meta is not None
    actual = constraints_to_dict(meta)
    assert actual == expected


@pytest.mark.parametrize("annotation", SPECIAL_TYPES_CONSTRAINTS)
def test_special_types_have_constraints(annotation):
    _, meta = analyze_constraints(annotation)
    assert meta is not None
    assert meta.pattern is not None


@pytest.mark.parametrize("annotation, expected_keys", SPECIAL_COMPOSITION)
def test_special_type_composition(annotation, expected_keys):
    _, meta = analyze_constraints(annotation)
    actual = set(constraints_to_dict(meta).keys())
    assert actual == expected_keys


def test_base_type_is_clean():
    ann, _ = analyze_constraints(Annotated[str, Field(min_length=3, max_length=20)])
    assert ann is str


def test_base_type_clean_after_composition():
    Base = Annotated[int, Field(ge=0)]
    Full = Annotated[Base, Field(le=100)]
    ann, _ = analyze_constraints(Full)
    assert ann is int


def test_base_type_clean_three_levels():
    L1 = Annotated[float, Field(ge=0.0)]
    L2 = Annotated[L1, Field(le=1.0)]
    L3 = Annotated[L2, Field(gt=0.0)]
    ann, _ = analyze_constraints(L3)
    assert ann is float

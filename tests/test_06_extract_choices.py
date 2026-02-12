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
from pytypeinput.param import ChoiceMetadata
from pytypeinput.types import (
    Slider, Step, Placeholder, Dropdown,
    Color, Email, ImageFile, File,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


class SingleValue(Enum):
    ONLY = "only"


def get_colors():
    return ["red", "blue", "green"]


def get_numbers():
    return [1, 2, 3]


def get_single():
    return ["only"]


def get_empty():
    return []


def get_mixed():
    return ["a", 1, True]


def get_not_list():
    return "not a list"


def get_explodes():
    raise RuntimeError("boom")


not_callable = "not a function"


NOT_A_CHOICE = [
    str, int, float, bool, date, time,
    Annotated[str, Field(min_length=3)],
    Annotated[int, Field(ge=0)],
    Annotated[str, Field(pattern=r'^\d+$')],
    Color, Email, ImageFile, File,
]


ENUM_CHOICES = [
    (Priority,      ChoiceMetadata(enum_class=Priority, options=("low", "high"))),
    (Status,        ChoiceMetadata(enum_class=Status, options=(1, 0))),
    (SingleValue,   ChoiceMetadata(enum_class=SingleValue, options=("only",))),
]


LITERAL_CHOICES = [
    (Literal["a", "b", "c"],    ChoiceMetadata(options=("a", "b", "c"))),
    (Literal[1, 2, 3],          ChoiceMetadata(options=(1, 2, 3))),
    (Literal["x"],              ChoiceMetadata(options=("x",))),
    (Literal[True, False],      ChoiceMetadata(options=(True, False))),
]


DROPDOWN_CHOICES = [
    (Annotated[str, Dropdown(get_colors)],
     ChoiceMetadata(options_function=get_colors, options=("red", "blue", "green"))),
    (Annotated[int, Dropdown(get_numbers)],
     ChoiceMetadata(options_function=get_numbers, options=(1, 2, 3))),
    (Annotated[str, Dropdown(get_single)],
     ChoiceMetadata(options_function=get_single, options=("only",))),
    (Annotated[str, Field(min_length=3), Dropdown(get_colors)],
     ChoiceMetadata(options_function=get_colors, options=("red", "blue", "green"))),
]


INVALID_DROPDOWNS = [
    (Annotated[str, Dropdown(not_callable)],     TypeError, "callable"),
    (Annotated[str, Dropdown(get_empty)],        ValueError, "empty"),
    (Annotated[str, Dropdown(get_not_list)],     TypeError, "list or tuple"),
    (Annotated[str, Dropdown(get_mixed)],        TypeError, "same type"),
    (Annotated[str, Dropdown(get_explodes)],     ValueError, "failed"),
]


DROPDOWN_LAST_WINS = [
    (Annotated[str, Dropdown(get_single), Dropdown(get_colors)],
     ChoiceMetadata(options_function=get_colors, options=("red", "blue", "green"))),
]


_Base_dropdown = Annotated[str, Dropdown(get_single)]


DROPDOWN_COMPOSITION = [
    (Annotated[_Base_dropdown, Dropdown(get_colors)],
     ChoiceMetadata(options_function=get_colors, options=("red", "blue", "green"))),
]


ALL_VALID_CHOICES = (
    ENUM_CHOICES
    + LITERAL_CHOICES
    + DROPDOWN_CHOICES
    + DROPDOWN_LAST_WINS
    + DROPDOWN_COMPOSITION
)


def analyze_choices(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    annotation, _ = extract_param_ui(annotation)
    annotation, _ = extract_list(annotation)
    annotation, _ = extract_item_ui(annotation)
    return extract_choices(annotation)


@pytest.mark.parametrize("annotation", NOT_A_CHOICE)
def test_not_a_choice(annotation):
    _, meta = analyze_choices(annotation)
    assert meta is None


@pytest.mark.parametrize("annotation, expected", ALL_VALID_CHOICES)
def test_extracts_choices(annotation, expected):
    _, meta = analyze_choices(annotation)
    assert meta == expected


@pytest.mark.parametrize("annotation, error_type, match", INVALID_DROPDOWNS)
def test_invalid_dropdown_raises(annotation, error_type, match):
    with pytest.raises(error_type, match=match):
        analyze_choices(annotation)

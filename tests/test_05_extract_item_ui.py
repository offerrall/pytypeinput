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
from pytypeinput.param import ItemUIMetadata
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


RETURNS_NONE = [
    str, int, float, bool, date, time,
    Annotated[str, Field(min_length=3)],
    Annotated[int, Field(ge=0)],
    Annotated[str, Field(min_length=3, max_length=20)],
    Annotated[str, Field(pattern=r'^\d+$')],
    Color, ImageFile, File,
    Priority,
    Literal["a", "b", "c"],
    Annotated[str, Dropdown(get_colors)],
    Annotated[str, Field(min_length=3), Dropdown(get_colors)],
]


SLIDER = [
    (Annotated[int, Field(ge=0, le=100), Slider()],
     ItemUIMetadata(is_slider=True)),
    (Annotated[float, Field(ge=0.0, le=1.0), Slider()],
     ItemUIMetadata(is_slider=True)),
    (Annotated[int, Field(ge=0), Slider(show_value=False)],
     ItemUIMetadata(is_slider=True, show_slider_value=False)),
    (Annotated[int, Slider()],
     ItemUIMetadata(is_slider=True)),
]


STEP = [
    (Annotated[int, Step(5)],
     ItemUIMetadata(step=5)),
    (Annotated[float, Step(0.1)],
     ItemUIMetadata(step=0.1)),
    (Annotated[float, Field(ge=0), Step(0.5)],
     ItemUIMetadata(step=0.5)),
    (Annotated[int, Field(ge=0, le=100), Slider(), Step(10)],
     ItemUIMetadata(is_slider=True, step=10)),
]


PLACEHOLDER = [
    (Annotated[str, Placeholder("Enter name...")],
     ItemUIMetadata(placeholder="Enter name...")),
    (Annotated[str, Field(min_length=3), Placeholder("...")],
     ItemUIMetadata(placeholder="...")),
]


PATTERN_MESSAGE = [
    (Annotated[str, Field(pattern=r'^\d+$'), PatternMessage("Numbers only")],
     ItemUIMetadata(pattern_message="Numbers only")),
    (Annotated[str, Field(pattern=r'^[a-z]+$'), PatternMessage("Lowercase")],
     ItemUIMetadata(pattern_message="Lowercase")),
]


IS_PASSWORD = [
    (Annotated[str, IsPassword()],
     ItemUIMetadata(is_password=True)),
    (Annotated[str, Field(min_length=8), IsPassword()],
     ItemUIMetadata(is_password=True)),
]


ROWS = [
    (Annotated[str, Rows(5)],
     ItemUIMetadata(rows=5)),
    (Annotated[str, Rows(10)],
     ItemUIMetadata(rows=10)),
    (Annotated[str, Field(max_length=500), Rows(3)],
     ItemUIMetadata(rows=3)),
]


COMBINATIONS = [
    (Annotated[int, Field(ge=0, le=100), Slider(), Step(5)],
     ItemUIMetadata(is_slider=True, step=5)),
    (Annotated[int, Field(ge=0), Slider(show_value=False), Step(10)],
     ItemUIMetadata(is_slider=True, show_slider_value=False, step=10)),
    (Annotated[str, Field(pattern=r'^\d+$'), Placeholder("123"), PatternMessage("Numbers")],
     ItemUIMetadata(placeholder="123", pattern_message="Numbers")),
    (Annotated[str, Field(min_length=8), IsPassword(), Placeholder("********")],
     ItemUIMetadata(is_password=True, placeholder="********")),
    (Annotated[str, Rows(5), Placeholder("Write here...")],
     ItemUIMetadata(rows=5, placeholder="Write here...")),
]


_Slider_base = Annotated[int, Field(ge=0, le=100), Slider()]
_Step_base = Annotated[int, Step(5)]
_Password_base = Annotated[str, IsPassword()]
_Rows_base = Annotated[str, Rows(5)]
_Placeholder_base = Annotated[str, Placeholder("...")]


COMPOSITION = [
    (Annotated[_Slider_base, Step(10)],
     ItemUIMetadata(is_slider=True, step=10)),
    (Annotated[_Password_base, Placeholder("********")],
     ItemUIMetadata(is_password=True, placeholder="********")),
    (Annotated[_Rows_base, Placeholder("Write...")],
     ItemUIMetadata(rows=5, placeholder="Write...")),
    (Annotated[Annotated[int, Field(ge=0)], Slider(), Step(5)],
     ItemUIMetadata(is_slider=True, step=5)),
    (Annotated[Annotated[Annotated[int, Field(ge=0)], Slider()], Step(2)],
     ItemUIMetadata(is_slider=True, step=2)),
]


LAST_WINS = [
    (Annotated[int, Slider(show_value=True), Slider(show_value=False)],
     ItemUIMetadata(is_slider=True, show_slider_value=False)),
    (Annotated[int, Step(5), Step(10)],
     ItemUIMetadata(step=10)),
    (Annotated[str, Placeholder("A"), Placeholder("B")],
     ItemUIMetadata(placeholder="B")),
    (Annotated[str, Field(pattern=r'^\d+$'), PatternMessage("A"), PatternMessage("B")],
     ItemUIMetadata(pattern_message="B")),
    (Annotated[str, Rows(3), Rows(10)],
     ItemUIMetadata(rows=10)),
    (Annotated[_Step_base, Step(10)],
     ItemUIMetadata(step=10)),
    (Annotated[_Placeholder_base, Placeholder("NEW")],
     ItemUIMetadata(placeholder="NEW")),
    (Annotated[_Rows_base, Rows(20)],
     ItemUIMetadata(rows=20)),
]


EMAIL_ITEM_UI = (
    Email,
    ItemUIMetadata(
        pattern_message="Must be a valid email address (e.g., name@example.com)",
        placeholder="name@example.com",
    ),
)


ALL_WITH_METADATA = (
    SLIDER
    + STEP
    + PLACEHOLDER
    + PATTERN_MESSAGE
    + IS_PASSWORD
    + ROWS
    + COMBINATIONS
    + COMPOSITION
    + LAST_WINS
)


def analyze_item_ui(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    annotation, _ = extract_param_ui(annotation)
    annotation, _ = extract_list(annotation)
    return extract_item_ui(annotation)


@pytest.mark.parametrize("annotation", RETURNS_NONE)
def test_returns_none(annotation):
    _, meta = analyze_item_ui(annotation)
    assert meta is None


@pytest.mark.parametrize("annotation, expected", ALL_WITH_METADATA)
def test_extracts_item_ui(annotation, expected):
    _, meta = analyze_item_ui(annotation)
    assert meta == expected


def test_email_has_item_ui():
    _, meta = analyze_item_ui(EMAIL_ITEM_UI[0])
    assert meta == EMAIL_ITEM_UI[1]

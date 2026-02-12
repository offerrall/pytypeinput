import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.extractors.validate_optional_02 import extract_optional
from pytypeinput.extractors.extract_param_ui_03 import extract_param_ui
from pytypeinput.extractors.extract_list_04 import extract_list
from pytypeinput.extractors.extract_item_ui_05 import extract_item_ui
from pytypeinput.extractors.extract_choices_06 import extract_choices
from pytypeinput.extractors.extract_constraints_07 import extract_constraints
from pytypeinput.extractors.resolve_widget_09 import resolve_widget_type
from pytypeinput.types import (
    Label, Description, Slider, Step, Placeholder, PatternMessage,
    IsPassword, Rows, Dropdown,
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File,
    OptionalEnabled,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


class Size(Enum):
    S = 1
    M = 2
    L = 3


def get_colors():
    return ["red", "blue", "green"]


def get_numbers():
    return [1, 2, 3]


def widget_for(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    annotation, _ = extract_param_ui(annotation)
    annotation, _ = extract_list(annotation)
    annotation, item_ui = extract_item_ui(annotation)
    annotation, choices = extract_choices(annotation)
    annotation, constraints = extract_constraints(annotation)
    return resolve_widget_type(annotation, constraints, choices, item_ui)


BASE_TYPES = [
    (str, "Text"),
    (int, "Number"),
    (float, "Number"),
    (bool, "Checkbox"),
    (date, "Date"),
    (time, "Time"),
]

DROPDOWN = [
    Priority,
    Size,
    Literal["a", "b", "c"],
    Literal[1, 2, 3],
    Literal[True, False],
    Annotated[str, Dropdown(get_colors)],
    Annotated[int, Dropdown(get_numbers)],
    Annotated[Priority, Label("P")],
    Annotated[Literal["x", "y"], Label("L")],
]

SLIDER = [
    Annotated[int, Slider()],
    Annotated[int, Field(ge=0, le=100), Slider()],
    Annotated[float, Field(ge=0.0, le=1.0), Slider()],
    Annotated[int, Slider(show_value=False)],
    Annotated[int, Slider(), Step(5)],
    Annotated[int, Field(ge=0, le=100), Slider(), Step(10)],
]

PASSWORD = [
    Annotated[str, IsPassword()],
    Annotated[str, Field(min_length=8), IsPassword()],
    Annotated[str, IsPassword(), Placeholder("********")],
]

TEXTAREA = [
    Annotated[str, Rows(5)],
    Annotated[str, Rows(10)],
    Annotated[str, Rows(3), Placeholder("Write...")],
    Annotated[str, Field(max_length=500), Rows(5)],
]

SPECIAL = [
    (Color, "Color"),
    (Email, "Email"),
    (ImageFile, "ImageFile"),
    (VideoFile, "VideoFile"),
    (AudioFile, "AudioFile"),
    (DataFile, "DataFile"),
    (TextFile, "TextFile"),
    (DocumentFile, "DocumentFile"),
    (File, "File"),
]

CONSTRAINTS_FALLBACK = [
    (Annotated[int, Field(ge=0)], "Number"),
    (Annotated[int, Field(ge=0, le=100)], "Number"),
    (Annotated[float, Field(gt=0, lt=1)], "Number"),
    (Annotated[str, Field(min_length=3)], "Text"),
    (Annotated[str, Field(min_length=1, max_length=50)], "Text"),
    (Annotated[str, Field(pattern=r"^\d{3}$")], "Text"),
]

OPTIONAL_SAME = [
    (str | None, "Text"),
    (int | None, "Number"),
    (float | None, "Number"),
    (bool | None, "Checkbox"),
    (date | None, "Date"),
    (time | None, "Time"),
    (Priority | None, "Dropdown"),
    (Literal["a", "b"] | None, "Dropdown"),
    (Color | None, "Color"),
    (Email | None, "Email"),
    (str | OptionalEnabled, "Text"),
]

LIST_INNER = [
    (list[str], "Text"),
    (list[int], "Number"),
    (list[float], "Number"),
    (list[bool], "Checkbox"),
    (list[date], "Date"),
    (list[time], "Time"),
    (list[Priority], "Dropdown"),
    (list[Color], "Color"),
    (list[Email], "Email"),
    (list[Annotated[int, Slider(), Step(5)]], "Slider"),
    (list[Annotated[str, IsPassword()]], "Password"),
    (list[Annotated[str, Rows(5)]], "Textarea"),
    (list[Annotated[str, Field(min_length=3)]], "Text"),
    (list[Annotated[int, Field(ge=0, le=100)]], "Number"),
    (Annotated[list[str], Field(min_length=1)], "Text"),
    (Annotated[list[int], Field(min_length=1, max_length=10)], "Number"),
    (Annotated[list[Annotated[int, Slider()]], Field(max_length=5)], "Slider"),
]

UI_NO_CHANGE = [
    (Annotated[int, Step(5)], "Number"),
    (Annotated[float, Step(0.1)], "Number"),
    (Annotated[str, Placeholder("...")], "Text"),
    (Annotated[str, Field(pattern=r"^\d+$"), PatternMessage("N")], "Text"),
]

LABEL_NO_CHANGE = [
    (Annotated[str, Label("Name")], "Text"),
    (Annotated[int, Label("Age"), Description("Years")], "Number"),
    (Annotated[str, Label("C"), Placeholder("..."), Dropdown(get_colors)], "Dropdown"),
]

COMBOS = [
    (Annotated[int, Label("Vol"), Field(ge=0, le=100), Slider(), Step(5)], "Slider"),
    (Annotated[str, Label("PW"), IsPassword(), Placeholder("***")], "Password"),
    (Annotated[str, Field(max_length=1000), Rows(10), Placeholder("...")], "Textarea"),
    (Annotated[Color, Label("Pick")], "Color"),
    (Annotated[Email, Label("Mail"), Description("Your email")], "Email"),
    (Annotated[ImageFile, Label("Upload")], "ImageFile"),
    (Annotated[str, Label("C"), Placeholder("..."), Dropdown(get_colors)], "Dropdown"),
    (Annotated[Priority, Label("Priority")], "Dropdown"),
]


@pytest.mark.parametrize("annotation, expected", BASE_TYPES)
def test_base_type(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation", DROPDOWN)
def test_dropdown(annotation):
    assert widget_for(annotation) == "Dropdown"


@pytest.mark.parametrize("annotation", SLIDER)
def test_slider(annotation):
    assert widget_for(annotation) == "Slider"


@pytest.mark.parametrize("annotation", PASSWORD)
def test_password(annotation):
    assert widget_for(annotation) == "Password"


@pytest.mark.parametrize("annotation", TEXTAREA)
def test_textarea(annotation):
    assert widget_for(annotation) == "Textarea"


@pytest.mark.parametrize("annotation, expected", SPECIAL)
def test_special_type(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", CONSTRAINTS_FALLBACK)
def test_constraints_fallback(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", OPTIONAL_SAME)
def test_optional_same_widget(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", LIST_INNER)
def test_list_resolves_inner_widget(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", UI_NO_CHANGE)
def test_ui_metadata_no_change(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", LABEL_NO_CHANGE)
def test_label_no_change(annotation, expected):
    assert widget_for(annotation) == expected


@pytest.mark.parametrize("annotation, expected", COMBOS)
def test_combos(annotation, expected):
    assert widget_for(annotation) == expected

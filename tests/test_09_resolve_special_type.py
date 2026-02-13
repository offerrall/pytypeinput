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
from pytypeinput.extractors.resolve_widget_09 import resolve_special_widget
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
    return resolve_special_widget(constraints)


# ===== Returns "Color" =====

COLOR = [
    Color,
    Annotated[Color, Label("Pick")],
    Color | None,
    list[Color],
]

# ===== Returns "File" =====

FILE = [
    ImageFile,
    VideoFile,
    AudioFile,
    DataFile,
    TextFile,
    DocumentFile,
    File,
    Annotated[ImageFile, Label("Upload")],
    list[File],
]

# ===== Returns None (everything else) =====

RETURNS_NONE = [
    # Base types
    str,
    int,
    float,
    bool,
    date,
    time,
    # Enum / Literal / Dropdown (detected by choices)
    Priority,
    Size,
    Literal["a", "b", "c"],
    Literal[1, 2, 3],
    Literal[True, False],
    Annotated[str, Dropdown(get_colors)],
    Annotated[int, Dropdown(get_numbers)],
    Annotated[Priority, Label("P")],
    Annotated[Literal["x", "y"], Label("L")],
    Annotated[str, Label("C"), Placeholder("..."), Dropdown(get_colors)],
    Annotated[Priority, Label("Priority")],
    # Slider (detected by item_ui)
    Annotated[int, Slider()],
    Annotated[int, Field(ge=0, le=100), Slider()],
    Annotated[float, Field(ge=0.0, le=1.0), Slider()],
    Annotated[int, Slider(show_value=False)],
    Annotated[int, Slider(), Step(5)],
    Annotated[int, Field(ge=0, le=100), Slider(), Step(10)],
    # Password (detected by item_ui)
    Annotated[str, IsPassword()],
    Annotated[str, Field(min_length=8), IsPassword()],
    Annotated[str, IsPassword(), Placeholder("********")],
    # Textarea (detected by item_ui)
    Annotated[str, Rows(5)],
    Annotated[str, Rows(10)],
    Annotated[str, Rows(3), Placeholder("Write...")],
    Annotated[str, Field(max_length=500), Rows(5)],
    # Email (just a str with pattern)
    Email,
    Annotated[Email, Label("Mail"), Description("Your email")],
    Email | None,
    list[Email],
    # Constraints
    Annotated[int, Field(ge=0)],
    Annotated[int, Field(ge=0, le=100)],
    Annotated[float, Field(gt=0, lt=1)],
    Annotated[str, Field(min_length=3)],
    Annotated[str, Field(min_length=1, max_length=50)],
    Annotated[str, Field(pattern=r"^\d{3}$")],
    # UI metadata
    Annotated[int, Step(5)],
    Annotated[float, Step(0.1)],
    Annotated[str, Placeholder("...")],
    Annotated[str, Field(pattern=r"^\d+$"), PatternMessage("N")],
    # Labels
    Annotated[str, Label("Name")],
    Annotated[int, Label("Age"), Description("Years")],
    # Optional
    str | None,
    int | None,
    float | None,
    bool | None,
    date | None,
    time | None,
    Priority | None,
    Literal["a", "b"] | None,
    str | OptionalEnabled,
    # Lists
    list[str],
    list[int],
    list[float],
    list[bool],
    list[date],
    list[time],
    list[Priority],
    list[Annotated[int, Slider(), Step(5)]],
    list[Annotated[str, IsPassword()]],
    list[Annotated[str, Rows(5)]],
    list[Annotated[str, Field(min_length=3)]],
    list[Annotated[int, Field(ge=0, le=100)]],
    Annotated[list[str], Field(min_length=1)],
    Annotated[list[int], Field(min_length=1, max_length=10)],
    Annotated[list[Annotated[int, Slider()]], Field(max_length=5)],
    # Combos
    Annotated[int, Label("Vol"), Field(ge=0, le=100), Slider(), Step(5)],
    Annotated[str, Label("PW"), IsPassword(), Placeholder("***")],
    Annotated[str, Field(max_length=1000), Rows(10), Placeholder("...")],
]


@pytest.mark.parametrize("annotation", COLOR)
def test_color(annotation):
    assert widget_for(annotation) == "Color"


@pytest.mark.parametrize("annotation", FILE)
def test_file(annotation):
    assert widget_for(annotation) == "File"


@pytest.mark.parametrize("annotation", RETURNS_NONE)
def test_returns_none(annotation):
    assert widget_for(annotation) is None
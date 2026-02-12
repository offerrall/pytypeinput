import inspect
import pytest
from typing import Annotated, Literal, Union
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
from pytypeinput.extractors.validate_final_08 import validate_final
from pytypeinput.types import (
    Label, Description, Slider, Step, Placeholder, PatternMessage,
    IsPassword, Rows, Dropdown,
    Color, Email, ImageFile, File,
    OptionalEnabled, OptionalDisabled,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


def get_colors():
    return ["red", "blue", "green"]


def get_numbers():
    return [1, 2, 3]


VALID_NO_DEFAULT = [
    str, int, float, bool, date, time,
    Annotated[str, Field(min_length=3)],
    Annotated[int, Field(ge=0, le=100)],
    Annotated[float, Field(ge=0.0, le=1.0)],
    Annotated[str, Placeholder("..."), Field(min_length=3)],
    Annotated[int, Field(ge=0), Slider()],
    Annotated[str, IsPassword(), Field(min_length=8)],
    Annotated[str, Rows(5)],
    Annotated[str, Label("Name"), Field(min_length=3)],
    Annotated[int, Label("Age"), Description("Your age"), Field(ge=0)],
    Color, Email, ImageFile, File,
    Priority, Status,
    Literal["a", "b", "c"],
    Literal[1, 2, 3],
    Annotated[str, Dropdown(get_colors)],
    Annotated[int, Dropdown(get_numbers)],
    str | None,
    int | None,
    Annotated[str, Field(min_length=3)] | None,
    str | OptionalEnabled,
    str | OptionalDisabled,
    list[str],
    list[int],
    list[Annotated[str, Field(min_length=3)]],
    Annotated[list[str], Field(min_length=1)],
]


VALID_WITH_DEFAULT = [
    (str, "hello"),
    (str, ""),
    (Annotated[str, Field(min_length=3)], "hello"),
    (Annotated[str, Field(max_length=5)], "hi"),
    (Annotated[str, Field(min_length=1, max_length=10)], "test"),
    (Annotated[str, Field(pattern=r'^\d+$')], "123"),
    (int, 42),
    (int, 0),
    (int, -10),
    (Annotated[int, Field(ge=0)], 0),
    (Annotated[int, Field(ge=0)], 100),
    (Annotated[int, Field(ge=0, le=100)], 50),
    (Annotated[int, Field(gt=0)], 1),
    (Annotated[int, Field(lt=100)], 99),
    (float, 3.14),
    (float, 0.0),
    (float, -2.5),
    (Annotated[float, Field(ge=0.0)], 0.0),
    (Annotated[float, Field(ge=0.0, le=1.0)], 0.5),
    (bool, True),
    (bool, False),
    (date, date.today()),
    (date, date.min),
    (date, date(2024, 1, 1)),
    (time, time(14, 30)),
    (time, time(0, 0)),
    (Priority, Priority.LOW),
    (Priority, Priority.HIGH),
    (Status, Status.ACTIVE),
    (Status, Status.INACTIVE),
    (Priority, "low"),
    (Priority, "high"),
    (Status, 1),
    (Status, 0),
    (Literal["a", "b", "c"], "a"),
    (Literal["a", "b", "c"], "c"),
    (Literal[1, 2, 3], 1),
    (Literal[1, 2, 3], 3),
    (Annotated[str, Dropdown(get_colors)], "red"),
    (Annotated[str, Dropdown(get_colors)], "blue"),
    (Annotated[str, Dropdown(get_colors)], "green"),
    (Annotated[int, Dropdown(get_numbers)], 1),
    (Annotated[int, Dropdown(get_numbers)], 2),
    (Annotated[int, Dropdown(get_numbers)], 3),
    (str | None, "hello"),
    (int | None, 42),
    (Annotated[str, Field(min_length=3)] | None, "hello"),
    (str | None, None),
    (int | None, None),
]


INVALID_BASE_TYPE = [
    (list, "Empty list type is not supported"),
    (dict, "Unsupported type"),
    (set, "Unsupported type"),
    (tuple, "Unsupported type"),
    (bytes, "Unsupported type"),
    (complex, "Unsupported type"),
    (object, "Unsupported type"),
    (list[dict], "Unsupported type"),
    (list[set], "Unsupported type"),
    (list[tuple], "Unsupported type"),
    (list[bytes], "Unsupported type"),
    (list[complex], "Unsupported type"),
    (list[object], "Unsupported type"),
    (Annotated[list[dict], Field(min_length=1)], "Unsupported type"),
    (Annotated[list[bytes], Field(max_length=10)], "Unsupported type"),
    (Annotated[int, Dropdown(get_colors)], "Dropdown options are str but type is int"),
    (Annotated[str, Dropdown(get_numbers)], "Dropdown options are int but type is str"),
    (Annotated[float, Dropdown(get_colors)], "Dropdown options are str but type is float"),
    (Annotated[bool, Dropdown(get_numbers)], "Dropdown options are int but type is bool"),
]


INVALID_DEFAULT_TYPE = [
    (str, 42, "not a valid str"),
    (str, True, "not a valid str"),
    (str, 3.14, "not a valid str"),
    (int, "hello", "not a valid int"),
    (int, 3.14, "not a valid int"),
    (float, "hello", "not a valid float"),
    (bool, "yes", "not a valid bool"),
    (bool, 1, "not a valid bool"),
    (bool, 0, "not a valid bool"),
    (date, "2024-01-01", "not a valid date"),
    (date, 42, "not a valid date"),
    (time, "14:30", "not a valid time"),
    (time, 42, "not a valid time"),

]


INVALID_DEFAULT_CHOICES = [
    (Priority, "missing", "not in options"),
    (Priority, "LOW", "not in options"),
    (Priority, "medium", "not in options"),
    (Status, 999, "not in options"),
    (Status, -1, "not in options"),
    (Status, 2, "not in options"),
    (Priority, 123, "not a valid str"),
    (Priority, True, "not a valid str"),
    (Status, "active", "not a valid int"),
    (Status, 1.5, "not a valid int"),
    (Literal["a", "b", "c"], "d", "not in options"),
    (Literal["a", "b", "c"], "A", "not in options"),
    (Literal[1, 2, 3], 4, "not in options"),
    (Literal[1, 2, 3], 0, "not in options"),
    (Annotated[str, Dropdown(get_colors)], "purple", "not in options"),
    (Annotated[str, Dropdown(get_colors)], "RED", "not in options"),
    (Annotated[int, Dropdown(get_numbers)], 0, "not in options"),
    (Annotated[int, Dropdown(get_numbers)], 4, "not in options"),
    (Annotated[int, Dropdown(get_numbers)], 999, "not in options"),
]


INVALID_DEFAULT_CONSTRAINTS = [
    (Annotated[str, Field(min_length=3)], "ab", "violates constraints"),
    (Annotated[str, Field(min_length=3)], "", "violates constraints"),
    (Annotated[str, Field(min_length=1)], "", "violates constraints"),
    (Annotated[str, Field(max_length=5)], "toolong", "violates constraints"),
    (Annotated[str, Field(max_length=3)], "abcd", "violates constraints"),
    (Annotated[str, Field(min_length=3, max_length=5)], "ab", "violates constraints"),
    (Annotated[str, Field(min_length=3, max_length=5)], "toolong", "violates constraints"),
    (Annotated[int, Field(ge=0)], -1, "violates constraints"),
    (Annotated[int, Field(ge=10)], 9, "violates constraints"),
    (Annotated[float, Field(ge=0.0)], -0.1, "violates constraints"),
    (Annotated[int, Field(le=100)], 101, "violates constraints"),
    (Annotated[float, Field(le=1.0)], 1.1, "violates constraints"),
    (Annotated[int, Field(ge=0, le=100)], -1, "violates constraints"),
    (Annotated[int, Field(ge=0, le=100)], 101, "violates constraints"),
    (Annotated[int, Field(gt=0)], 0, "violates constraints"),
    (Annotated[int, Field(gt=0)], -1, "violates constraints"),
    (Annotated[int, Field(lt=100)], 100, "violates constraints"),
    (Annotated[int, Field(lt=100)], 101, "violates constraints"),
    (Annotated[str, Field(pattern=r'^\d+$')], "abc", "violates constraints"),
    (Annotated[str, Field(pattern=r'^\d+$')], "", "violates constraints"),
    (Annotated[str, Field(pattern=r'^[a-z]+$')], "ABC", "violates constraints"),

]


BOOL_INT_EDGE = [
    (bool, 1, "not a valid bool"),
    (bool, 0, "not a valid bool"),
    (int, True, "not a valid int"),
    (int, False, "not a valid int"),
]


def full_analyze(annotation, default=EMPTY):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, default)
    annotation, _ = extract_param_ui(annotation)
    annotation, list_meta = extract_list(annotation)
    annotation, _ = extract_item_ui(annotation)
    annotation, choices = extract_choices(annotation)
    annotation, constraints = extract_constraints(annotation)
    validate_final(annotation, default, choices, constraints, list_meta)
    return annotation


@pytest.mark.parametrize("annotation", VALID_NO_DEFAULT)
def test_valid_no_default(annotation):
    full_analyze(annotation)


@pytest.mark.parametrize("annotation, default", VALID_WITH_DEFAULT)
def test_valid_with_default(annotation, default):
    full_analyze(annotation, default)


@pytest.mark.parametrize("annotation, match", INVALID_BASE_TYPE)
def test_invalid_base_type(annotation, match):
    with pytest.raises(TypeError, match=match):
        full_analyze(annotation)


@pytest.mark.parametrize("annotation, default, match", INVALID_DEFAULT_TYPE)
def test_invalid_default_type(annotation, default, match):
    with pytest.raises(TypeError, match=match):
        full_analyze(annotation, default)


@pytest.mark.parametrize("annotation, default, match", INVALID_DEFAULT_CHOICES)
def test_invalid_default_choices(annotation, default, match):
    with pytest.raises((TypeError, ValueError), match=match):
        full_analyze(annotation, default)


@pytest.mark.parametrize("annotation, default, match", INVALID_DEFAULT_CONSTRAINTS)
def test_invalid_default_constraints(annotation, default, match):
    with pytest.raises(ValueError, match=match):
        full_analyze(annotation, default)


@pytest.mark.parametrize("annotation, default, match", BOOL_INT_EDGE)
def test_bool_int_edge_cases(annotation, default, match):
    with pytest.raises(TypeError, match=match):
        full_analyze(annotation, default)
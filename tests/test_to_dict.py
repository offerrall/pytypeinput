import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.types import (
    Label, Description, Step, Placeholder, Rows,
    Slider, IsPassword, Dropdown,
    Color, Email,
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


def colors():
    return ["red", "green", "blue"]


def test_basic_int():
    d = analyze_type(int, "age").to_dict()
    assert d["name"] == "age"
    assert d["param_type"] == "int"
    assert "default" not in d
    assert d["widget_type"] == "Number"
    assert "choices" not in d
    assert "constraints" not in d
    assert "optional" not in d
    assert "list" not in d
    assert "item_ui" not in d
    assert "param_ui" not in d


def test_basic_str():
    d = analyze_type(str, "name").to_dict()
    assert d["param_type"] == "str"
    assert d["widget_type"] == "Text"


def test_basic_bool():
    d = analyze_type(bool, "flag").to_dict()
    assert d["param_type"] == "bool"
    assert d["widget_type"] == "Checkbox"


def test_basic_float():
    d = analyze_type(float, "val").to_dict()
    assert d["param_type"] == "float"
    assert d["widget_type"] == "Number"


def test_basic_date():
    d = analyze_type(date, "d").to_dict()
    assert d["param_type"] == "date"
    assert d["widget_type"] == "Date"


def test_basic_time():
    d = analyze_type(time, "t").to_dict()
    assert d["param_type"] == "time"
    assert d["widget_type"] == "Time"


def test_default_int():
    d = analyze_type(int, "n", 42).to_dict()
    assert d["default"] == 42


def test_default_str():
    d = analyze_type(str, "s", "hello").to_dict()
    assert d["default"] == "hello"


def test_default_bool():
    d = analyze_type(bool, "b", True).to_dict()
    assert d["default"] is True


def test_default_date():
    d = analyze_type(date, "d", date(2024, 1, 1)).to_dict()
    assert d["default"] == "2024-01-01"


def test_default_time():
    d = analyze_type(time, "t", time(14, 30)).to_dict()
    assert d["default"] == "14:30:00"


def test_default_none():
    d = analyze_type(str, "s", None).to_dict()
    assert "default" not in d


def test_enum_no_default():
    d = analyze_type(Priority, "p").to_dict()
    assert d["param_type"] == "str"
    assert d["widget_type"] == "Dropdown"
    assert d["choices"]["enum_class"] == "Priority"
    assert d["choices"]["options"] == ["low", "high"]
    assert "options_function" not in d["choices"]


def test_enum_with_instance_default():
    d = analyze_type(Priority, "p", Priority.LOW).to_dict()
    assert d["default"] == "low"
    assert d["choices"]["enum_class"] == "Priority"


def test_enum_with_raw_default():
    d = analyze_type(Priority, "p", "high").to_dict()
    assert d["default"] == "high"


def test_enum_int_values():
    d = analyze_type(Size, "s", Size.M).to_dict()
    assert d["param_type"] == "int"
    assert d["default"] == 2
    assert d["choices"]["options"] == [1, 2, 3]
    assert d["choices"]["enum_class"] == "Size"


def test_literal_str():
    d = analyze_type(Literal["a", "b", "c"], "x").to_dict()
    assert d["widget_type"] == "Dropdown"
    assert d["choices"]["options"] == ["a", "b", "c"]
    assert "enum_class" not in d["choices"]


def test_literal_int():
    d = analyze_type(Literal[1, 2, 3], "x").to_dict()
    assert d["choices"]["options"] == [1, 2, 3]


def test_literal_with_default():
    d = analyze_type(Literal["a", "b"], "x", "a").to_dict()
    assert d["default"] == "a"


def test_dropdown():
    d = analyze_type(Annotated[str, Dropdown(colors)], "c").to_dict()
    assert d["widget_type"] == "Dropdown"
    assert d["choices"]["options"] == ["red", "green", "blue"]
    assert "enum_class" not in d["choices"]
    assert "options_function" not in d["choices"]


def test_constraints_int():
    d = analyze_type(Annotated[int, Field(ge=0, le=100)], "n").to_dict()
    assert d["constraints"]["ge"] == 0
    assert d["constraints"]["le"] == 100


def test_constraints_str():
    d = analyze_type(Annotated[str, Field(min_length=3, max_length=20)], "s").to_dict()
    assert d["constraints"]["min_length"] == 3
    assert d["constraints"]["max_length"] == 20


def test_constraints_pattern():
    d = analyze_type(Annotated[str, Field(pattern=r"^\d+$")], "s").to_dict()
    assert d["constraints"]["pattern"] == r"^\d+$"


def test_optional_no_default():
    d = analyze_type(str | None, "s").to_dict()
    assert d["optional"]["enabled"] is False


def test_optional_with_default():
    d = analyze_type(str | None, "s", "hi").to_dict()
    assert d["optional"]["enabled"] is True


def test_optional_enabled_marker():
    d = analyze_type(str | OptionalEnabled, "s").to_dict()
    assert d["optional"]["enabled"] is True


def test_list_plain():
    d = analyze_type(list[int], "nums").to_dict()
    assert d["param_type"] == "int"
    assert "list" in d


def test_list_constrained():
    d = analyze_type(Annotated[list[str], Field(min_length=1, max_length=10)], "tags").to_dict()
    assert d["list"]["min_length"] == 1
    assert d["list"]["max_length"] == 10


def test_slider():
    d = analyze_type(Annotated[int, Field(ge=0, le=100), Slider(), Step(5)], "v").to_dict()
    assert d["widget_type"] == "Slider"
    assert d["item_ui"]["is_slider"] is True
    assert d["item_ui"]["step"] == 5


def test_password():
    d = analyze_type(Annotated[str, IsPassword()], "pw").to_dict()
    assert d["widget_type"] == "Password"
    assert d["item_ui"]["is_password"] is True


def test_textarea():
    d = analyze_type(Annotated[str, Rows(5)], "bio").to_dict()
    assert d["widget_type"] == "Textarea"
    assert d["item_ui"]["rows"] == 5


def test_placeholder():
    d = analyze_type(Annotated[str, Placeholder("...")], "s").to_dict()
    assert d["item_ui"]["placeholder"] == "..."


def test_label_and_description():
    d = analyze_type(Annotated[int, Label("Age"), Description("Your age")], "a").to_dict()
    assert d["param_ui"]["label"] == "Age"
    assert d["param_ui"]["description"] == "Your age"


def test_special_color():
    d = analyze_type(Color, "c").to_dict()
    assert d["widget_type"] == "Color"


def test_special_email():
    d = analyze_type(Email, "e").to_dict()
    assert d["widget_type"] == "Email"


def test_full_combo():
    ann = Annotated[int, Label("Vol"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)]
    d = analyze_type(ann | None, "v", 50).to_dict()
    assert d["name"] == "v"
    assert d["param_type"] == "int"
    assert d["default"] == 50
    assert d["widget_type"] == "Slider"
    assert d["optional"]["enabled"] is True
    assert d["constraints"]["ge"] == 0
    assert d["constraints"]["le"] == 100
    assert d["item_ui"]["is_slider"] is True
    assert d["item_ui"]["step"] == 5
    assert d["param_ui"]["label"] == "Vol"
    assert d["param_ui"]["description"] == "D"


def test_list_enum_default():
    d = analyze_type(list[Priority], "p", [Priority.LOW, Priority.HIGH]).to_dict()
    assert d["default"] == ["low", "high"]
    assert d["choices"]["enum_class"] == "Priority"


def test_options_function_not_in_dict():
    d = analyze_type(Annotated[str, Dropdown(colors)], "c").to_dict()
    assert "options_function" not in d["choices"]


def test_enum_class_none_for_literal():
    d = analyze_type(Literal["a", "b"], "x").to_dict()
    assert "enum_class" not in d["choices"]
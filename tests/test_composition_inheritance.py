import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.param import ParamMetadata
from pytypeinput.types import (
    Label, Description, Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword, Dropdown,
    OptionalEnabled, OptionalDisabled,
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Size(Enum):
    S = 1
    M = 2
    L = 3


def colors():
    return ["red", "green", "blue"]


def sizes():
    return [1, 2, 3]


PositiveInt = Annotated[int, Field(ge=0)]
BoundedInt = Annotated[int, Field(ge=0, le=100)]
SmallStr = Annotated[str, Field(min_length=1, max_length=50)]
LongStr = Annotated[str, Field(min_length=1, max_length=5000)]
PatternDigits = Annotated[str, Field(pattern=r"^\d+$")]
PositiveFloat = Annotated[float, Field(ge=0.0)]
UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]

SliderInt = Annotated[BoundedInt, Slider()]
SliderStep5 = Annotated[BoundedInt, Slider(), Step(5)]
SliderNoValue = Annotated[BoundedInt, Slider(show_value=False)]
PasswordStr = Annotated[SmallStr, IsPassword()]
TextAreaStr = Annotated[LongStr, Rows(10)]
PlaceholderStr = Annotated[SmallStr, Placeholder("Type here...")]
StepFloat = Annotated[UnitFloat, Step(0.01)]

LabeledInt = Annotated[int, Label("Count")]
LabeledStr = Annotated[str, Label("Name")]
DescribedInt = Annotated[int, Description("A number")]
FullLabelInt = Annotated[int, Label("Age"), Description("Your age")]

LabeledSlider = Annotated[SliderInt, Label("Volume")]
LabeledPassword = Annotated[PasswordStr, Label("Secret")]
LabeledTextArea = Annotated[TextAreaStr, Label("Bio")]
DescribedSlider = Annotated[SliderStep5, Description("Adjust value")]
FullSlider = Annotated[SliderStep5, Label("Level"), Description("Set level")]
FullPassword = Annotated[
    PasswordStr,
    Label("Password"),
    Description("Enter password"),
    Placeholder("********"),
]
FullTextArea = Annotated[
    TextAreaStr,
    Label("Notes"),
    Description("Add notes"),
    Placeholder("Write..."),
]


class TestFieldComposition:
    def test_single_field(self):
        r = analyze_type(Annotated[int, Field(ge=0)], "f")
        assert r.constraints.ge == 0

    def test_two_fields_merge(self):
        r = analyze_type(Annotated[PositiveInt, Field(le=100)], "f")
        assert r.constraints.ge == 0
        assert r.constraints.le == 100

    def test_three_levels_merge(self):
        L1 = Annotated[int, Field(ge=0)]
        L2 = Annotated[L1, Field(le=100)]
        L3 = Annotated[L2, Field(gt=-1)]
        r = analyze_type(L3, "f")
        assert r.constraints.ge == 0
        assert r.constraints.le == 100
        assert r.constraints.gt == -1

    def test_four_levels_merge(self):
        L1 = Annotated[int, Field(ge=0)]
        L2 = Annotated[L1, Field(le=100)]
        L3 = Annotated[L2, Field(gt=-1)]
        L4 = Annotated[L3, Field(lt=101)]
        r = analyze_type(L4, "f")
        assert r.constraints.ge == 0
        assert r.constraints.le == 100
        assert r.constraints.gt == -1
        assert r.constraints.lt == 101

    def test_str_min_then_max(self):
        r = analyze_type(
            Annotated[SmallStr, Field(pattern=r"^[a-z]+$")], "f"
        )
        assert r.constraints.min_length == 1
        assert r.constraints.max_length == 50
        assert r.constraints.pattern == r"^[a-z]+$"

    def test_override_ge(self):
        r = analyze_type(Annotated[PositiveInt, Field(ge=10)], "f")
        assert r.constraints.ge == 10

    def test_override_le(self):
        r = analyze_type(Annotated[BoundedInt, Field(le=50)], "f")
        assert r.constraints.ge == 0
        assert r.constraints.le == 50

    def test_override_both(self):
        r = analyze_type(
            Annotated[BoundedInt, Field(ge=10, le=50)], "f"
        )
        assert r.constraints.ge == 10
        assert r.constraints.le == 50

    def test_override_min_length(self):
        r = analyze_type(Annotated[SmallStr, Field(min_length=5)], "f")
        assert r.constraints.min_length == 5
        assert r.constraints.max_length == 50

    def test_override_max_length(self):
        r = analyze_type(Annotated[SmallStr, Field(max_length=10)], "f")
        assert r.constraints.min_length == 1
        assert r.constraints.max_length == 10

    def test_override_pattern(self):
        Base = Annotated[str, Field(pattern=r"^\d+$")]
        r = analyze_type(
            Annotated[Base, Field(pattern=r"^[a-z]+$")], "f"
        )
        assert r.constraints.pattern == r"^[a-z]+$"

    def test_deep_override_chain(self):
        L1 = Annotated[int, Field(ge=0)]
        L2 = Annotated[L1, Field(ge=5)]
        L3 = Annotated[L2, Field(ge=10)]
        r = analyze_type(L3, "f")
        assert r.constraints.ge == 10

    def test_base_type_survives_composition(self):
        r = analyze_type(Annotated[PositiveInt, Field(le=100)], "f")
        assert r.param_type is int

    def test_base_type_survives_deep(self):
        L1 = Annotated[float, Field(ge=0.0)]
        L2 = Annotated[L1, Field(le=1.0)]
        L3 = Annotated[L2, Field(gt=0.0)]
        r = analyze_type(L3, "f")
        assert r.param_type is float


class TestFieldCompositionWithDefaults:
    def test_composed_valid_default(self):
        r = analyze_type(Annotated[PositiveInt, Field(le=100)], "f", 50)
        assert r.default == 50

    def test_composed_boundary_default(self):
        r = analyze_type(Annotated[PositiveInt, Field(le=100)], "f", 0)
        assert r.default == 0

    def test_composed_max_boundary(self):
        r = analyze_type(Annotated[PositiveInt, Field(le=100)], "f", 100)
        assert r.default == 100

    def test_composed_invalid_default_below(self):
        with pytest.raises(ValueError):
            analyze_type(Annotated[PositiveInt, Field(le=100)], "f", -1)

    def test_composed_invalid_default_above(self):
        with pytest.raises(ValueError):
            analyze_type(Annotated[PositiveInt, Field(le=100)], "f", 101)

    def test_override_makes_default_invalid(self):
        with pytest.raises(ValueError):
            analyze_type(Annotated[PositiveInt, Field(ge=10)], "f", 5)

    def test_override_makes_default_valid(self):
        r = analyze_type(
            Annotated[BoundedInt, Field(le=200)], "f", 150
        )
        assert r.default == 150

    def test_str_composed_valid(self):
        r = analyze_type(
            Annotated[SmallStr, Field(pattern=r"^[a-z]+$")],
            "f",
            "hello",
        )
        assert r.default == "hello"

    def test_str_composed_invalid_pattern(self):
        with pytest.raises(ValueError):
            analyze_type(
                Annotated[SmallStr, Field(pattern=r"^[a-z]+$")],
                "f",
                "HELLO",
            )

    def test_str_composed_invalid_length(self):
        with pytest.raises(ValueError):
            analyze_type(SmallStr, "f", "")

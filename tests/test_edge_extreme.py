import inspect
import pytest
from typing import Annotated, Literal, Union
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.param import ParamMetadata, ChoiceMetadata, OptionalMetadata
from pytypeinput.types import (
    Label, Description, Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword, Dropdown,
    OptionalEnabled, OptionalDisabled,
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File,
)

EMPTY = inspect.Parameter.empty


class SingleEnum(Enum):
    ONLY = "only"

class BoolEnum(Enum):
    YES = True
    NO = False

class NegativeEnum(Enum):
    NEG = -1
    ZERO = 0
    POS = 1

class FloatEnum(Enum):
    LOW = 0.1
    HIGH = 0.9

class DuplicateEnum(Enum):
    A = 1
    B = 1


def single_option():
    return ["only"]

def returns_tuple():
    return (1, 2, 3)

def bool_options():
    return [True, False]

def negative_options():
    return [-10, -5, 0, 5, 10]

def float_options():
    return [0.1, 0.5, 0.9]

def unicode_options():
    return ["café", "naïve", "日本語"]

def long_options():
    return list(range(100))

def colors():
    return ["red", "green", "blue"]


VALID = [
    (Annotated[Annotated[Annotated[Annotated[int, Field(ge=0, le=100)], Slider()], Step(5)], Label("Deep")], "f", EMPTY),
    (Annotated[Annotated[Annotated[int, Field(ge=0)], Field(le=100)], Field(gt=-1)], "f", EMPTY),
    (Annotated[Annotated[Annotated[str, Label("L1")], Label("L2")], Label("L3")], "f", EMPTY),

    (Annotated[str, Label("X"), Field(min_length=3)] | None, "f", EMPTY),
    (Annotated[str, Label("X"), Field(min_length=3)] | None, "f", None),
    (Annotated[str, Label("X"), Field(min_length=3)] | None, "f", "abc"),
    (Annotated[int, Field(ge=0, le=100), Slider()] | None, "f", 50),
    (Annotated[int, Field(ge=0, le=100), Slider()] | None, "f", None),

    (Annotated[str, Field(min_length=1)] | OptionalEnabled, "f", EMPTY),
    (Annotated[int, Slider(), Field(ge=0, le=100)] | OptionalDisabled, "f", 50),

    (list[str] | OptionalEnabled, "f", EMPTY),
    (list[str] | OptionalEnabled, "f", None),
    (list[str] | OptionalEnabled, "f", []),
    (list[str] | OptionalDisabled, "f", EMPTY),
    (list[int] | OptionalDisabled, "f", [1, 2, 3]),

    (Union[str, None], "f", EMPTY),
    (Union[str, None], "f", "hi"),
    (Union[int, None], "f", 0),
    (None | str, "f", EMPTY),
    (None | int, "f", 42),

    (SingleEnum, "f", EMPTY),
    (SingleEnum, "f", SingleEnum.ONLY),

    (BoolEnum, "f", EMPTY),
    (BoolEnum, "f", BoolEnum.YES),
    (BoolEnum, "f", BoolEnum.NO),

    (NegativeEnum, "f", EMPTY),
    (NegativeEnum, "f", NegativeEnum.NEG),
    (NegativeEnum, "f", NegativeEnum.ZERO),

    (FloatEnum, "f", EMPTY),
    (FloatEnum, "f", FloatEnum.LOW),

    (DuplicateEnum, "f", EMPTY),
    (DuplicateEnum, "f", DuplicateEnum.A),
    (DuplicateEnum, "f", DuplicateEnum.B),
    (DuplicateEnum, "f", 1),

    (SingleEnum | None, "f", EMPTY),
    (SingleEnum | None, "f", None),
    (SingleEnum | None, "f", SingleEnum.ONLY),
    (BoolEnum | None, "f", BoolEnum.NO),
    (NegativeEnum | None, "f", NegativeEnum.NEG),

    (Annotated[SingleEnum, Label("Pick")], "f", EMPTY),
    (Annotated[NegativeEnum, Label("N"), Description("D")], "f", EMPTY),

    (Literal["only"], "f", EMPTY),
    (Literal["only"], "f", "only"),
    (Literal[42], "f", EMPTY),
    (Literal[42], "f", 42),
    (Literal[True], "f", EMPTY),
    (Literal[True], "f", True),
    (Literal[False], "f", False),

    (Literal["a"] | None, "f", EMPTY),
    (Literal["a"] | None, "f", None),
    (Literal["a"] | None, "f", "a"),
    (Literal[1, 2, 3] | None, "f", None),

    (Annotated[str, Dropdown(single_option)], "f", EMPTY),
    (Annotated[str, Dropdown(single_option)], "f", "only"),
    (Annotated[int, Dropdown(returns_tuple)], "f", EMPTY),
    (Annotated[int, Dropdown(returns_tuple)], "f", 1),
    (Annotated[int, Dropdown(returns_tuple)], "f", 2),
    (Annotated[bool, Dropdown(bool_options)], "f", EMPTY),
    (Annotated[bool, Dropdown(bool_options)], "f", True),
    (Annotated[int, Dropdown(negative_options)], "f", EMPTY),
    (Annotated[int, Dropdown(negative_options)], "f", -10),
    (Annotated[int, Dropdown(negative_options)], "f", 0),
    (Annotated[float, Dropdown(float_options)], "f", EMPTY),
    (Annotated[float, Dropdown(float_options)], "f", 0.1),
    (Annotated[str, Dropdown(unicode_options)], "f", EMPTY),
    (Annotated[str, Dropdown(unicode_options)], "f", "café"),
    (Annotated[int, Dropdown(long_options)], "f", EMPTY),
    (Annotated[int, Dropdown(long_options)], "f", 0),
    (Annotated[int, Dropdown(long_options)], "f", 99),

    (Annotated[int, Field(ge=0)], "f", 0),
    (Annotated[int, Field(le=0)], "f", 0),
    (Annotated[int, Field(ge=0, le=0)], "f", 0),
    (Annotated[str, Field(min_length=0)], "f", ""),
    (Annotated[str, Field(max_length=0)], "f", ""),
    (Annotated[str, Field(min_length=0, max_length=0)], "f", ""),
    (Annotated[int, Field(ge=-999)], "f", -999),
    (Annotated[float, Field(ge=-0.0)], "f", 0.0),

    (float, "f", 0.0),
    (float, "f", -0.0),
    (float, "f", 1e-10),
    (float, "f", 1e10),
    (float, "f", 0.1 + 0.2),
    (Annotated[float, Field(ge=1e-100, le=1e100)], "f", 1e50),
    (Annotated[float, Field(ge=-1e100)], "f", -1e99),
    (Annotated[float, Field(ge=1e-10, le=1e-5)], "f", 1e-7),

    (str, "f", ""),
    (str, "f", " "),
    (str, "f", "\n"),
    (str, "f", "\t"),
    (str, "f", "café"),
    (str, "f", "日本語"),
    (str, "f", "🎉"),
    (str, "f", "a" * 10000),

    (date, "f", date.min),
    (date, "f", date.max),
    (date, "f", date(2000, 1, 1)),
    (date, "f", date(2024, 2, 29)),
    (time, "f", time.min),
    (time, "f", time.max),
    (time, "f", time(0, 0, 0)),
    (time, "f", time(23, 59, 59)),

    (list[Annotated[Annotated[int, Field(ge=0, le=100)], Slider(), Step(5)]], "f", EMPTY),
    (Annotated[list[Annotated[str, Field(min_length=1)]], Field(min_length=1, max_length=50)], "f", EMPTY),
    (list[SingleEnum], "f", EMPTY),
    (list[NegativeEnum], "f", EMPTY),
    (list[DuplicateEnum], "f", EMPTY),
    (list[Literal["a", "b"]], "f", EMPTY),
    (list[Literal[1, 2, 3]], "f", EMPTY),
    (list[ImageFile], "f", EMPTY),
    (list[DocumentFile], "f", EMPTY),
    (list[Annotated[str, Label("Tag"), Placeholder("...")]], "f", EMPTY),
    (Annotated[list[Annotated[int, Slider(), Field(ge=0, le=100)]], Label("Values"), Field(min_length=1)], "f", EMPTY),

    (Annotated[list[str], Field(min_length=0, max_length=0)], "f", []),
    (Annotated[list[Annotated[int, Field(ge=0, le=0)]], Field(min_length=1)], "f", [0, 0, 0]),
    (list[Annotated[float, Field(ge=0.0, le=1.0)]], "f", [0.0, 0.5, 1.0]),

    (list[Annotated[str, Dropdown(colors)]], "f", []),
    (list[Annotated[str, Dropdown(colors)]], "f", ["red"]),
    (list[Annotated[str, Dropdown(colors)]], "f", ["red", "green"]),
    (list[Annotated[str, Dropdown(colors)]], "f", ["blue"]),

    (Annotated[list[Email], Field(min_length=1, max_length=5)], "f", EMPTY),
    (Annotated[list[Color], Field(min_length=1)], "f", EMPTY),
    (list[Annotated[ImageFile, Label("Photo")]], "f", EMPTY),

    (Annotated[str, Field(pattern=r"^\d+$"), PatternMessage("Only numbers")], "f", EMPTY),
    (Annotated[str, Field(pattern=r"^\d+$"), PatternMessage("Only numbers")], "f", "123"),
    (Annotated[str, Field(pattern=r"^[a-z]+$"), PatternMessage("Lowercase only")], "f", "abc"),

    (Annotated[Annotated[Annotated[str, Field(min_length=1)], Field(min_length=2)], Field(min_length=3)], "f", EMPTY),
    (Annotated[Annotated[Annotated[str, Field(min_length=1)], Field(min_length=2)], Field(min_length=3)], "f", "abc"),
    (Annotated[Annotated[Annotated[int, Field(ge=0)], Field(ge=5)], Field(ge=10)], "f", 10),
    (Annotated[Annotated[str, Field(max_length=100)], Field(max_length=50)], "f", "x" * 50),

    (Color | None, "f", EMPTY),
    (Email | None, "f", EMPTY),
    (ImageFile | None, "f", EMPTY),
    (VideoFile | None, "f", EMPTY),
    (AudioFile | None, "f", EMPTY),
    (DataFile | None, "f", EMPTY),
    (TextFile | None, "f", EMPTY),
    (DocumentFile | None, "f", EMPTY),
    (File | None, "f", EMPTY),

    (Annotated[Color, Label("C"), Description("D")], "f", EMPTY),
    (Annotated[Email, Label("E"), Description("D")], "f", EMPTY),
    (Annotated[ImageFile, Label("I"), Description("D")], "f", EMPTY),

    (Annotated[Color, Label("C")] | None, "f", EMPTY),
    (Annotated[Email, Label("E")] | None, "f", EMPTY),

    (Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)] | None, "f", EMPTY),
    (Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)] | None, "f", None),
    (Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)] | None, "f", 50),
    (Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Slider(), Step(5)] | OptionalEnabled, "f", EMPTY),

    (Annotated[str, Label("PW"), Description("D"), Field(min_length=8, max_length=64), IsPassword(), Placeholder("***")] | None, "f", EMPTY),
    (Annotated[str, Label("PW"), Description("D"), Field(min_length=8, max_length=64), IsPassword(), Placeholder("***")] | None, "f", "password123"),

    (Annotated[str, Label("Bio"), Description("D"), Field(max_length=1000), Rows(10), Placeholder("...")] | None, "f", EMPTY),

    (Annotated[str, Label("Color"), Description("Pick"), Placeholder("..."), Dropdown(unicode_options)], "f", EMPTY),
    (Annotated[str, Label("Color"), Description("Pick"), Placeholder("..."), Dropdown(unicode_options)], "f", "café"),

    (int, "", EMPTY),
    (int, " ", EMPTY),
    (int, "a" * 1000, EMPTY),
    (int, "campo_1", EMPTY),
    (int, "café", EMPTY),
    (int, "日本語", EMPTY),
    (int, "🎉", EMPTY),
    (int, "has spaces", EMPTY),
    (int, "has-dashes", EMPTY),
    (int, "has.dots", EMPTY),
]


class EmptyEnum(Enum):
    pass

class MixedEnum(Enum):
    A = 1
    B = "two"

class MixedFloatIntEnum(Enum):
    A = 1
    B = 2.0

def empty_list():
    return []

def mixed_dropdown():
    return [1, "two", 3.0]

def none_in_dropdown():
    return [None, "a", "b"]

def raises_type_error():
    raise TypeError("boom")

def raises_value_error():
    raise ValueError("boom")


INVALID = [
    (Annotated[str, Field(min_length=3)] | None, "f", "ab"),
    (Annotated[int, Field(ge=0, le=100)] | None, "f", -1),
    (Annotated[int, Field(ge=0, le=100)] | None, "f", 101),
    (Annotated[int, Field(ge=0, le=100), Slider()] | None, "f", -1),

    (str | None, "f", 123),
    (int | None, "f", "no"),
    (float | None, "f", "no"),
    (bool | None, "f", 1),
    (int | None, "f", True),

    (SingleEnum, "f", NegativeEnum.NEG),

    (SingleEnum, "f", "ONLY"),

    (Literal["abc"], "f", "ABC"),
    (Literal["abc"], "f", "Abc"),

    (Literal[1, 2, 3], "f", "1"),
    (Literal["a", "b"], "f", 0),

    (EmptyEnum, "f", EMPTY),
    (MixedEnum, "f", EMPTY),
    (MixedFloatIntEnum, "f", EMPTY),

    (Annotated[str, Dropdown(empty_list)], "f", EMPTY),
    (Annotated[str, Dropdown(mixed_dropdown)], "f", EMPTY),
    (Annotated[str, Dropdown(none_in_dropdown)], "f", EMPTY),
    (Annotated[str, Dropdown(raises_type_error)], "f", EMPTY),
    (Annotated[str, Dropdown(raises_value_error)], "f", EMPTY),
    (Annotated[str, Dropdown(42)], "f", EMPTY),
    (Annotated[str, Dropdown(None)], "f", EMPTY),

    (Annotated[str, Dropdown(single_option)], "f", "invalid"),
    (Annotated[str, Dropdown(single_option)], "f", "ONLY"),
    (Annotated[int, Dropdown(returns_tuple)], "f", 0),
    (Annotated[int, Dropdown(returns_tuple)], "f", 4),
    (Annotated[bool, Dropdown(bool_options)], "f", 1),
    (Annotated[int, Dropdown(negative_options)], "f", -11),
    (Annotated[int, Dropdown(negative_options)], "f", 11),
    (Annotated[float, Dropdown(float_options)], "f", 0.2),
    (Annotated[str, Dropdown(unicode_options)], "f", "hello"),
    (Annotated[int, Dropdown(long_options)], "f", 100),
    (Annotated[int, Dropdown(long_options)], "f", -1),

    (Annotated[int, Field(ge=0, le=0)], "f", 1),
    (Annotated[int, Field(ge=0, le=0)], "f", -1),
    (Annotated[str, Field(max_length=0)], "f", "a"),
    (Annotated[int, Field(gt=0, lt=1)], "f", 0),
    (Annotated[int, Field(gt=0, lt=1)], "f", 1),

    (list[list[str]], "f", EMPTY),
    (list[list[list[int]]], "f", EMPTY),
    (Annotated[list[list[str]], Field(min_length=1)], "f", EMPTY),
    (list[Annotated[list[int], Field(min_length=1)]], "f", EMPTY),

    (list[dict], "f", EMPTY),
    (list[set], "f", EMPTY),
    (list[tuple], "f", EMPTY),
    (list[bytes], "f", EMPTY),
    (list[object], "f", EMPTY),
    (list[type], "f", EMPTY),
    (list[list], "f", EMPTY),

    (Annotated[list[str], Slider()], "f", EMPTY),
    (Annotated[list[str], IsPassword()], "f", EMPTY),
    (Annotated[list[str], Rows(5)], "f", EMPTY),
    (Annotated[list[str], Placeholder("X")], "f", EMPTY),
    (Annotated[list[str], Step(1)], "f", EMPTY),

    (Annotated[list[int], Field(ge=0)], "f", EMPTY),
    (Annotated[list[int], Field(le=100)], "f", EMPTY),
    (Annotated[list[str], Field(pattern=r"^\d+$")], "f", EMPTY),

    (str | int | None, "f", EMPTY),
    (str | int | float, "f", EMPTY),
    (str | int | float | None, "f", EMPTY),
    (Union[str, int, None], "f", EMPTY),
    (Union[str, int, float, bool], "f", EMPTY),

    (str | int, "f", EMPTY),
    (int | float, "f", EMPTY),
    (bool | int, "f", EMPTY),
    (str | date, "f", EMPTY),
    (list[str] | list[int], "f", EMPTY),

    (None, "f", EMPTY),
    (type(None), "f", EMPTY),

    (dict, "f", EMPTY),
    (set, "f", EMPTY),
    (tuple, "f", EMPTY),
    (bytes, "f", EMPTY),
    (complex, "f", EMPTY),
    (object, "f", EMPTY),
    (type, "f", EMPTY),
    (list, "f", EMPTY),
    (int | str, "f", EMPTY),

    (Annotated[int, "random string"], "f", EMPTY),
    (Annotated[str, "a", "b", "c"], "f", EMPTY),
    (Annotated[int | None, "metadata"], "f", EMPTY),

    (int, "f", True),
    (int, "f", False),
    (bool, "f", 0),
    (bool, "f", 1),
    (bool, "f", -1),
    (Annotated[int, Field(ge=0)], "f", True),
    (Annotated[bool, Field()], "f", 0),

    (Annotated[int, Field(ge=0)], "f", "0"),
    (Annotated[str, Field(min_length=1)], "f", 1),
    (Annotated[float, Field(ge=0.0)], "f", 0),
    (Annotated[float, Field(ge=0.0)], "f", True),

    (list[Annotated[str, Dropdown(colors)]], "f", ["purple"]),
    (list[Annotated[str, Dropdown(colors)]], "f", ["red", "purple"]),
    (list[Annotated[str, Dropdown(colors)]], "f", ["RED"]),

    (int, 123, EMPTY),
    (int, None, EMPTY),
    (int, True, EMPTY),
    (int, 3.14, EMPTY),
    (int, [], EMPTY),
    (int, {}, EMPTY),

    # Slider without bounds
    (Annotated[int, Slider()], "f", EMPTY),
    (Annotated[int, Slider(), Field(ge=0)], "f", EMPTY),
    (Annotated[int, Slider(), Field(le=100)], "f", EMPTY),
    (Annotated[float, Slider()], "f", EMPTY),
    (list[Annotated[int, Slider()]], "f", EMPTY),
    (Annotated[int, Slider(), Field(gt=0)], "f", EMPTY),
    (Annotated[int, Slider(), Field(lt=100)], "f", EMPTY),
]


@pytest.mark.parametrize("annotation, name, default", VALID)
def test_edge_valid(annotation, name, default):
    result = analyze_type(annotation, name, default)
    assert isinstance(result, ParamMetadata)


@pytest.mark.parametrize("annotation, name, default", INVALID)
def test_edge_invalid(annotation, name, default):
    with pytest.raises((TypeError, ValueError)):
        analyze_type(annotation, name, default)
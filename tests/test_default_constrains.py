import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.types import Dropdown, Slider, Step

EMPTY = inspect.Parameter.empty


class Color(Enum):
    R = "red"
    G = "green"
    B = "blue"


class Size(Enum):
    S = 1
    M = 2
    L = 3


def colors():
    return ["red", "green", "blue"]


def numbers():
    return [1, 2, 3]


VALID = [
    (Annotated[int, Field(ge=0)], 0),
    (Annotated[int, Field(ge=0)], 1),
    (Annotated[int, Field(ge=0)], 999),
    (Annotated[int, Field(ge=-10)], -10),
    (Annotated[int, Field(ge=-10)], 0),
    (Annotated[float, Field(ge=0.0)], 0.0),
    (Annotated[float, Field(ge=0.0)], 0.001),
    (Annotated[int, Field(le=100)], 100),
    (Annotated[int, Field(le=100)], 0),
    (Annotated[int, Field(le=100)], -50),
    (Annotated[float, Field(le=1.0)], 1.0),
    (Annotated[float, Field(le=1.0)], 0.0),
    (Annotated[int, Field(gt=0)], 1),
    (Annotated[int, Field(gt=0)], 999),
    (Annotated[float, Field(gt=0.0)], 0.001),
    (Annotated[int, Field(lt=100)], 99),
    (Annotated[int, Field(lt=100)], 0),
    (Annotated[int, Field(lt=100)], -999),
    (Annotated[float, Field(lt=1.0)], 0.999),
    (Annotated[int, Field(ge=0, le=100)], 0),
    (Annotated[int, Field(ge=0, le=100)], 50),
    (Annotated[int, Field(ge=0, le=100)], 100),
    (Annotated[float, Field(ge=0.0, le=1.0)], 0.0),
    (Annotated[float, Field(ge=0.0, le=1.0)], 0.5),
    (Annotated[float, Field(ge=0.0, le=1.0)], 1.0),
    (Annotated[int, Field(gt=0, lt=100)], 1),
    (Annotated[int, Field(gt=0, lt=100)], 50),
    (Annotated[int, Field(gt=0, lt=100)], 99),
    (Annotated[float, Field(gt=0.0, lt=1.0)], 0.001),
    (Annotated[float, Field(gt=0.0, lt=1.0)], 0.999),
    (Annotated[int, Field(ge=0, lt=100)], 0),
    (Annotated[int, Field(ge=0, lt=100)], 99),
    (Annotated[int, Field(gt=0, le=100)], 1),
    (Annotated[int, Field(gt=0, le=100)], 100),
    (Annotated[str, Field(min_length=0)], ""),
    (Annotated[str, Field(min_length=0)], "a"),
    (Annotated[str, Field(min_length=1)], "a"),
    (Annotated[str, Field(min_length=1)], "abc"),
    (Annotated[str, Field(min_length=3)], "abc"),
    (Annotated[str, Field(min_length=3)], "abcdef"),
    (Annotated[str, Field(max_length=5)], ""),
    (Annotated[str, Field(max_length=5)], "a"),
    (Annotated[str, Field(max_length=5)], "abcde"),
    (Annotated[str, Field(min_length=2, max_length=5)], "ab"),
    (Annotated[str, Field(min_length=2, max_length=5)], "abc"),
    (Annotated[str, Field(min_length=2, max_length=5)], "abcde"),
    (Annotated[str, Field(pattern=r"^\d+$")], "123"),
    (Annotated[str, Field(pattern=r"^\d+$")], "0"),
    (Annotated[str, Field(pattern=r"^[a-z]+$")], "abc"),
    (Annotated[str, Field(pattern=r"^[A-Z]{3}$")], "ABC"),
    (Annotated[str, Field(pattern=r"^\d+$", min_length=2)], "12"),
    (Annotated[str, Field(pattern=r"^\d+$", min_length=2)], "123456"),
    (Annotated[int, Field(ge=0, le=100), Slider(), Step(5)], 0),
    (Annotated[int, Field(ge=0, le=100), Slider(), Step(5)], 50),
    (Annotated[int, Field(ge=0, le=100), Slider(), Step(5)], 100),
    (Annotated[int, Field(ge=0, le=100)] | None, 50),
    (Annotated[str, Field(min_length=3)] | None, "abc"),
    (Annotated[int, Field(ge=0)] | None, None),
    (Annotated[str, Field(min_length=3)] | None, None),
    (Annotated[int, Field(ge=0, le=100)], EMPTY),
    (Annotated[str, Field(min_length=3, max_length=20)], EMPTY),
    (Annotated[str, Field(pattern=r"^\d+$")], EMPTY),
    (Color, "f", Color.R),
    (Color, "f", Color.G),
    (Color, "f", Color.B),
    (Size, "f", Size.S),
    (Size, "f", Size.M),
    (Size, "f", Size.L),
    (Color, "f", "red"),
    (Color, "f", "green"),
    (Color, "f", "blue"),
    (Size, "f", 1),
    (Size, "f", 2),
    (Size, "f", 3),
    (Literal["a", "b", "c"], "f", "a"),
    (Literal["a", "b", "c"], "f", "b"),
    (Literal["a", "b", "c"], "f", "c"),
    (Literal[1, 2, 3], "f", 1),
    (Literal[1, 2, 3], "f", 2),
    (Literal[1, 2, 3], "f", 3),
    (Annotated[str, Dropdown(colors)], "f", "red"),
    (Annotated[str, Dropdown(colors)], "f", "green"),
    (Annotated[str, Dropdown(colors)], "f", "blue"),
    (Annotated[int, Dropdown(numbers)], "f", 1),
    (Annotated[int, Dropdown(numbers)], "f", 2),
    (Annotated[int, Dropdown(numbers)], "f", 3),
    (Color | None, "f", Color.R),
    (Color | None, "f", "red"),
    (Color | None, "f", None),
    (Size | None, "f", Size.L),
    (Size | None, "f", 3),
    (Size | None, "f", None),
]


INVALID = [
    (Annotated[int, Field(ge=0)], -1),
    (Annotated[int, Field(ge=10)], 9),
    (Annotated[float, Field(ge=0.0)], -0.001),
    (Annotated[int, Field(le=100)], 101),
    (Annotated[float, Field(le=1.0)], 1.001),
    (Annotated[int, Field(gt=0)], 0),
    (Annotated[int, Field(gt=0)], -1),
    (Annotated[float, Field(gt=0.0)], 0.0),
    (Annotated[float, Field(gt=0.0)], -0.001),
    (Annotated[int, Field(lt=100)], 100),
    (Annotated[int, Field(lt=100)], 101),
    (Annotated[float, Field(lt=1.0)], 1.0),
    (Annotated[float, Field(lt=1.0)], 1.001),
    (Annotated[int, Field(ge=0, le=100)], -1),
    (Annotated[int, Field(ge=0, le=100)], 101),
    (Annotated[float, Field(ge=0.0, le=1.0)], -0.001),
    (Annotated[float, Field(ge=0.0, le=1.0)], 1.001),
    (Annotated[int, Field(gt=0, lt=100)], 0),
    (Annotated[int, Field(gt=0, lt=100)], 100),
    (Annotated[float, Field(gt=0.0, lt=1.0)], 0.0),
    (Annotated[float, Field(gt=0.0, lt=1.0)], 1.0),
    (Annotated[int, Field(ge=0, lt=100)], 100),
    (Annotated[int, Field(ge=0, lt=100)], -1),
    (Annotated[int, Field(gt=0, le=100)], 0),
    (Annotated[int, Field(gt=0, le=100)], 101),
    (Annotated[str, Field(min_length=1)], ""),
    (Annotated[str, Field(min_length=3)], "ab"),
    (Annotated[str, Field(min_length=3)], ""),
    (Annotated[str, Field(min_length=5)], "abcd"),
    (Annotated[str, Field(max_length=3)], "abcd"),
    (Annotated[str, Field(max_length=5)], "abcdef"),
    (Annotated[str, Field(max_length=0)], "a"),
    (Annotated[str, Field(min_length=2, max_length=5)], "a"),
    (Annotated[str, Field(min_length=2, max_length=5)], "abcdef"),
    (Annotated[str, Field(pattern=r"^\d+$")], "abc"),
    (Annotated[str, Field(pattern=r"^\d+$")], ""),
    (Annotated[str, Field(pattern=r"^\d+$")], "12a"),
    (Annotated[str, Field(pattern=r"^[a-z]+$")], "ABC"),
    (Annotated[str, Field(pattern=r"^[a-z]+$")], "abc123"),
    (Annotated[str, Field(pattern=r"^[A-Z]{3}$")], "AB"),
    (Annotated[str, Field(pattern=r"^[A-Z]{3}$")], "ABCD"),
    (Annotated[str, Field(pattern=r"^[A-Z]{3}$")], "abc"),
    (Annotated[str, Field(pattern=r"^\d+$", min_length=2)], "1"),
    (Annotated[int, Field(ge=0, le=100)] | None, -1),
    (Annotated[int, Field(ge=0, le=100)] | None, 101),
    (Annotated[str, Field(min_length=3)] | None, "ab"),
    (Annotated[int, Field(ge=0, le=100), Slider()], -1),
    (Annotated[int, Field(ge=0, le=100), Slider()], 101),
    (Annotated[int, Field(ge=0)], "not_int"),
    (Annotated[str, Field(min_length=3)], 42),
    (Annotated[float, Field(ge=0.0)], "zero"),
    (Annotated[int, Field(ge=0)], True),
    (Annotated[bool, Field()], 1),
    (Color, "f", "yellow"),
    (Color, "f", "RED"),
    (Color, "f", "rojo"),
    (Size, "f", 4),
    (Size, "f", 0),
    (Size, "f", -1),
    (Color, "f", 123),
    (Color, "f", True),
    (Size, "f", "one"),
    (Size, "f", 1.5),
    (Literal["a", "b", "c"], "f", "d"),
    (Literal["a", "b", "c"], "f", "A"),
    (Literal[1, 2, 3], "f", 4),
    (Literal[1, 2, 3], "f", 0),
    (Annotated[str, Dropdown(colors)], "f", "purple"),
    (Annotated[str, Dropdown(colors)], "f", "RED"),
    (Annotated[int, Dropdown(numbers)], "f", 0),
    (Annotated[int, Dropdown(numbers)], "f", 4),
    (Annotated[int, Dropdown(numbers)], "f", 999),
]


LIST_VALID = [
    (list[int], []),
    (list[int], [1, 2, 3]),
    (list[str], []),
    (list[str], ["a", "b", "c"]),
    (list[float], [1.0, 2.5, 3.14]),
    (list[bool], [True, False]),
    (list[date], []),
    (list[time], []),
    (Annotated[list[int], Field(min_length=0)], []),
    (Annotated[list[int], Field(min_length=0)], [1]),
    (Annotated[list[int], Field(min_length=1)], [1]),
    (Annotated[list[int], Field(min_length=1)], [1, 2, 3]),
    (Annotated[list[str], Field(min_length=2)], ["a", "b"]),
    (Annotated[list[str], Field(min_length=2)], ["a", "b", "c", "d"]),
    (Annotated[list[int], Field(max_length=3)], []),
    (Annotated[list[int], Field(max_length=3)], [1]),
    (Annotated[list[int], Field(max_length=3)], [1, 2, 3]),
    (Annotated[list[str], Field(max_length=2)], []),
    (Annotated[list[str], Field(max_length=2)], ["a"]),
    (Annotated[list[str], Field(max_length=2)], ["a", "b"]),
    (Annotated[list[int], Field(max_length=0)], []),
    (Annotated[list[int], Field(min_length=1, max_length=3)], [1]),
    (Annotated[list[int], Field(min_length=1, max_length=3)], [1, 2]),
    (Annotated[list[int], Field(min_length=1, max_length=3)], [1, 2, 3]),
    (Annotated[list[str], Field(min_length=2, max_length=4)], ["a", "b"]),
    (Annotated[list[str], Field(min_length=2, max_length=4)], ["a", "b", "c"]),
    (list[Annotated[int, Field(ge=0)]], []),
    (list[Annotated[int, Field(ge=0)]], [0]),
    (list[Annotated[int, Field(ge=0)]], [0, 1, 2]),
    (list[Annotated[int, Field(ge=0)]], [100, 999]),
    (list[Annotated[int, Field(ge=0, le=100)]], [0, 50, 100]),
    (list[Annotated[str, Field(min_length=3)]], []),
    (list[Annotated[str, Field(min_length=3)]], ["abc"]),
    (list[Annotated[str, Field(min_length=3)]], ["abc", "def", "ghi"]),
    (list[Annotated[str, Field(pattern=r"^\d+$")]], []),
    (list[Annotated[str, Field(pattern=r"^\d+$")]], ["123", "456"]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=1)], [0]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=1)], [1, 2, 3]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(max_length=3)], [0]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(max_length=3)], [1, 2, 3]),
    (Annotated[list[Annotated[str, Field(min_length=2)]], Field(min_length=1, max_length=3)], ["ab"]),
    (Annotated[list[Annotated[str, Field(min_length=2)]], Field(min_length=1, max_length=3)], ["ab", "cd", "ef"]),
    (list[Color], []),
    (list[Color], [Color.R]),
    (list[Color], [Color.R, Color.G]),
    (list[Color], [Color.R, Color.G, Color.B]),
    (list[Size], [Size.S, Size.M, Size.L]),
    (list[Color], ["red"]),
    (list[Color], ["red", "green"]),
    (list[Color], ["red", "green", "blue"]),
    (list[Size], [1]),
    (list[Size], [1, 2]),
    (list[Size], [1, 2, 3]),
    (list[Color], [Color.R, "green"]),
    (list[Color], ["red", Color.G, "blue"]),
    (list[Size], [Size.S, 2]),
    (list[Size], [1, Size.M, 3]),
    (list[Literal["a", "b", "c"]], []),
    (list[Literal["a", "b", "c"]], ["a"]),
    (list[Literal["a", "b", "c"]], ["a", "b"]),
    (list[Literal["a", "b", "c"]], ["a", "b", "c"]),
    (list[Literal[1, 2, 3]], []),
    (list[Literal[1, 2, 3]], [1, 2, 3]),
    (Annotated[list[Color], Field(min_length=1)], [Color.R]),
    (Annotated[list[Color], Field(min_length=1)], [Color.R, Color.G]),
    (Annotated[list[Color], Field(min_length=1, max_length=3)], [Color.R]),
    (Annotated[list[Color], Field(min_length=1, max_length=3)], [Color.R, Color.G]),
    (Annotated[list[Size], Field(max_length=2)], [Size.S]),
    (Annotated[list[Color], Field(min_length=1)], ["red"]),
    (Annotated[list[Color], Field(min_length=1)], ["red", "green"]),
    (Annotated[list[Size], Field(max_length=2)], [1]),
    (Annotated[list[Size], Field(max_length=2)], [1, 2]),
    (Annotated[list[Color], Field(min_length=1)], [Color.R, "green"]),
    (Annotated[list[Size], Field(max_length=2)], [Size.S, 2]),
    (Annotated[list[Literal["a", "b"]], Field(min_length=1)], ["a"]),
    (Annotated[list[Literal[1, 2, 3]], Field(max_length=2)], [1, 2]),
    (list[Annotated[str, Dropdown(colors)]], []),
    (list[Annotated[str, Dropdown(colors)]], ["red"]),
    (list[Annotated[str, Dropdown(colors)]], ["red", "green"]),
    (list[Annotated[str, Dropdown(colors)]], ["blue"]),
    (list[Annotated[int, Dropdown(numbers)]], [1, 2]),
    (list[Annotated[int, Dropdown(numbers)]], [1, 2, 3]),
    (list[int] | None, None),
    (list[str] | None, None),
    (Annotated[list[int], Field(min_length=1)] | None, None),
    (Annotated[list[str], Field(max_length=5)] | None, None),
    (list[int] | None, []),
    (list[int] | None, [1, 2, 3]),
    (Annotated[list[int], Field(min_length=1)] | None, [1]),
    (Annotated[list[int], Field(min_length=1)] | None, [1, 2, 3]),
    (Annotated[list[str], Field(max_length=3)] | None, ["a", "b"]),
    (list[int], EMPTY),
    (list[str], EMPTY),
    (Annotated[list[int], Field(min_length=1)], EMPTY),
    (Annotated[list[int], Field(max_length=10)], EMPTY),
    (list[Annotated[int, Field(ge=0)]], EMPTY),
]


LIST_INVALID = [
    (Annotated[list[int], Field(min_length=1)], []),
    (Annotated[list[str], Field(min_length=2)], []),
    (Annotated[list[str], Field(min_length=2)], ["a"]),
    (Annotated[list[str], Field(min_length=3)], ["a", "b"]),
    (Annotated[list[int], Field(min_length=5)], [1, 2, 3]),
    (Annotated[list[int], Field(max_length=2)], [1, 2, 3]),
    (Annotated[list[str], Field(max_length=1)], ["a", "b"]),
    (Annotated[list[int], Field(max_length=0)], [1]),
    (Annotated[list[str], Field(max_length=3)], ["a", "b", "c", "d"]),
    (Annotated[list[int], Field(min_length=2, max_length=4)], [1]),
    (Annotated[list[int], Field(min_length=2, max_length=4)], [1, 2, 3, 4, 5]),
    (Annotated[list[str], Field(min_length=1, max_length=2)], []),
    (Annotated[list[str], Field(min_length=1, max_length=2)], ["a", "b", "c"]),
    (list[Annotated[int, Field(ge=0)]], [-1]),
    (list[Annotated[int, Field(ge=0)]], [-1, 0, 1]),
    (list[Annotated[int, Field(ge=0)]], [1, 2, -5]),
    (list[Annotated[int, Field(ge=0, le=100)]], [0, 50, 101]),
    (list[Annotated[int, Field(ge=0, le=100)]], [-1, 50]),
    (list[Annotated[str, Field(min_length=3)]], ["ab"]),
    (list[Annotated[str, Field(min_length=3)]], ["abc", "de"]),
    (list[Annotated[str, Field(min_length=3)]], ["a", "abc"]),
    (list[Annotated[str, Field(pattern=r"^\d+$")]], ["abc"]),
    (list[Annotated[str, Field(pattern=r"^\d+$")]], ["123", "abc"]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=1)], []),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)], [1]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(max_length=2)], [1, 2, 3]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=1)], [-1]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)], [-1, 0]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)], [1, -1]),
    (Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)], [-1]),
    (list[int], ["not", "ints"]),
    (list[str], [1, 2, 3]),
    (list[int], [1, "two", 3]),
    (list[float], ["1.0", "2.5"]),
    (list[bool], [0, 1]),
    (list[bool], ["true", "false"]),
    (list[Color], [Color.R, "yellow"]),
    (list[Color], ["yellow"]),
    (list[Color], ["red", "yellow"]),
    (list[Color], [Color.R, "RED"]),
    (list[Size], [Size.S, 4]),
    (list[Size], [4]),
    (list[Size], [1, 4]),
    (list[Size], [0, 1]),
    (list[Color], [123]),
    (list[Color], [Color.R, 123]),
    (list[Size], ["one"]),
    (list[Size], [Size.S, "two"]),
    (list[Size], [1.5]),
    (list[Literal["a", "b", "c"]], ["d"]),
    (list[Literal["a", "b", "c"]], ["a", "d"]),
    (list[Literal[1, 2, 3]], [4]),
    (list[Literal[1, 2, 3]], [1, 4]),
    (list[Literal[1, 2, 3]], [0, 1, 2]),
    (list[Annotated[str, Dropdown(colors)]], ["purple"]),
    (list[Annotated[str, Dropdown(colors)]], ["red", "purple"]),
    (list[Annotated[int, Dropdown(numbers)]], [999]),
    (list[Annotated[int, Dropdown(numbers)]], [1, 999]),
    (Annotated[list[int], Field(min_length=1)] | None, []),
    (Annotated[list[str], Field(min_length=2)] | None, ["a"]),
    (Annotated[list[int], Field(max_length=2)] | None, [1, 2, 3]),
    (list[Annotated[int, Field(ge=0)]] | None, [-1, 0, 1]),
    (list[Annotated[int, Field(ge=0)]] | None, [-1]),
    (list[int], "not a list"),
    (list[int], 123),
    (list[str], "string"),
    (Annotated[list[str], Field(min_length=1)], {}),
    (Annotated[list[int], Field(max_length=5)], {1, 2, 3}),
]


def _unpack(case):
    if len(case) == 2:
        return case[0], "f", case[1]
    return case


@pytest.mark.parametrize("case", VALID)
def test_default_valid(case):
    ann, name, default = _unpack(case)
    result = analyze_type(ann, name, default)
    assert result is not None


@pytest.mark.parametrize("case", INVALID)
def test_default_invalid(case):
    ann, name, default = _unpack(case)
    with pytest.raises((TypeError, ValueError)):
        analyze_type(ann, name, default)


@pytest.mark.parametrize("case", LIST_VALID)
def test_list_default_valid(case):
    ann, name, default = _unpack(case)
    result = analyze_type(ann, name, default)
    assert result is not None


@pytest.mark.parametrize("case", LIST_INVALID)
def test_list_default_invalid(case):
    ann, name, default = _unpack(case)
    with pytest.raises((TypeError, ValueError)):
        analyze_type(ann, name, default)
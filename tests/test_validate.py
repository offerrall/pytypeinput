import pytest
from typing import Annotated, Literal
from datetime import date, time
from enum import Enum

from pydantic import Field

from pytypeinput import analyze_type
from pytypeinput.validate import validate_value


# ─── Enums ───────────────────────────────────────────────────────────

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# ─── Helpers ─────────────────────────────────────────────────────────

def meta(annotation, name="field", default=...):
    if default is ...:
        import inspect
        default = inspect.Parameter.empty
    return analyze_type(annotation, name, default)


# ─── None handling ───────────────────────────────────────────────────

NONE_PASS = [
    ("optional str",        meta(str | None, "f"),              None, None),
    ("optional int",        meta(int | None, "f"),              None, None),
    ("optional float",      meta(float | None, "f"),            None, None),
    ("optional bool",       meta(bool | None, "f"),             None, None),
    ("optional date",       meta(date | None, "f"),             None, None),
    ("optional time",       meta(time | None, "f"),             None, None),
    ("optional enum",       meta(Color | None, "f"),            None, None),
    ("optional list",       meta(list[int] | None, "f"),        None, None),
]

NONE_FAIL = [
    ("required str",        meta(str, "f")),
    ("required int",        meta(int, "f")),
    ("required float",      meta(float, "f")),
    ("required bool",       meta(bool, "f")),
    ("required date",       meta(date, "f")),
    ("required time",       meta(time, "f")),
    ("required enum",       meta(Color, "f")),
]

@pytest.mark.parametrize("label,m,value,expected", NONE_PASS, ids=[x[0] for x in NONE_PASS])
def test_none_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m", NONE_FAIL, ids=[x[0] for x in NONE_FAIL])
def test_none_fail(label, m):
    with pytest.raises(ValueError):
        validate_value(m, None)


# ─── Python native values (passthrough) ─────────────────────────────

PYTHON_NATIVE = [
    ("str",             meta(str, "f"),         "hello",                "hello"),
    ("int",             meta(int, "f"),         42,                     42),
    ("float",           meta(float, "f"),       3.14,                   3.14),
    ("bool true",       meta(bool, "f"),        True,                   True),
    ("bool false",      meta(bool, "f"),        False,                  False),
    ("date",            meta(date, "f"),        date(2024, 1, 15),      date(2024, 1, 15)),
    ("time",            meta(time, "f"),        time(14, 30),           time(14, 30)),
    ("enum by instance",meta(Color, "f"),       Color.RED,              Color.RED),
    ("enum int inst",   meta(Priority, "f"),    Priority.HIGH,          Priority.HIGH),
]

@pytest.mark.parametrize("label,m,value,expected", PYTHON_NATIVE, ids=[x[0] for x in PYTHON_NATIVE])
def test_python_native(label, m, value, expected):
    assert validate_value(m, value) == expected


# ─── JSON/string coercion ────────────────────────────────────────────

JSON_COERCE = [
    ("str→int",             meta(int, "f"),         "42",           42),
    ("str→float",           meta(float, "f"),       "3.14",         3.14),
    ("str→bool true",       meta(bool, "f"),        "true",         True),
    ("str→bool false",      meta(bool, "f"),        "false",        False),
    ("str→bool 1",          meta(bool, "f"),        "1",            True),
    ("str→bool 0",          meta(bool, "f"),        "0",            False),
    ("str→bool yes",        meta(bool, "f"),        "yes",          True),
    ("str→bool no",         meta(bool, "f"),        "no",           False),
    ("str→bool TRUE",       meta(bool, "f"),        "TRUE",         True),
    ("str→date",            meta(date, "f"),        "2024-01-15",   date(2024, 1, 15)),
    ("str→time",            meta(time, "f"),        "14:30:00",     time(14, 30)),
    ("str→time short",      meta(time, "f"),        "08:00",        time(8, 0)),
    ("float→int exact",     meta(int, "f"),         42.0,           42),
    ("int→float",           meta(float, "f"),       3,              3.0),
    ("int 1→bool",          meta(bool, "f"),        1,              True),
    ("int 0→bool",          meta(bool, "f"),        0,              False),
    ("enum by str value",   meta(Color, "f"),       "red",          Color.RED),
    ("enum by str name",    meta(Color, "f"),       "RED",          Color.RED),
    ("enum by int value",   meta(Priority, "f"),    2,              Priority.MEDIUM),
]

@pytest.mark.parametrize("label,m,value,expected", JSON_COERCE, ids=[x[0] for x in JSON_COERCE])
def test_json_coerce(label, m, value, expected):
    assert validate_value(m, value) == expected


# ─── Coercion failures ──────────────────────────────────────────────

COERCE_FAIL = [
    ("bool→int",            meta(int, "f"),         True,       TypeError),
    ("bool→float",          meta(float, "f"),       True,       TypeError),
    ("str bad→int",         meta(int, "f"),         "abc",      TypeError),
    ("str bad→float",       meta(float, "f"),       "abc",      TypeError),
    ("str bad→bool",        meta(bool, "f"),        "maybe",    TypeError),
    ("str bad→date",        meta(date, "f"),        "not-date", ValueError),
    ("str bad→time",        meta(time, "f"),        "not-time", ValueError),
    ("int→str",             meta(str, "f"),         42,         TypeError),
    ("list→str",            meta(str, "f"),         [1, 2],     TypeError),
    ("dict→int",            meta(int, "f"),         {},         TypeError),
    ("float frac→int",      meta(int, "f"),         3.7,        TypeError),
    ("str bad→float raise", meta(float, "f"),       "xyz",      TypeError),
    ("none→str",            meta(str, "f"),         [],         TypeError),
    ("enum bad value",      meta(Color, "f"),       "yellow",   ValueError),
    ("enum bad int",        meta(Priority, "f"),    99,         ValueError),
    ("int→date",            meta(date, "f"),        20240115,   TypeError),
    ("int→time",            meta(time, "f"),        1430,       TypeError),
    ("bytes→int",           meta(int, "f"),         b"hello",   TypeError),
]

@pytest.mark.parametrize("label,m,value,exc", COERCE_FAIL, ids=[x[0] for x in COERCE_FAIL])
def test_coerce_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Empty string on required ───────────────────────────────────────

EMPTY_STR = [
    ("empty str",           meta(str, "f"),         "",         ValueError),
    ("whitespace str",      meta(str, "f"),         "   ",      ValueError),
    ("tab str",             meta(str, "f"),         "\t\n",     ValueError),
]

@pytest.mark.parametrize("label,m,value,exc", EMPTY_STR, ids=[x[0] for x in EMPTY_STR])
def test_empty_str_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Constraints ─────────────────────────────────────────────────────

CONSTRAINTS_PASS = [
    ("int ge/le mid",       meta(Annotated[int, Field(ge=0, le=100)], "f"),     50,         50),
    ("int ge/le min",       meta(Annotated[int, Field(ge=0, le=100)], "f"),     0,          0),
    ("int ge/le max",       meta(Annotated[int, Field(ge=0, le=100)], "f"),     100,        100),
    ("float gt/lt",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"), 0.5,        0.5),
    ("str min/max len",     meta(Annotated[str, Field(min_length=2, max_length=5)], "f"), "abc", "abc"),
    ("str pattern",         meta(Annotated[str, Field(pattern=r"^\d{3}$")], "f"), "123",    "123"),
    ("str from json",       meta(Annotated[int, Field(ge=0, le=100)], "f"),     "50",       50),
]

CONSTRAINTS_FAIL = [
    ("int below ge",        meta(Annotated[int, Field(ge=0, le=100)], "f"),     -1,         ValueError),
    ("int above le",        meta(Annotated[int, Field(ge=0, le=100)], "f"),     101,        ValueError),
    ("float at gt",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"), 0.0,        ValueError),
    ("float at lt",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"), 1.0,        ValueError),
    ("str too short",       meta(Annotated[str, Field(min_length=2, max_length=5)], "f"), "a", ValueError),
    ("str too long",        meta(Annotated[str, Field(min_length=2, max_length=5)], "f"), "abcdef", ValueError),
    ("str bad pattern",     meta(Annotated[str, Field(pattern=r"^\d{3}$")], "f"), "12",     ValueError),
    ("str json bad",        meta(Annotated[int, Field(ge=0, le=100)], "f"),     "-1",       ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", CONSTRAINTS_PASS, ids=[x[0] for x in CONSTRAINTS_PASS])
def test_constraints_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", CONSTRAINTS_FAIL, ids=[x[0] for x in CONSTRAINTS_FAIL])
def test_constraints_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Choices: Enum ───────────────────────────────────────────────────

ENUM_CHOICES_PASS = [
    ("enum instance",       meta(Color, "f"),       Color.BLUE,     Color.BLUE),
    ("enum by value",       meta(Color, "f"),       "green",        Color.GREEN),
    ("enum by name",        meta(Color, "f"),       "BLUE",         Color.BLUE),
    ("int enum instance",   meta(Priority, "f"),    Priority.LOW,   Priority.LOW),
    ("int enum by value",   meta(Priority, "f"),    1,              Priority.LOW),
]

ENUM_CHOICES_FAIL = [
    ("enum bad str",        meta(Color, "f"),       "purple",       ValueError),
    ("enum bad int",        meta(Priority, "f"),    99,             ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", ENUM_CHOICES_PASS, ids=[x[0] for x in ENUM_CHOICES_PASS])
def test_enum_choices_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", ENUM_CHOICES_FAIL, ids=[x[0] for x in ENUM_CHOICES_FAIL])
def test_enum_choices_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Choices: Literal ────────────────────────────────────────────────

LITERAL_PASS = [
    ("literal str",         meta(Literal["a", "b", "c"], "f"),  "a",    "a"),
    ("literal str b",       meta(Literal["a", "b", "c"], "f"),  "b",    "b"),
    ("literal int",         meta(Literal[1, 2, 3], "f"),        2,      2),
]

LITERAL_FAIL = [
    ("literal bad str",     meta(Literal["a", "b", "c"], "f"),  "z",    ValueError),
    ("literal bad int",     meta(Literal[1, 2, 3], "f"),        9,      ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LITERAL_PASS, ids=[x[0] for x in LITERAL_PASS])
def test_literal_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LITERAL_FAIL, ids=[x[0] for x in LITERAL_FAIL])
def test_literal_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Lists: basic ───────────────────────────────────────────────────

LIST_PASS = [
    ("int list",            meta(list[int], "f"),       [1, 2, 3],              [1, 2, 3]),
    ("str list",            meta(list[str], "f"),       ["a", "b"],             ["a", "b"]),
    ("float list",          meta(list[float], "f"),     [1.0, 2.5],            [1.0, 2.5]),
    ("bool list",           meta(list[bool], "f"),      [True, False],          [True, False]),
    ("date list",           meta(list[date], "f"),      [date(2024, 1, 1)],     [date(2024, 1, 1)]),
    ("enum list",           meta(list[Color], "f"),     [Color.RED],            [Color.RED]),
    ("tuple input",         meta(list[int], "f"),       (1, 2),                 [1, 2]),
]

LIST_COERCE = [
    ("str→int list",        meta(list[int], "f"),       ["1", "2", "3"],        [1, 2, 3]),
    ("str→float list",      meta(list[float], "f"),     ["1.5", "2.5"],         [1.5, 2.5]),
    ("str→date list",       meta(list[date], "f"),      ["2024-01-01"],         [date(2024, 1, 1)]),
    ("str→enum list",       meta(list[Color], "f"),     ["red", "blue"],        [Color.RED, Color.BLUE]),
    ("int→float list",      meta(list[float], "f"),     [1, 2],                 [1.0, 2.0]),
    ("enum name list",      meta(list[Color], "f"),     ["RED", "GREEN"],       [Color.RED, Color.GREEN]),
]

LIST_FAIL = [
    ("empty list",          meta(list[int], "f"),       [],             ValueError),
    ("not a list",          meta(list[int], "f"),       "hello",        TypeError),
    ("not a list int",      meta(list[int], "f"),       42,             TypeError),
    ("bad item in list",    meta(list[int], "f"),       [1, "abc", 3],  TypeError),
]

@pytest.mark.parametrize("label,m,value,expected", LIST_PASS, ids=[x[0] for x in LIST_PASS])
def test_list_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,expected", LIST_COERCE, ids=[x[0] for x in LIST_COERCE])
def test_list_coerce(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LIST_FAIL, ids=[x[0] for x in LIST_FAIL])
def test_list_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Lists: constraints ─────────────────────────────────────────────

LIST_CONSTRAINED_PASS = [
    ("int list constrained items",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=10)]], Field(min_length=1, max_length=3)], "f"),
        [1, 5, 10], [1, 5, 10]),
    ("int list min items",
        meta(Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)], "f"),
        [0, 1], [0, 1]),
]

LIST_CONSTRAINED_FAIL = [
    ("list too short",
        meta(Annotated[list[int], Field(min_length=2, max_length=5)], "f"),
        [1], ValueError),
    ("list too long",
        meta(Annotated[list[int], Field(min_length=1, max_length=2)], "f"),
        [1, 2, 3], ValueError),
    ("list item out of range",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=10)]], Field(min_length=1)], "f"),
        [5, 99], ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LIST_CONSTRAINED_PASS, ids=[x[0] for x in LIST_CONSTRAINED_PASS])
def test_list_constrained_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LIST_CONSTRAINED_FAIL, ids=[x[0] for x in LIST_CONSTRAINED_FAIL])
def test_list_constrained_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Lists: enum choices ────────────────────────────────────────────

LIST_ENUM_PASS = [
    ("enum list native",    meta(list[Color], "f"),     [Color.RED, Color.BLUE],    [Color.RED, Color.BLUE]),
    ("enum list by value",  meta(list[Color], "f"),     ["red", "blue"],            [Color.RED, Color.BLUE]),
    ("enum list by name",   meta(list[Color], "f"),     ["RED", "GREEN"],           [Color.RED, Color.GREEN]),
    ("enum list mixed",     meta(list[Color], "f"),     [Color.RED, "blue"],        [Color.RED, Color.BLUE]),
    ("int enum list",       meta(list[Priority], "f"),  [1, 3],                     [Priority.LOW, Priority.HIGH]),
]

LIST_ENUM_FAIL = [
    ("enum list bad value", meta(list[Color], "f"),     ["red", "yellow"],  ValueError),
    ("int enum bad value",  meta(list[Priority], "f"),  [1, 99],            ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LIST_ENUM_PASS, ids=[x[0] for x in LIST_ENUM_PASS])
def test_list_enum_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LIST_ENUM_FAIL, ids=[x[0] for x in LIST_ENUM_FAIL])
def test_list_enum_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ─── Optional + None in lists ───────────────────────────────────────

OPTIONAL_LIST = [
    ("optional list none",          meta(list[int] | None, "f"),    None,       None),
    ("optional list with values",   meta(list[int] | None, "f"),    [1, 2],     [1, 2]),
    ("optional enum list none",     meta(list[Color] | None, "f"),  None,       None),
]

@pytest.mark.parametrize("label,m,value,expected", OPTIONAL_LIST, ids=[x[0] for x in OPTIONAL_LIST])
def test_optional_list(label, m, value, expected):
    assert validate_value(m, value) == expected


# ─── Edge cases ──────────────────────────────────────────────────────

EDGE_CASES = [
    ("int zero",            meta(int, "f"),     0,          0),
    ("float zero",          meta(float, "f"),   0.0,        0.0),
    ("bool false",          meta(bool, "f"),    False,      False),
    ("str single char",     meta(str, "f"),     "x",        "x"),
    ("str with spaces",     meta(str, "f"),     "  hi  ",   "  hi  "),
    ("very large int",      meta(int, "f"),     999999999,  999999999),
    ("negative int",        meta(int, "f"),     -42,        -42),
    ("negative float",      meta(float, "f"),   -3.14,      -3.14),
    ("str negative int",    meta(int, "f"),     "-42",      -42),
    ("str negative float",  meta(float, "f"),   "-3.14",    -3.14),
    ("date min",            meta(date, "f"),    "0001-01-01", date(1, 1, 1)),
    ("time midnight",       meta(time, "f"),    "00:00:00", time(0, 0, 0)),
    ("time end of day",     meta(time, "f"),    "23:59:59", time(23, 59, 59)),
    ("single item list",    meta(list[int], "f"), [42],     [42]),
]

@pytest.mark.parametrize("label,m,value,expected", EDGE_CASES, ids=[x[0] for x in EDGE_CASES])
def test_edge_cases(label, m, value, expected):
    assert validate_value(m, value) == expected
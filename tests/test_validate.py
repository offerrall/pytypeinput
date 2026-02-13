import pytest
import inspect
from typing import Annotated, Literal
from datetime import date, time
from enum import Enum

from pydantic import Field

from pytypeinput import analyze_type
from pytypeinput.validate import validate_value
from pytypeinput.types import (
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File,
    Step, Slider, Dropdown, Placeholder, IsPassword,
    Label, Description, Rows,
    OptionalEnabled, OptionalDisabled,
)


# ─── Enums ───────────────────────────────────────────────────────────

class StrEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

class IntEnum(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class SingleEnum(Enum):
    ONLY = "only"

class BoolEnum(Enum):
    ON = True
    OFF = False


# ─── Helpers ─────────────────────────────────────────────────────────

def meta(annotation, name="field", default=...):
    if default is ...:
        default = inspect.Parameter.empty
    return analyze_type(annotation, name, default)


# ═══════════════════════════════════════════════════════════════════════
# None handling
# ═══════════════════════════════════════════════════════════════════════

NONE_PASS = [
    ("optional str",                meta(str | None, "f"),                              None, None),
    ("optional int",                meta(int | None, "f"),                              None, None),
    ("optional float",              meta(float | None, "f"),                            None, None),
    ("optional bool",               meta(bool | None, "f"),                             None, None),
    ("optional date",               meta(date | None, "f"),                             None, None),
    ("optional time",               meta(time | None, "f"),                             None, None),
    ("optional str enum",           meta(StrEnum | None, "f"),                          None, None),
    ("optional int enum",           meta(IntEnum | None, "f"),                          None, None),
    ("optional list[int]",          meta(list[int] | None, "f"),                        None, None),
    ("optional list[str]",          meta(list[str] | None, "f"),                        None, None),
    ("optional list[enum]",         meta(list[StrEnum] | None, "f"),                    None, None),
    ("optional literal str",        meta(Literal["a", "b"] | None, "f"),                None, None),
    ("optional literal int",        meta(Literal[1, 2] | None, "f"),                    None, None),
    ("optional constrained int",    meta(Annotated[int, Field(ge=0)] | None, "f"),      None, None),
    ("optional constrained str",    meta(Annotated[str, Field(min_length=1)] | None, "f"), None, None),
    ("optional color",              meta(Color | None, "f"),                             None, None),
    ("optional email",              meta(Email | None, "f"),                             None, None),
    ("optional file",               meta(File | None, "f"),                              None, None),
    ("optional with default none",  meta(str | None, "f", default=None),                None, None),
]

NONE_FAIL = [
    ("required str",                meta(str, "f")),
    ("required int",                meta(int, "f")),
    ("required float",              meta(float, "f")),
    ("required bool",               meta(bool, "f")),
    ("required date",               meta(date, "f")),
    ("required time",               meta(time, "f")),
    ("required str enum",           meta(StrEnum, "f")),
    ("required int enum",           meta(IntEnum, "f")),
    ("required literal",            meta(Literal["a", "b"], "f")),
    ("required constrained int",    meta(Annotated[int, Field(ge=0)], "f")),
    ("required color",              meta(Color, "f")),
    ("required email",              meta(Email, "f")),
    ("required file",               meta(File, "f")),
    ("required list",               meta(list[int], "f")),
]

@pytest.mark.parametrize("label,m,value,expected", NONE_PASS, ids=[x[0] for x in NONE_PASS])
def test_none_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m", NONE_FAIL, ids=[x[0] for x in NONE_FAIL])
def test_none_fail(label, m):
    with pytest.raises(ValueError):
        validate_value(m, None)


# ═══════════════════════════════════════════════════════════════════════
# Python native values (passthrough)
# ═══════════════════════════════════════════════════════════════════════

PYTHON_NATIVE = [
    ("str hello",               meta(str, "f"),             "hello",                "hello"),
    ("str unicode",             meta(str, "f"),             "héllo 🌍",             "héllo 🌍"),
    ("str special chars",       meta(str, "f"),             "<script>alert</script>","<script>alert</script>"),
    ("str very long",           meta(str, "f"),             "x" * 10000,            "x" * 10000),
    ("int positive",            meta(int, "f"),             42,                     42),
    ("int zero",                meta(int, "f"),             0,                      0),
    ("int negative",            meta(int, "f"),             -42,                    -42),
    ("int very large",          meta(int, "f"),             10**18,                 10**18),
    ("int very negative",       meta(int, "f"),             -(10**18),              -(10**18)),
    ("float positive",          meta(float, "f"),           3.14,                   3.14),
    ("float zero",              meta(float, "f"),           0.0,                    0.0),
    ("float negative",          meta(float, "f"),           -3.14,                  -3.14),
    ("float very small",        meta(float, "f"),           0.000001,               0.000001),
    ("float very large",        meta(float, "f"),           1e15,                   1e15),
    ("bool true",               meta(bool, "f"),            True,                   True),
    ("bool false",              meta(bool, "f"),            False,                  False),
    ("date normal",             meta(date, "f"),            date(2024, 1, 15),      date(2024, 1, 15)),
    ("date leap year",          meta(date, "f"),            date(2024, 2, 29),      date(2024, 2, 29)),
    ("date min",                meta(date, "f"),            date(1, 1, 1),          date(1, 1, 1)),
    ("time normal",             meta(time, "f"),            time(14, 30),           time(14, 30)),
    ("time with seconds",       meta(time, "f"),            time(14, 30, 45),       time(14, 30, 45)),
    ("time midnight",           meta(time, "f"),            time(0, 0, 0),          time(0, 0, 0)),
    ("time end of day",         meta(time, "f"),            time(23, 59, 59),       time(23, 59, 59)),
    ("str enum instance",       meta(StrEnum, "f"),         StrEnum.RED,            StrEnum.RED),
    ("str enum all members",    meta(StrEnum, "f"),         StrEnum.BLUE,           StrEnum.BLUE),
    ("int enum instance",       meta(IntEnum, "f"),         IntEnum.HIGH,           IntEnum.HIGH),
    ("int enum all members",    meta(IntEnum, "f"),         IntEnum.LOW,            IntEnum.LOW),
    ("single enum",             meta(SingleEnum, "f"),      SingleEnum.ONLY,        SingleEnum.ONLY),
]

@pytest.mark.parametrize("label,m,value,expected", PYTHON_NATIVE, ids=[x[0] for x in PYTHON_NATIVE])
def test_python_native(label, m, value, expected):
    assert validate_value(m, value) == expected


# ═══════════════════════════════════════════════════════════════════════
# JSON/string coercion
# ═══════════════════════════════════════════════════════════════════════

JSON_COERCE = [
    # str → int
    ("str→int pos",             meta(int, "f"),         "42",           42),
    ("str→int neg",             meta(int, "f"),         "-7",           -7),
    ("str→int zero",            meta(int, "f"),         "0",            0),
    ("str→int large",           meta(int, "f"),         "999999999",    999999999),
    # str → float
    ("str→float pos",           meta(float, "f"),       "3.14",         3.14),
    ("str→float neg",           meta(float, "f"),       "-0.5",         -0.5),
    ("str→float zero",          meta(float, "f"),       "0.0",          0.0),
    ("str→float int-like",      meta(float, "f"),       "3",            3.0),
    ("str→float sci",           meta(float, "f"),       "1e5",          1e5),
    # str → bool
    ("str→bool true",           meta(bool, "f"),        "true",         True),
    ("str→bool false",          meta(bool, "f"),        "false",        False),
    ("str→bool TRUE",           meta(bool, "f"),        "TRUE",         True),
    ("str→bool FALSE",          meta(bool, "f"),        "FALSE",        False),
    ("str→bool True",           meta(bool, "f"),        "True",         True),
    ("str→bool False",          meta(bool, "f"),        "False",        False),
    ("str→bool 1",              meta(bool, "f"),        "1",            True),
    ("str→bool 0",              meta(bool, "f"),        "0",            False),
    ("str→bool yes",            meta(bool, "f"),        "yes",          True),
    ("str→bool no",             meta(bool, "f"),        "no",           False),
    ("str→bool YES",            meta(bool, "f"),        "YES",          True),
    ("str→bool NO",             meta(bool, "f"),        "NO",           False),
    # str → date
    ("str→date normal",         meta(date, "f"),        "2024-01-15",   date(2024, 1, 15)),
    ("str→date leap",           meta(date, "f"),        "2024-02-29",   date(2024, 2, 29)),
    ("str→date min",            meta(date, "f"),        "0001-01-01",   date(1, 1, 1)),
    # str → time
    ("str→time full",           meta(time, "f"),        "14:30:00",     time(14, 30)),
    ("str→time short",          meta(time, "f"),        "08:00",        time(8, 0)),
    ("str→time midnight",       meta(time, "f"),        "00:00:00",     time(0, 0, 0)),
    ("str→time end",            meta(time, "f"),        "23:59:59",     time(23, 59, 59)),
    ("str→time seconds",        meta(time, "f"),        "12:34:56",     time(12, 34, 56)),
    # float → int (exact)
    ("float→int exact pos",     meta(int, "f"),         42.0,           42),
    ("float→int exact zero",    meta(int, "f"),         0.0,            0),
    ("float→int exact neg",     meta(int, "f"),         -5.0,           -5),
    # int → float
    ("int→float pos",           meta(float, "f"),       3,              3.0),
    ("int→float zero",          meta(float, "f"),       0,              0.0),
    ("int→float neg",           meta(float, "f"),       -10,            -10.0),
    # numeric → bool
    ("int 1→bool",              meta(bool, "f"),        1,              True),
    ("int 0→bool",              meta(bool, "f"),        0,              False),
    ("int 42→bool",             meta(bool, "f"),        42,             True),
    ("int -1→bool",             meta(bool, "f"),        -1,             True),
    ("float 1.0→bool",          meta(bool, "f"),        1.0,            True),
    ("float 0.0→bool",          meta(bool, "f"),        0.0,            False),
    # enum coercion
    ("strenum by value",        meta(StrEnum, "f"),     "red",          StrEnum.RED),
    ("strenum by value 2",      meta(StrEnum, "f"),     "green",        StrEnum.GREEN),
    ("strenum by name",         meta(StrEnum, "f"),     "BLUE",         StrEnum.BLUE),
    ("strenum by name 2",       meta(StrEnum, "f"),     "RED",          StrEnum.RED),
    ("intenum by value",        meta(IntEnum, "f"),     1,              IntEnum.LOW),
    ("intenum by value 2",      meta(IntEnum, "f"),     3,              IntEnum.HIGH),
    ("intenum by name",         meta(IntEnum, "f"),     "MEDIUM",       IntEnum.MEDIUM),
    ("singleenum by value",     meta(SingleEnum, "f"),  "only",         SingleEnum.ONLY),
    ("singleenum by name",      meta(SingleEnum, "f"),  "ONLY",         SingleEnum.ONLY),
]

@pytest.mark.parametrize("label,m,value,expected", JSON_COERCE, ids=[x[0] for x in JSON_COERCE])
def test_json_coerce(label, m, value, expected):
    assert validate_value(m, value) == expected


# ═══════════════════════════════════════════════════════════════════════
# Coercion failures
# ═══════════════════════════════════════════════════════════════════════

COERCE_FAIL = [
    # bool → numeric (rejected)
    ("bool True→int",           meta(int, "f"),         True,           TypeError),
    ("bool False→int",          meta(int, "f"),         False,          TypeError),
    ("bool True→float",         meta(float, "f"),       True,           TypeError),
    ("bool False→float",        meta(float, "f"),       False,          TypeError),
    # bad str → numeric
    ("str abc→int",             meta(int, "f"),         "abc",          TypeError),
    ("str empty→int",           meta(int, "f"),         "",             TypeError),
    ("str space→int",           meta(int, "f"),         " ",            TypeError),
    ("str abc→float",           meta(float, "f"),       "abc",          TypeError),
    ("str empty→float",         meta(float, "f"),       "",             TypeError),
    # bad str → bool
    ("str maybe→bool",          meta(bool, "f"),        "maybe",        TypeError),
    ("str 2→bool",              meta(bool, "f"),        "2",            TypeError),
    ("str empty→bool",          meta(bool, "f"),        "",             TypeError),
    # bad str → date
    ("str bad→date",            meta(date, "f"),        "not-date",     ValueError),
    ("str slash→date",          meta(date, "f"),        "15/01/2024",   ValueError),
    ("str month13→date",        meta(date, "f"),        "2024-13-01",   ValueError),
    ("str day32→date",          meta(date, "f"),        "2024-01-32",   ValueError),
    ("str partial→date",        meta(date, "f"),        "2024-01",      ValueError),
    ("str noleap→date",         meta(date, "f"),        "2023-02-29",   ValueError),
    # bad str → time
    ("str bad→time",            meta(time, "f"),        "not-time",     ValueError),
    ("str 25h→time",            meta(time, "f"),        "25:00:00",     ValueError),
    ("str 60m→time",            meta(time, "f"),        "12:60:00",     ValueError),
    # wrong type → str
    ("int→str",                 meta(str, "f"),         42,             TypeError),
    ("float→str",               meta(str, "f"),         3.14,           TypeError),
    ("bool→str",                meta(str, "f"),         True,           TypeError),
    ("list→str",                meta(str, "f"),         [1, 2],         TypeError),
    ("dict→str",                meta(str, "f"),         {},             TypeError),
    ("none→str",                meta(str, "f"),         None,           ValueError),
    ("bytes→str",               meta(str, "f"),         b"hello",       TypeError),
    # wrong type → int
    ("dict→int",                meta(int, "f"),         {},             TypeError),
    ("list→int",                meta(int, "f"),         [1],            TypeError),
    ("bytes→int",               meta(int, "f"),         b"1",           TypeError),
    # fractional float → int (rejected)
    ("float 3.7→int",           meta(int, "f"),         3.7,            TypeError),
    ("float -1.5→int",          meta(int, "f"),         -1.5,           TypeError),
    ("float 0.1→int",           meta(int, "f"),         0.1,            TypeError),
    # wrong type → date/time
    ("int→date",                meta(date, "f"),        20240115,       TypeError),
    ("int→time",                meta(time, "f"),        1430,           TypeError),
    ("float→date",              meta(date, "f"),        2024.01,        TypeError),
    ("list→date",               meta(date, "f"),        [2024, 1, 1],   TypeError),
    # enum failures
    ("strenum bad value",       meta(StrEnum, "f"),     "yellow",       ValueError),
    ("strenum bad int",         meta(StrEnum, "f"),     123,            ValueError),
    ("strenum empty",           meta(StrEnum, "f"),     "",             ValueError),
    ("intenum bad value",       meta(IntEnum, "f"),     99,             ValueError),
    ("intenum bad str",         meta(IntEnum, "f"),     "invalid",      ValueError),
    ("intenum float",           meta(IntEnum, "f"),     1.5,            ValueError),
    # wrong container → list
    ("set→list",                meta(list[int], "f"),   {1, 2},         TypeError),
    ("dict→list",               meta(list[int], "f"),   {"a": 1},       TypeError),
    ("str→list",                meta(list[int], "f"),   "hello",        TypeError),
    ("int→list",                meta(list[int], "f"),   42,             TypeError),
]

@pytest.mark.parametrize("label,m,value,exc", COERCE_FAIL, ids=[x[0] for x in COERCE_FAIL])
def test_coerce_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Empty string on required str
# ═══════════════════════════════════════════════════════════════════════

EMPTY_STR = [
    ("empty",               meta(str, "f"),         "",             ValueError),
    ("space",               meta(str, "f"),         " ",            ValueError),
    ("spaces",              meta(str, "f"),         "   ",          ValueError),
    ("tab",                 meta(str, "f"),         "\t",           ValueError),
    ("newline",             meta(str, "f"),         "\n",           ValueError),
    ("carriage return",     meta(str, "f"),         "\r",           ValueError),
    ("mixed whitespace",    meta(str, "f"),         " \t\n\r ",     ValueError),
    ("tab newline",         meta(str, "f"),         "\t\n",         ValueError),
]

@pytest.mark.parametrize("label,m,value,exc", EMPTY_STR, ids=[x[0] for x in EMPTY_STR])
def test_empty_str_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Numeric constraints
# ═══════════════════════════════════════════════════════════════════════

CONSTRAINTS_NUM_PASS = [
    # ge / le
    ("int ge/le mid",           meta(Annotated[int, Field(ge=0, le=100)], "f"),             50,     50),
    ("int ge/le at min",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             0,      0),
    ("int ge/le at max",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             100,    100),
    ("int ge only",             meta(Annotated[int, Field(ge=10)], "f"),                    10,     10),
    ("int ge large",            meta(Annotated[int, Field(ge=10)], "f"),                    9999,   9999),
    ("int le only",             meta(Annotated[int, Field(le=50)], "f"),                    -100,   -100),
    ("int le at max",           meta(Annotated[int, Field(le=50)], "f"),                    50,     50),
    # gt / lt
    ("int gt/lt mid",           meta(Annotated[int, Field(gt=0, lt=10)], "f"),              5,      5),
    ("int gt just above",       meta(Annotated[int, Field(gt=0, lt=10)], "f"),              1,      1),
    ("int lt just below",       meta(Annotated[int, Field(gt=0, lt=10)], "f"),              9,      9),
    # float
    ("float gt/lt mid",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         0.5,    0.5),
    ("float gt near zero",      meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         0.001,  0.001),
    ("float lt near one",       meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         0.999,  0.999),
    ("float ge/le negative",    meta(Annotated[float, Field(ge=-10.0, le=-1.0)], "f"),      -5.0,   -5.0),
    ("float ge/le at min",      meta(Annotated[float, Field(ge=-10.0, le=-1.0)], "f"),      -10.0,  -10.0),
    ("float ge/le at max",      meta(Annotated[float, Field(ge=-10.0, le=-1.0)], "f"),      -1.0,   -1.0),
    # coerced from string
    ("str→int constrained",     meta(Annotated[int, Field(ge=0, le=100)], "f"),             "50",   50),
    ("str→float constrained",   meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         "0.5",  0.5),
    ("str→int at boundary",     meta(Annotated[int, Field(ge=0, le=100)], "f"),             "0",    0),
]

CONSTRAINTS_NUM_FAIL = [
    # ge / le
    ("int below ge",            meta(Annotated[int, Field(ge=0, le=100)], "f"),             -1,     ValueError),
    ("int above le",            meta(Annotated[int, Field(ge=0, le=100)], "f"),             101,    ValueError),
    ("int way below ge",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             -9999,  ValueError),
    ("int way above le",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             9999,   ValueError),
    # gt / lt (boundary exclusive)
    ("int at gt",               meta(Annotated[int, Field(gt=0, lt=10)], "f"),              0,      ValueError),
    ("int at lt",               meta(Annotated[int, Field(gt=0, lt=10)], "f"),              10,     ValueError),
    # float
    ("float at gt",             meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         0.0,    ValueError),
    ("float at lt",             meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         1.0,    ValueError),
    ("float below ge",          meta(Annotated[float, Field(ge=-10.0, le=-1.0)], "f"),      -10.001,ValueError),
    ("float above le",          meta(Annotated[float, Field(ge=-10.0, le=-1.0)], "f"),      -0.999, ValueError),
    # coerced from string
    ("str→int below ge",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             "-1",   ValueError),
    ("str→int above le",        meta(Annotated[int, Field(ge=0, le=100)], "f"),             "101",  ValueError),
    ("str→float at gt",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         "0.0",  ValueError),
    ("str→float at lt",         meta(Annotated[float, Field(gt=0.0, lt=1.0)], "f"),         "1.0",  ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", CONSTRAINTS_NUM_PASS, ids=[x[0] for x in CONSTRAINTS_NUM_PASS])
def test_constraints_num_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", CONSTRAINTS_NUM_FAIL, ids=[x[0] for x in CONSTRAINTS_NUM_FAIL])
def test_constraints_num_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# String constraints
# ═══════════════════════════════════════════════════════════════════════

CONSTRAINTS_STR_PASS = [
    ("min/max mid",         meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "abc",      "abc"),
    ("min/max at min",      meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "ab",       "ab"),
    ("min/max at max",      meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "abcde",    "abcde"),
    ("min only",            meta(Annotated[str, Field(min_length=1)], "f"),                 "x",        "x"),
    ("max only",            meta(Annotated[str, Field(max_length=100)], "f"),               "hello",    "hello"),
    ("pattern digits",      meta(Annotated[str, Field(pattern=r"^\d{3}$")], "f"),           "123",      "123"),
    ("pattern alpha",       meta(Annotated[str, Field(pattern=r"^[a-z]+$")], "f"),          "hello",    "hello"),
    ("pattern mixed",       meta(Annotated[str, Field(pattern=r"^[A-Z]\d+$")], "f"),        "A123",     "A123"),
    ("color #fff",          meta(Color, "f"),                                               "#fff",     "#fff"),
    ("color #000000",       meta(Color, "f"),                                               "#000000",  "#000000"),
    ("color #ABCDEF",       meta(Color, "f"),                                               "#ABCDEF",  "#ABCDEF"),
    ("color #aAbBcC",       meta(Color, "f"),                                               "#aAbBcC",  "#aAbBcC"),
    ("email simple",        meta(Email, "f"),                                               "a@b.com",  "a@b.com"),
    ("email complex",       meta(Email, "f"),                                               "user.name+tag@example.co.uk", "user.name+tag@example.co.uk"),
    ("email digits",        meta(Email, "f"),                                               "123@456.com", "123@456.com"),
    ("email percent",       meta(Email, "f"),                                               "a%b@c.com","a%b@c.com"),
]

CONSTRAINTS_STR_FAIL = [
    ("too short",           meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "a",        ValueError),
    ("too long",            meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "abcdef",   ValueError),
    ("way too long",        meta(Annotated[str, Field(min_length=2, max_length=5)], "f"),   "x" * 100,  ValueError),
    ("bad digits",          meta(Annotated[str, Field(pattern=r"^\d{3}$")], "f"),           "12",       ValueError),
    ("bad digits 4",        meta(Annotated[str, Field(pattern=r"^\d{3}$")], "f"),           "1234",     ValueError),
    ("bad alpha upper",     meta(Annotated[str, Field(pattern=r"^[a-z]+$")], "f"),          "Hello",    ValueError),
    ("bad alpha digits",    meta(Annotated[str, Field(pattern=r"^[a-z]+$")], "f"),          "abc123",   ValueError),
    ("color no hash",       meta(Color, "f"),                                               "ff0000",   ValueError),
    ("color word",          meta(Color, "f"),                                               "red",      ValueError),
    ("color bad chars",     meta(Color, "f"),                                               "#gggggg",  ValueError),
    ("color too long",      meta(Color, "f"),                                               "#1234567", ValueError),
    ("color 4 chars",       meta(Color, "f"),                                               "#abcd",    ValueError),
    ("email no at",         meta(Email, "f"),                                               "invalid",  ValueError),
    ("email no domain",     meta(Email, "f"),                                               "a@",       ValueError),
    ("email no user",       meta(Email, "f"),                                               "@b.com",   ValueError),
    ("email double at",     meta(Email, "f"),                                               "a@@b.com", ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", CONSTRAINTS_STR_PASS, ids=[x[0] for x in CONSTRAINTS_STR_PASS])
def test_constraints_str_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", CONSTRAINTS_STR_FAIL, ids=[x[0] for x in CONSTRAINTS_STR_FAIL])
def test_constraints_str_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# File type patterns
# ═══════════════════════════════════════════════════════════════════════

FILE_PASS = [
    ("image png",           meta(ImageFile, "f"),       "photo.png",        "photo.png"),
    ("image jpg",           meta(ImageFile, "f"),       "photo.jpg",        "photo.jpg"),
    ("image jpeg",          meta(ImageFile, "f"),       "a.jpeg",           "a.jpeg"),
    ("image gif",           meta(ImageFile, "f"),       "anim.gif",         "anim.gif"),
    ("image webp",          meta(ImageFile, "f"),       "x.webp",           "x.webp"),
    ("image svg",           meta(ImageFile, "f"),       "icon.svg",         "icon.svg"),
    ("image uppercase",     meta(ImageFile, "f"),       "PHOTO.PNG",        "PHOTO.PNG"),
    ("image mixed case",    meta(ImageFile, "f"),       "Photo.Jpg",        "Photo.Jpg"),
    ("video mp4",           meta(VideoFile, "f"),       "video.mp4",        "video.mp4"),
    ("video mov",           meta(VideoFile, "f"),       "clip.mov",         "clip.mov"),
    ("video mkv",           meta(VideoFile, "f"),       "film.mkv",         "film.mkv"),
    ("audio mp3",           meta(AudioFile, "f"),       "song.mp3",         "song.mp3"),
    ("audio wav",           meta(AudioFile, "f"),       "sound.wav",        "sound.wav"),
    ("audio flac",          meta(AudioFile, "f"),       "music.flac",       "music.flac"),
    ("data csv",            meta(DataFile, "f"),        "data.csv",         "data.csv"),
    ("data json",           meta(DataFile, "f"),        "config.json",      "config.json"),
    ("data xlsx",           meta(DataFile, "f"),        "sheet.xlsx",       "sheet.xlsx"),
    ("data yaml",           meta(DataFile, "f"),        "config.yaml",      "config.yaml"),
    ("text txt",            meta(TextFile, "f"),        "readme.txt",       "readme.txt"),
    ("text md",             meta(TextFile, "f"),        "notes.md",         "notes.md"),
    ("text log",            meta(TextFile, "f"),        "app.log",          "app.log"),
    ("doc pdf",             meta(DocumentFile, "f"),    "report.pdf",       "report.pdf"),
    ("doc docx",            meta(DocumentFile, "f"),    "letter.docx",      "letter.docx"),
    ("doc pptx",            meta(DocumentFile, "f"),    "slides.pptx",      "slides.pptx"),
    ("any file",            meta(File, "f"),            "anything.xyz",     "anything.xyz"),
    ("any file no ext",     meta(File, "f"),            "makefile",         "makefile"),
    ("any file dotfile",    meta(File, "f"),            ".gitignore",       ".gitignore"),
    ("any file path",       meta(File, "f"),            "path/to/file.txt", "path/to/file.txt"),
]

FILE_FAIL = [
    ("image bad ext",       meta(ImageFile, "f"),       "photo.txt",    ValueError),
    ("image no ext",        meta(ImageFile, "f"),       "photo",        ValueError),
    ("video bad ext",       meta(VideoFile, "f"),       "video.png",    ValueError),
    ("audio bad ext",       meta(AudioFile, "f"),       "song.mp4",     ValueError),
    ("data bad ext",        meta(DataFile, "f"),        "data.txt",     ValueError),
    ("text bad ext",        meta(TextFile, "f"),        "file.pdf",     ValueError),
    ("doc bad ext",         meta(DocumentFile, "f"),    "file.txt",     ValueError),
    ("image empty",         meta(ImageFile, "f"),       "",             ValueError),
    ("video empty",         meta(VideoFile, "f"),       "",             ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", FILE_PASS, ids=[x[0] for x in FILE_PASS])
def test_file_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", FILE_FAIL, ids=[x[0] for x in FILE_FAIL])
def test_file_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Enum choices
# ═══════════════════════════════════════════════════════════════════════

ENUM_PASS = [
    ("strenum inst all",        meta(StrEnum, "f"),         StrEnum.RED,        StrEnum.RED),
    ("strenum inst green",      meta(StrEnum, "f"),         StrEnum.GREEN,      StrEnum.GREEN),
    ("strenum inst blue",       meta(StrEnum, "f"),         StrEnum.BLUE,       StrEnum.BLUE),
    ("strenum by value",        meta(StrEnum, "f"),         "red",              StrEnum.RED),
    ("strenum by value green",  meta(StrEnum, "f"),         "green",            StrEnum.GREEN),
    ("strenum by name",         meta(StrEnum, "f"),         "RED",              StrEnum.RED),
    ("strenum by name green",   meta(StrEnum, "f"),         "GREEN",            StrEnum.GREEN),
    ("intenum inst",            meta(IntEnum, "f"),         IntEnum.LOW,        IntEnum.LOW),
    ("intenum by value 1",      meta(IntEnum, "f"),         1,                  IntEnum.LOW),
    ("intenum by value 2",      meta(IntEnum, "f"),         2,                  IntEnum.MEDIUM),
    ("intenum by value 3",      meta(IntEnum, "f"),         3,                  IntEnum.HIGH),
    ("intenum by name",         meta(IntEnum, "f"),         "HIGH",             IntEnum.HIGH),
    ("singleenum inst",         meta(SingleEnum, "f"),      SingleEnum.ONLY,    SingleEnum.ONLY),
    ("singleenum by value",     meta(SingleEnum, "f"),      "only",             SingleEnum.ONLY),
    ("singleenum by name",      meta(SingleEnum, "f"),      "ONLY",             SingleEnum.ONLY),
]

ENUM_FAIL = [
    ("strenum bad value",       meta(StrEnum, "f"),         "purple",       ValueError),
    ("strenum bad int",         meta(StrEnum, "f"),         123,            ValueError),
    ("strenum empty",           meta(StrEnum, "f"),         "",             ValueError),
    ("strenum wrong enum",      meta(StrEnum, "f"),         IntEnum.LOW,    ValueError),
    ("intenum bad value",       meta(IntEnum, "f"),         99,             ValueError),
    ("intenum bad value 0",     meta(IntEnum, "f"),         0,              ValueError),
    ("intenum bad str",         meta(IntEnum, "f"),         "invalid",      ValueError),
    ("intenum float",           meta(IntEnum, "f"),         1.5,            ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", ENUM_PASS, ids=[x[0] for x in ENUM_PASS])
def test_enum_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", ENUM_FAIL, ids=[x[0] for x in ENUM_FAIL])
def test_enum_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Literal choices
# ═══════════════════════════════════════════════════════════════════════

LITERAL_PASS = [
    ("str a",               meta(Literal["a", "b", "c"], "f"),      "a",    "a"),
    ("str b",               meta(Literal["a", "b", "c"], "f"),      "b",    "b"),
    ("str c",               meta(Literal["a", "b", "c"], "f"),      "c",    "c"),
    ("int 1",               meta(Literal[1, 2, 3], "f"),            1,      1),
    ("int 2",               meta(Literal[1, 2, 3], "f"),            2,      2),
    ("int 3",               meta(Literal[1, 2, 3], "f"),            3,      3),
    ("single option",       meta(Literal["only"], "f"),             "only", "only"),
    ("bool true",           meta(Literal[True, False], "f"),        True,   True),
    ("bool false",          meta(Literal[True, False], "f"),        False,  False),
]

LITERAL_FAIL = [
    ("str not in set",      meta(Literal["a", "b", "c"], "f"),      "z",    ValueError),
    ("int not in set",      meta(Literal[1, 2, 3], "f"),            9,      ValueError),
    ("case sensitive",      meta(Literal["abc"], "f"),              "ABC",  ValueError),
    ("extra spaces",        meta(Literal["abc"], "f"),              " abc", ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LITERAL_PASS, ids=[x[0] for x in LITERAL_PASS])
def test_literal_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LITERAL_FAIL, ids=[x[0] for x in LITERAL_FAIL])
def test_literal_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Dropdown (dynamic choices) — NOT validated against options
# ═══════════════════════════════════════════════════════════════════════

def _get_fruits():
    return ["apple", "banana", "cherry"]

DROPDOWN_PASS = [
    ("in options",          meta(Annotated[str, Dropdown(_get_fruits)], "f"),    "apple",    "apple"),
    ("in options 2",        meta(Annotated[str, Dropdown(_get_fruits)], "f"),    "banana",   "banana"),
    ("NOT in options ok",   meta(Annotated[str, Dropdown(_get_fruits)], "f"),    "mango",    "mango"),
    ("any string ok",       meta(Annotated[str, Dropdown(_get_fruits)], "f"),    "xyz",      "xyz"),
]

@pytest.mark.parametrize("label,m,value,expected", DROPDOWN_PASS, ids=[x[0] for x in DROPDOWN_PASS])
def test_dropdown_pass(label, m, value, expected):
    assert validate_value(m, value) == expected


# ═══════════════════════════════════════════════════════════════════════
# Lists — basic
# ═══════════════════════════════════════════════════════════════════════

LIST_PASS = [
    ("int list",            meta(list[int], "f"),           [1, 2, 3],              [1, 2, 3]),
    ("str list",            meta(list[str], "f"),           ["a", "b"],             ["a", "b"]),
    ("float list",          meta(list[float], "f"),         [1.0, 2.5],             [1.0, 2.5]),
    ("bool list",           meta(list[bool], "f"),          [True, False],          [True, False]),
    ("date list",           meta(list[date], "f"),          [date(2024, 1, 1)],     [date(2024, 1, 1)]),
    ("time list",           meta(list[time], "f"),          [time(8, 0)],           [time(8, 0)]),
    ("enum list",           meta(list[StrEnum], "f"),       [StrEnum.RED],          [StrEnum.RED]),
    ("tuple input",         meta(list[int], "f"),           (1, 2),                 [1, 2]),
    ("single item",         meta(list[int], "f"),           [42],                   [42]),
    ("many items",          meta(list[int], "f"),           list(range(50)),         list(range(50))),
]

LIST_COERCE = [
    ("str→int",             meta(list[int], "f"),           ["1", "2", "3"],        [1, 2, 3]),
    ("str→float",           meta(list[float], "f"),         ["1.5", "2.5"],         [1.5, 2.5]),
    ("str→date",            meta(list[date], "f"),          ["2024-01-01"],         [date(2024, 1, 1)]),
    ("str→time",            meta(list[time], "f"),          ["08:00", "14:30"],     [time(8, 0), time(14, 30)]),
    ("str→enum value",      meta(list[StrEnum], "f"),       ["red", "blue"],        [StrEnum.RED, StrEnum.BLUE]),
    ("str→enum name",       meta(list[StrEnum], "f"),       ["RED", "GREEN"],       [StrEnum.RED, StrEnum.GREEN]),
    ("int→float",           meta(list[float], "f"),         [1, 2],                 [1.0, 2.0]),
    ("mixed enum",          meta(list[StrEnum], "f"),       [StrEnum.RED, "blue"],  [StrEnum.RED, StrEnum.BLUE]),
    ("int enum values",     meta(list[IntEnum], "f"),       [1, 3],                 [IntEnum.LOW, IntEnum.HIGH]),
    ("str→bool",            meta(list[bool], "f"),          ["true", "false"],      [True, False]),
]

LIST_FAIL = [
    ("empty list",          meta(list[int], "f"),           [],             ValueError),
    ("not list str",        meta(list[int], "f"),           "hello",        TypeError),
    ("not list int",        meta(list[int], "f"),           42,             TypeError),
    ("not list dict",       meta(list[int], "f"),           {"a": 1},       TypeError),
    ("not list set",        meta(list[int], "f"),           {1, 2},         TypeError),
    ("bad item str→int",    meta(list[int], "f"),           [1, "abc", 3],  TypeError),
    ("bad item bool→int",   meta(list[int], "f"),           [1, True, 3],   TypeError),
    ("bad enum value",      meta(list[StrEnum], "f"),       ["red", "xyz"], ValueError),
    ("bad date str",        meta(list[date], "f"),          ["bad"],        ValueError),
    ("bad time str",        meta(list[time], "f"),          ["nope"],       ValueError),
    ("mixed types",         meta(list[int], "f"),           [1, 2.5, 3],    TypeError),
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


# ═══════════════════════════════════════════════════════════════════════
# Lists — constrained
# ═══════════════════════════════════════════════════════════════════════

LIST_CONSTR_PASS = [
    ("items+length ok",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=10)]], Field(min_length=1, max_length=3)], "f"),
        [1, 5, 10], [1, 5, 10]),
    ("min items exact",
        meta(Annotated[list[int], Field(min_length=2)], "f"),
        [0, 1], [0, 1]),
    ("max items exact",
        meta(Annotated[list[int], Field(min_length=1, max_length=2)], "f"),
        [1, 2], [1, 2]),
    ("coerced items",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=100)]], Field(min_length=1)], "f"),
        ["5", "10"], [5, 10]),
    ("float items constrained",
        meta(Annotated[list[Annotated[float, Field(ge=0.0, le=1.0)]], Field(min_length=1)], "f"),
        [0.0, 0.5, 1.0], [0.0, 0.5, 1.0]),
    ("str items constrained",
        meta(Annotated[list[Annotated[str, Field(min_length=1, max_length=5)]], Field(min_length=1)], "f"),
        ["hi", "bye"], ["hi", "bye"]),
]

LIST_CONSTR_FAIL = [
    ("too short",
        meta(Annotated[list[int], Field(min_length=2, max_length=5)], "f"),
        [1], ValueError),
    ("too long",
        meta(Annotated[list[int], Field(min_length=1, max_length=2)], "f"),
        [1, 2, 3], ValueError),
    ("item out of range",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=10)]], Field(min_length=1)], "f"),
        [5, 99], ValueError),
    ("item below ge",
        meta(Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=1)], "f"),
        [-1], ValueError),
    ("str item too long",
        meta(Annotated[list[Annotated[str, Field(max_length=3)]], Field(min_length=1)], "f"),
        ["abcd"], ValueError),
    ("float item at gt",
        meta(Annotated[list[Annotated[float, Field(gt=0.0)]], Field(min_length=1)], "f"),
        [0.0], ValueError),
    ("first item ok second bad",
        meta(Annotated[list[Annotated[int, Field(ge=0, le=10)]], Field(min_length=1)], "f"),
        [5, 11], ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LIST_CONSTR_PASS, ids=[x[0] for x in LIST_CONSTR_PASS])
def test_list_constr_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LIST_CONSTR_FAIL, ids=[x[0] for x in LIST_CONSTR_FAIL])
def test_list_constr_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Lists — enum choices
# ═══════════════════════════════════════════════════════════════════════

LIST_ENUM_PASS = [
    ("native instances",    meta(list[StrEnum], "f"),       [StrEnum.RED, StrEnum.BLUE],    [StrEnum.RED, StrEnum.BLUE]),
    ("by value",            meta(list[StrEnum], "f"),       ["red", "blue"],                [StrEnum.RED, StrEnum.BLUE]),
    ("by name",             meta(list[StrEnum], "f"),       ["RED", "GREEN"],               [StrEnum.RED, StrEnum.GREEN]),
    ("mixed inst+value",    meta(list[StrEnum], "f"),       [StrEnum.RED, "blue"],          [StrEnum.RED, StrEnum.BLUE]),
    ("int enum values",     meta(list[IntEnum], "f"),       [1, 3],                         [IntEnum.LOW, IntEnum.HIGH]),
    ("int enum names",      meta(list[IntEnum], "f"),       ["LOW", "HIGH"],                [IntEnum.LOW, IntEnum.HIGH]),
    ("int enum mixed",      meta(list[IntEnum], "f"),       [IntEnum.LOW, 3],               [IntEnum.LOW, IntEnum.HIGH]),
    ("all members",         meta(list[StrEnum], "f"),       ["red", "green", "blue"],       [StrEnum.RED, StrEnum.GREEN, StrEnum.BLUE]),
    ("single enum list",    meta(list[SingleEnum], "f"),    ["only"],                       [SingleEnum.ONLY]),
]

LIST_ENUM_FAIL = [
    ("bad value in list",   meta(list[StrEnum], "f"),       ["red", "yellow"],      ValueError),
    ("all bad values",      meta(list[StrEnum], "f"),       ["x", "y"],             ValueError),
    ("int enum bad value",  meta(list[IntEnum], "f"),       [1, 99],                ValueError),
    ("int enum bad all",    meta(list[IntEnum], "f"),       [99, 100],              ValueError),
    ("wrong enum type",     meta(list[StrEnum], "f"),       [IntEnum.LOW],          ValueError),
]

@pytest.mark.parametrize("label,m,value,expected", LIST_ENUM_PASS, ids=[x[0] for x in LIST_ENUM_PASS])
def test_list_enum_pass(label, m, value, expected):
    assert validate_value(m, value) == expected

@pytest.mark.parametrize("label,m,value,exc", LIST_ENUM_FAIL, ids=[x[0] for x in LIST_ENUM_FAIL])
def test_list_enum_fail(label, m, value, exc):
    with pytest.raises(exc):
        validate_value(m, value)


# ═══════════════════════════════════════════════════════════════════════
# Optional lists
# ═══════════════════════════════════════════════════════════════════════

OPTIONAL_LIST = [
    ("int list none",           meta(list[int] | None, "f"),            None,           None),
    ("int list values",         meta(list[int] | None, "f"),            [1, 2],         [1, 2]),
    ("str list none",           meta(list[str] | None, "f"),            None,           None),
    ("float list none",         meta(list[float] | None, "f"),          None,           None),
    ("date list none",          meta(list[date] | None, "f"),           None,           None),
    ("enum list none",          meta(list[StrEnum] | None, "f"),        None,           None),
    ("enum list values",        meta(list[StrEnum] | None, "f"),        ["red"],        [StrEnum.RED]),
    ("enum list coerce",        meta(list[StrEnum] | None, "f"),        ["RED"],        [StrEnum.RED]),
]

@pytest.mark.parametrize("label,m,value,expected", OPTIONAL_LIST, ids=[x[0] for x in OPTIONAL_LIST])
def test_optional_list(label, m, value, expected):
    assert validate_value(m, value) == expected


# ═══════════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════════

EDGE_CASES = [
    # Zero / falsy values that should be valid
    ("int zero",                meta(int, "f"),             0,              0),
    ("float zero",              meta(float, "f"),           0.0,            0.0),
    ("bool false",              meta(bool, "f"),            False,          False),
    # Strings
    ("str single char",         meta(str, "f"),             "x",            "x"),
    ("str with inner spaces",   meta(str, "f"),             "  hi  ",       "  hi  "),
    ("str newline in middle",   meta(str, "f"),             "a\nb",         "a\nb"),
    ("str unicode emoji",       meta(str, "f"),             "hello 🎉",     "hello 🎉"),
    ("str html-like",           meta(str, "f"),             "<b>bold</b>",  "<b>bold</b>"),
    ("str quotes",              meta(str, "f"),             'say "hi"',     'say "hi"'),
    # Large numbers
    ("very large int",          meta(int, "f"),             10**15,         10**15),
    ("very negative int",       meta(int, "f"),             -(10**15),      -(10**15)),
    ("very large float",        meta(float, "f"),           1e100,          1e100),
    ("very small float",        meta(float, "f"),           1e-100,         1e-100),
    # Boundary dates/times
    ("date min",                meta(date, "f"),            "0001-01-01",   date(1, 1, 1)),
    ("time midnight str",       meta(time, "f"),            "00:00:00",     time(0, 0, 0)),
    ("time end str",            meta(time, "f"),            "23:59:59",     time(23, 59, 59)),
    # Single item list
    ("single item list",        meta(list[int], "f"),       [42],           [42]),
    # Constrained + coerced
    ("str→int constrained",     meta(Annotated[int, Field(ge=0, le=100)], "f"),     "50",   50),
    # Optional with actual value
    ("optional str with val",   meta(str | None, "f"),      "hello",        "hello"),
    ("optional int with val",   meta(int | None, "f"),      42,             42),
    ("optional bool with val",  meta(bool | None, "f"),     False,          False),
    ("optional enum with val",  meta(StrEnum | None, "f"),  "red",          StrEnum.RED),
    ("optional list with val",  meta(list[int] | None, "f"),[1],            [1]),
]

@pytest.mark.parametrize("label,m,value,expected", EDGE_CASES, ids=[x[0] for x in EDGE_CASES])
def test_edge_cases(label, m, value, expected):
    assert validate_value(m, value) == expected
import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.normalize_default_10 import normalize_default
from pytypeinput.param import ChoiceMetadata, ListMetadata


EMPTY = inspect.Parameter.empty


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


class Single(Enum):
    ONLY = "only"


RETURNS_NONE = [
    (EMPTY, None, None),
    (EMPTY, ChoiceMetadata(options=("a", "b")), None),
    (EMPTY, ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None),
    (EMPTY, None, ListMetadata()),
    (None, None, None),
    (None, ChoiceMetadata(options=("a", "b")), None),
    (None, ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None),
    (None, None, ListMetadata()),
]


PASSTHROUGH = [
    ("hello", None, None, "hello"),
    (42, None, None, 42),
    (3.14, None, None, 3.14),
    (True, None, None, True),
    (False, None, None, False),
    ("", None, None, ""),
    (0, None, None, 0),
    (-1, None, None, -1),
    ("a", ChoiceMetadata(options=("a", "b", "c")), None, "a"),
    (1, ChoiceMetadata(options=(1, 2, 3)), None, 1),
    (
        "red",
        ChoiceMetadata(
            options=("red", "blue"),
            options_function=lambda: ["red", "blue"],
        ),
        None,
        "red",
    ),
    ([1, 2, 3], None, ListMetadata(), [1, 2, 3]),
    (["a", "b"], None, ListMetadata(min_length=1), ["a", "b"]),
    ([], None, ListMetadata(), []),
    (["a", "b"], ChoiceMetadata(options=("a", "b", "c")), ListMetadata(), ["a", "b"]),
]


ENUM_SINGLE = [
    (Color.RED, ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None, "red"),
    (Color.GREEN, ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None, "green"),
    (Color.BLUE, ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None, "blue"),
    (Status.ACTIVE, ChoiceMetadata(enum_class=Status, options=(1, 0)), None, 1),
    (Status.INACTIVE, ChoiceMetadata(enum_class=Status, options=(1, 0)), None, 0),
    (Single.ONLY, ChoiceMetadata(enum_class=Single, options=("only",)), None, "only"),
]


ENUM_RAW = [
    ("red", ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")), None, "red"),
    (1, ChoiceMetadata(enum_class=Status, options=(1, 0)), None, 1),
    (0, ChoiceMetadata(enum_class=Status, options=(1, 0)), None, 0),
]


ENUM_LIST = [
    (
        [Color.RED, Color.BLUE],
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        ["red", "blue"],
    ),
    (
        [Status.ACTIVE, Status.INACTIVE],
        ChoiceMetadata(enum_class=Status, options=(1, 0)),
        ListMetadata(),
        [1, 0],
    ),
    (
        [Color.RED],
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(min_length=1),
        ["red"],
    ),
    (
        [],
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        [],
    ),
]


ENUM_LIST_MIXED = [
    (
        [Color.RED, "green"],
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        ["red", "green"],
    ),
    (
        ["red", Color.BLUE],
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        ["red", "blue"],
    ),
    (
        [Status.ACTIVE, 0],
        ChoiceMetadata(enum_class=Status, options=(1, 0)),
        ListMetadata(),
        [1, 0],
    ),
]


ENUM_LIST_TUPLE = [
    (
        (Color.RED, Color.GREEN),
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        ["red", "green"],
    ),
]


ENUM_NON_LIST_WITH_LIST_META = [
    (
        "not a list",
        ChoiceMetadata(enum_class=Color, options=("red", "green", "blue")),
        ListMetadata(),
        "not a list",
    ),
]


@pytest.mark.parametrize("default, choices, list_meta", RETURNS_NONE)
def test_returns_none(default, choices, list_meta):
    result = normalize_default(default, choices, list_meta)
    assert result is None


@pytest.mark.parametrize("default, choices, list_meta, expected", PASSTHROUGH)
def test_passthrough(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_SINGLE)
def test_enum_single(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected
    assert not isinstance(result, Enum)


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_RAW)
def test_enum_raw_passthrough(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_LIST)
def test_enum_list(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected
    for item in result:
        assert not isinstance(item, Enum)


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_LIST_MIXED)
def test_enum_list_mixed(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_LIST_TUPLE)
def test_enum_list_tuple(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected
    assert isinstance(result, list)


@pytest.mark.parametrize("default, choices, list_meta, expected", ENUM_NON_LIST_WITH_LIST_META)
def test_enum_non_list_with_list_meta(default, choices, list_meta, expected):
    result = normalize_default(default, choices, list_meta)
    assert result == expected

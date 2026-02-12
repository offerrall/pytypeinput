import pytest
from typing import Annotated, Literal
from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum

from pydantic import BaseModel, Field

from pytypeinput import (
    analyze_function,
    analyze_pydantic_model,
    analyze_dataclass,
    analyze_class_init,
)


# ─── Shared types ────────────────────────────────────────────────────

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


# ─── analyze_function ────────────────────────────────────────────────

def fn_basic(name: str, age: int, score: float, active: bool) -> None: ...
def fn_defaults(name: str = "world", count: int = 10) -> None: ...
def fn_optional(name: str | None = None, age: int | None = None) -> None: ...
def fn_annotated(value: Annotated[int, Field(ge=0, le=100)] = 50) -> None: ...
def fn_enum(color: Color = Color.RED) -> None: ...
def fn_literal(size: Literal["S", "M", "L"] = "M") -> None: ...
def fn_date(birthday: date = date(2000, 1, 1)) -> None: ...
def fn_list(tags: list[str] = ["a"]) -> None: ...
def fn_mixed(name: str, age: int = 25, color: Color | None = None) -> None: ...
def fn_no_annotations(x, y): ...
def fn_partial(x, name: str = "hi"): ...

FN_TESTS = [
    ("basic types",     fn_basic,       4,  ["name", "age", "score", "active"]),
    ("with defaults",   fn_defaults,    2,  ["name", "count"]),
    ("optional",        fn_optional,    2,  ["name", "age"]),
    ("annotated",       fn_annotated,   1,  ["value"]),
    ("enum",            fn_enum,        1,  ["color"]),
    ("literal",         fn_literal,     1,  ["size"]),
    ("date",            fn_date,        1,  ["birthday"]),
    ("list",            fn_list,        1,  ["tags"]),
    ("mixed",           fn_mixed,       3,  ["name", "age", "color"]),
    ("no annotations",  fn_no_annotations, 0, []),
    ("partial annot",   fn_partial,     1,  ["name"]),
]

@pytest.mark.parametrize("label,func,count,names", FN_TESTS, ids=[x[0] for x in FN_TESTS])
def test_analyze_function(label, func, count, names):
    result = analyze_function(func)
    assert len(result) == count
    assert [p.name for p in result] == names


FN_TYPES = [
    ("str",     fn_basic, "name",   str),
    ("int",     fn_basic, "age",    int),
    ("float",   fn_basic, "score",  float),
    ("bool",    fn_basic, "active", bool),
]

@pytest.mark.parametrize("label,func,field,expected_type", FN_TYPES, ids=[x[0] for x in FN_TYPES])
def test_analyze_function_types(label, func, field, expected_type):
    result = {p.name: p for p in analyze_function(func)}
    assert result[field].param_type is expected_type


FN_DEFAULTS = [
    ("str default",     fn_defaults,    "name",     "world"),
    ("int default",     fn_defaults,    "count",    10),
    ("enum default",    fn_enum,        "color",    "red"),
    ("literal default", fn_literal,     "size",     "M"),
]

@pytest.mark.parametrize("label,func,field,expected", FN_DEFAULTS, ids=[x[0] for x in FN_DEFAULTS])
def test_analyze_function_defaults(label, func, field, expected):
    result = {p.name: p for p in analyze_function(func)}
    assert result[field].default == expected


FN_OPTIONAL = [
    ("optional str",    fn_optional, "name",  True),
    ("optional int",    fn_optional, "age",   True),
    ("required str",    fn_basic,    "name",  False),
    ("mixed optional",  fn_mixed,    "color", True),
    ("mixed required",  fn_mixed,    "name",  False),
]

@pytest.mark.parametrize("label,func,field,is_opt", FN_OPTIONAL, ids=[x[0] for x in FN_OPTIONAL])
def test_analyze_function_optional(label, func, field, is_opt):
    result = {p.name: p for p in analyze_function(func)}
    assert (result[field].optional is not None) == is_opt


# ─── analyze_pydantic_model ─────────────────────────────────────────

class BasicModel(BaseModel):
    name: str
    age: int
    score: float = 0.0

class OptionalModel(BaseModel):
    name: str | None = None
    count: int = 5

class AnnotatedModel(BaseModel):
    value: Annotated[int, Field(ge=0, le=100)] = 50

class EnumModel(BaseModel):
    color: Color = Color.RED

class LiteralModel(BaseModel):
    size: Literal["S", "M", "L"]

class ListModel(BaseModel):
    tags: list[str]

class ComplexModel(BaseModel):
    name: str
    age: int = 25
    color: Color | None = None
    tags: list[str] = ["default"]

PYDANTIC_TESTS = [
    ("basic",       BasicModel,     3,  ["name", "age", "score"]),
    ("optional",    OptionalModel,  2,  ["name", "count"]),
    ("annotated",   AnnotatedModel, 1,  ["value"]),
    ("enum",        EnumModel,      1,  ["color"]),
    ("literal",     LiteralModel,   1,  ["size"]),
    ("list",        ListModel,      1,  ["tags"]),
    ("complex",     ComplexModel,   4,  ["name", "age", "color", "tags"]),
]

@pytest.mark.parametrize("label,model,count,names", PYDANTIC_TESTS, ids=[x[0] for x in PYDANTIC_TESTS])
def test_analyze_pydantic(label, model, count, names):
    result = analyze_pydantic_model(model)
    assert len(result) == count
    assert [p.name for p in result] == names


PYDANTIC_DEFAULTS = [
    ("float default",   BasicModel,     "score",    0.0),
    ("int default",     OptionalModel,  "count",    5),
    ("annotated",       AnnotatedModel, "value",    50),
    ("enum",            EnumModel,      "color",    "red"),
]

@pytest.mark.parametrize("label,model,field,expected", PYDANTIC_DEFAULTS, ids=[x[0] for x in PYDANTIC_DEFAULTS])
def test_analyze_pydantic_defaults(label, model, field, expected):
    result = {p.name: p for p in analyze_pydantic_model(model)}
    assert result[field].default == expected


def test_analyze_pydantic_not_basemodel():
    with pytest.raises(TypeError):
        analyze_pydantic_model(dict)


# ─── analyze_dataclass ──────────────────────────────────────────────

@dataclass
class BasicDC:
    name: str
    age: int
    score: float = 0.0

@dataclass
class OptionalDC:
    name: str | None = None
    count: int = 5

@dataclass
class AnnotatedDC:
    value: Annotated[int, Field(ge=0, le=100)] = 50

@dataclass
class EnumDC:
    color: Color = Color.RED

@dataclass
class ListDC:
    tags: list[str] = field(default_factory=lambda: ["a"])

@dataclass
class NoInitFieldDC:
    name: str
    internal: str = field(init=False, default="hidden")

DC_TESTS = [
    ("basic",           BasicDC,        3,  ["name", "age", "score"]),
    ("optional",        OptionalDC,     2,  ["name", "count"]),
    ("annotated",       AnnotatedDC,    1,  ["value"]),
    ("enum",            EnumDC,         1,  ["color"]),
    ("list factory",    ListDC,         1,  ["tags"]),
    ("no init field",   NoInitFieldDC,  1,  ["name"]),
]

@pytest.mark.parametrize("label,cls,count,names", DC_TESTS, ids=[x[0] for x in DC_TESTS])
def test_analyze_dataclass(label, cls, count, names):
    result = analyze_dataclass(cls)
    assert len(result) == count
    assert [p.name for p in result] == names


DC_DEFAULTS = [
    ("float default",   BasicDC,    "score",    0.0),
    ("int default",     OptionalDC, "count",    5),
    ("enum default",    EnumDC,     "color",    "red"),
]

@pytest.mark.parametrize("label,cls,field_name,expected", DC_DEFAULTS, ids=[x[0] for x in DC_DEFAULTS])
def test_analyze_dataclass_defaults(label, cls, field_name, expected):
    result = {p.name: p for p in analyze_dataclass(cls)}
    assert result[field_name].default == expected


def test_analyze_dataclass_not_dataclass():
    with pytest.raises(TypeError):
        analyze_dataclass(dict)


# ─── analyze_class_init ─────────────────────────────────────────────

class BasicClass:
    def __init__(self, name: str, age: int, score: float = 0.0):
        pass

class OptionalClass:
    def __init__(self, name: str | None = None, count: int = 5):
        pass

class EnumClass:
    def __init__(self, color: Color = Color.RED):
        pass

class NoAnnotations:
    def __init__(self, x, y):
        pass

class MixedAnnotations:
    def __init__(self, x, name: str, y, age: int = 25):
        pass

CLASS_TESTS = [
    ("basic",           BasicClass,         3,  ["name", "age", "score"]),
    ("optional",        OptionalClass,      2,  ["name", "count"]),
    ("enum",            EnumClass,          1,  ["color"]),
    ("no annotations",  NoAnnotations,      0,  []),
    ("mixed",           MixedAnnotations,   2,  ["name", "age"]),
]

@pytest.mark.parametrize("label,cls,count,names", CLASS_TESTS, ids=[x[0] for x in CLASS_TESTS])
def test_analyze_class_init(label, cls, count, names):
    result = analyze_class_init(cls)
    assert len(result) == count
    assert [p.name for p in result] == names


CLASS_DEFAULTS = [
    ("float default",   BasicClass,     "score",    0.0),
    ("int default",     OptionalClass,  "count",    5),
    ("enum default",    EnumClass,      "color",    "red"),
]

@pytest.mark.parametrize("label,cls,field_name,expected", CLASS_DEFAULTS, ids=[x[0] for x in CLASS_DEFAULTS])
def test_analyze_class_init_defaults(label, cls, field_name, expected):
    result = {p.name: p for p in analyze_class_init(cls)}
    assert result[field_name].default == expected
import inspect
import pytest
from typing import Annotated, Literal, Any
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.param import ParamMetadata
from pytypeinput.helpers import rebuild_annotated, serialize_value
from pytypeinput.types import (
    Label, Description, Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword, Dropdown,
    OptionalEnabled, OptionalDisabled,
    Color, Email, ImageFile,
)

EMPTY = inspect.Parameter.empty


# ===== ENUMS =====

class Priority(Enum):
    LOW = "low"
    HIGH = "high"

class Size(Enum):
    S = 1
    M = 2
    L = 3


def colors():
    return ["red", "green", "blue"]


# =============================================================================
# 1. helpers.py — rebuild_annotated
# =============================================================================

class TestRebuildAnnotated:
    def test_empty_metadata_returns_base(self):
        assert rebuild_annotated(int, []) is int

    def test_empty_metadata_returns_str(self):
        assert rebuild_annotated(str, []) is str

    def test_single_metadata(self):
        from typing import get_origin, get_args
        result = rebuild_annotated(int, [Field(ge=0)])
        assert get_origin(result) is Annotated

    def test_multiple_metadata(self):
        from typing import get_origin, get_args
        result = rebuild_annotated(str, [Field(min_length=1), Placeholder("...")])
        args = get_args(result)
        assert args[0] is str
        assert len(args) == 3


# =============================================================================
# 2. helpers.py — serialize_value branches
# =============================================================================

class TestSerializeValue:
    def test_none(self):
        assert serialize_value(None) is None

    def test_enum_instance(self):
        assert serialize_value(Priority.LOW) == "low"
        assert serialize_value(Size.S) == 1

    def test_type_class(self):
        assert serialize_value(int) == "int"
        assert serialize_value(str) == "str"
        assert serialize_value(Priority) == "Priority"

    def test_date(self):
        assert serialize_value(date(2024, 1, 15)) == "2024-01-15"

    def test_date_min(self):
        assert serialize_value(date.min) == date.min.isoformat()

    def test_time(self):
        assert serialize_value(time(14, 30)) == "14:30:00"

    def test_time_midnight(self):
        assert serialize_value(time(0, 0)) == "00:00:00"

    def test_tuple(self):
        assert serialize_value(("a", "b")) == ["a", "b"]

    def test_tuple_nested_enum(self):
        assert serialize_value((Priority.LOW, Priority.HIGH)) == ["low", "high"]

    def test_list(self):
        assert serialize_value([1, 2, 3]) == [1, 2, 3]

    def test_list_with_enums(self):
        assert serialize_value([Priority.LOW, "raw"]) == ["low", "raw"]

    def test_list_with_none(self):
        assert serialize_value([None, 1]) == [None, 1]

    def test_tuple_with_none(self):
        assert serialize_value((None, "a")) == [None, "a"]

    def test_callable_returns_none(self):
        assert serialize_value(lambda: None) is None
        assert serialize_value(colors) is None

    def test_primitives_passthrough(self):
        assert serialize_value(42) == 42
        assert serialize_value(3.14) == 3.14
        assert serialize_value("hello") == "hello"
        assert serialize_value(True) is True
        assert serialize_value(False) is False

    def test_empty_string(self):
        assert serialize_value("") == ""

    def test_zero(self):
        assert serialize_value(0) == 0
        assert serialize_value(0.0) == 0.0

    def test_nested_tuple_with_types(self):
        result = serialize_value((date(2024, 1, 1), time(12, 0)))
        assert result == ["2024-01-01", "12:00:00"]

    def test_nested_list_with_types(self):
        result = serialize_value([date(2024, 1, 1), None, Priority.LOW])
        assert result == ["2024-01-01", None, "low"]

    def test_empty_list(self):
        assert serialize_value([]) == []

    def test_empty_tuple(self):
        assert serialize_value(()) == []


# =============================================================================
# 3. validate_type_01 — _is_none_type with Annotated[None, ...]
# =============================================================================

class TestValidateTypeNoneVariants:
    def test_annotated_none_in_union_rejected_if_alone(self):
        with pytest.raises(TypeError):
            analyze_type(type(None), "f")

    def test_optional_enabled_union_valid(self):
        result = analyze_type(str | OptionalEnabled, "f")
        assert isinstance(result, ParamMetadata)

    def test_optional_disabled_union_valid(self):
        result = analyze_type(str | OptionalDisabled, "f")
        assert isinstance(result, ParamMetadata)

    def test_three_way_union_with_annotated_none(self):
        with pytest.raises(TypeError, match="more than 2 types"):
            analyze_type(str | int | OptionalEnabled, "f")


# =============================================================================
# 4. extract_list — list without type args (bare `list`)
# =============================================================================

class TestBareListEdge:
    def test_bare_list_rejected(self):
        with pytest.raises(TypeError, match="Empty list type"):
            analyze_type(list, "f")

    def test_bare_list_optional_rejected(self):
        with pytest.raises(TypeError, match="Empty list type"):
            analyze_type(list | None, "f")


# =============================================================================
# 5. validate_final — enum default not instance, not in options
# =============================================================================

class TestEnumDefaultEdgeCases:
    def test_enum_raw_value_valid(self):
        result = analyze_type(Priority, "f", "low")
        assert result.default == "low"

    def test_enum_raw_value_invalid(self):
        with pytest.raises(ValueError, match="not in options"):
            analyze_type(Priority, "f", "medium")

    def test_enum_wrong_type_default(self):
        with pytest.raises(TypeError, match="not a valid str"):
            analyze_type(Priority, "f", 123)

    def test_enum_instance_from_different_enum(self):
        with pytest.raises(TypeError, match="not a valid str"):
            analyze_type(Priority, "f", Size.S)

    def test_int_enum_raw_value_valid(self):
        result = analyze_type(Size, "f", 2)
        assert result.default == 2

    def test_int_enum_raw_value_invalid(self):
        with pytest.raises(ValueError, match="not in options"):
            analyze_type(Size, "f", 99)


# =============================================================================
# 6. to_dict — choices is None (no choices path)
# =============================================================================

class TestToDictNoChoices:
    def test_plain_int_no_choices(self):
        d = analyze_type(int, "n", 42).to_dict()
        assert d["choices"] is None

    def test_plain_str_no_choices(self):
        d = analyze_type(str, "s").to_dict()
        assert d["choices"] is None

    def test_constrained_no_choices(self):
        d = analyze_type(Annotated[int, Field(ge=0, le=100)], "n").to_dict()
        assert d["choices"] is None
        assert d["constraints"] is not None


# =============================================================================
# 7. to_dict — all None metadata fields
# =============================================================================

class TestToDictAllNone:
    def test_minimal_to_dict(self):
        d = analyze_type(int, "x").to_dict()
        assert d["constraints"] is None
        assert d["optional"] is None
        assert d["list"] is None
        assert d["choices"] is None
        assert d["item_ui"] is None
        assert d["param_ui"] is None

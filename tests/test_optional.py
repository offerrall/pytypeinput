import pytest
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pytypeinput.types import OptionalEnabled, OptionalDisabled
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestBasicOptional:
    def test_int_optional_no_default(self):
        def func(x: int | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional is not None
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_int_optional_with_default(self):
        def func(x: int | None = 5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional is not None
        assert x.optional.enabled is True
        assert x.default == 5
    
    def test_str_optional_no_default(self):
        def func(x: str | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.optional.enabled is False
    
    def test_str_optional_with_default(self):
        def func(x: str | None = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == "hello"
    
    def test_float_optional_no_default(self):
        def func(x: float | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.optional.enabled is False
    
    def test_float_optional_with_default(self):
        def func(x: float | None = 3.14): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 3.14
    
    def test_bool_optional_no_default(self):
        def func(x: bool | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.optional.enabled is False
    
    def test_bool_optional_false_default(self):
        def func(x: bool | None = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is False
    
    def test_bool_optional_true_default(self):
        def func(x: bool | None = True): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is True
    
    def test_date_optional_no_default(self):
        from datetime import date
        def func(x: date | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == date
        assert x.optional.enabled is False
    
    def test_date_optional_with_default(self):
        from datetime import date
        def func(x: date | None = date(2025, 1, 1)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == date(2025, 1, 1)
    
    def test_time_optional_no_default(self):
        from datetime import time
        def func(x: time | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == time
        assert x.optional.enabled is False
    
    def test_time_optional_with_default(self):
        from datetime import time
        def func(x: time | None = time(14, 30)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == time(14, 30)


class TestOptionalEnabled:
    def test_int_optional_enabled_no_default(self):
        def func(x: int | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is True
        assert x.default is None
    
    def test_int_optional_enabled_with_default(self):
        def func(x: int | OptionalEnabled = 10): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 10
    
    def test_str_optional_enabled_no_default(self):
        def func(x: str | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.optional.enabled is True
        assert x.default is None
    
    def test_float_optional_enabled_with_default(self):
        def func(x: float | OptionalEnabled = 2.5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 2.5
    
    def test_bool_optional_enabled_no_default(self):
        def func(x: bool | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is None


class TestOptionalDisabled:
    def test_int_optional_disabled_no_default(self):
        def func(x: int | OptionalDisabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_int_optional_disabled_with_default(self):
        def func(x: int | OptionalDisabled = 10): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == 10
    
    def test_str_optional_disabled_with_default(self):
        def func(x: str | OptionalDisabled = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == "hello"
    
    def test_float_optional_disabled_no_default(self):
        def func(x: float | OptionalDisabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_bool_optional_disabled_true_default(self):
        def func(x: bool | OptionalDisabled = True): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default is True


class TestOptionalWithConstraints:
    def test_int_optional_with_ge(self):
        def func(x: Annotated[int, Field(ge=0)] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is False
        assert x.constraints is not None
    
    def test_int_optional_with_ge_and_default(self):
        def func(x: Annotated[int, Field(ge=0)] | None = 5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 5
    
    def test_str_optional_with_min_length(self):
        def func(x: Annotated[str, Field(min_length=3)] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.optional.enabled is False
        assert x.constraints is not None
    
    def test_str_optional_with_min_length_and_default(self):
        def func(x: Annotated[str, Field(min_length=3)] | None = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == "hello"
    
    def test_float_optional_with_range(self):
        def func(x: Annotated[float, Field(ge=0.0, le=1.0)] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.optional.enabled is False
    
    def test_float_optional_with_range_and_default(self):
        def func(x: Annotated[float, Field(ge=0.0, le=1.0)] | None = 0.5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 0.5


class TestOptionalEnabledWithConstraints:
    def test_int_optional_enabled_with_ge(self):
        def func(x: Annotated[int, Field(ge=0)] | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is True
        assert x.constraints is not None
        assert x.default is None
    
    def test_str_optional_enabled_with_pattern(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$')] | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.constraints is not None


class TestOptionalDisabledWithConstraints:
    def test_int_optional_disabled_with_le(self):
        def func(x: Annotated[int, Field(le=100)] | OptionalDisabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is False
        assert x.constraints is not None
    
    def test_int_optional_disabled_with_default_and_constraints(self):
        def func(x: Annotated[int, Field(ge=0, le=100)] | OptionalDisabled = 50): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == 50


class TestMultipleOptionalParameters:
    def test_mixed_optional_and_required(self):
        def func(a: int, b: int | None, c: str, d: str | None = "test"): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').optional is None
        assert get_param(result, 'b').optional.enabled is False
        assert get_param(result, 'c').optional is None
        assert get_param(result, 'd').optional.enabled is True
    
    def test_multiple_optional_different_types(self):
        def func(
            a: int | None,
            c: float | OptionalEnabled,
            b: str | None = "hello",
            d: bool | OptionalDisabled = True
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').optional.enabled is False
        assert get_param(result, 'b').optional.enabled is True
        assert get_param(result, 'c').optional.enabled is True
        assert get_param(result, 'd').optional.enabled is False
    
    def test_all_optional_with_constraints(self):
        def func(
            a: Annotated[int, Field(ge=0)] | None,
            c: Annotated[float, Field(le=100.0)] | OptionalEnabled,
            b: Annotated[str, Field(min_length=3)] | None = "test",
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').optional.enabled is False
        assert get_param(result, 'b').optional.enabled is True
        assert get_param(result, 'c').optional.enabled is True


class TestOptionalEdgeCases:
    def test_optional_with_zero_default(self):
        def func(x: int | None = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 0
    
    def test_optional_with_empty_string_default(self):
        def func(x: str | None = ""): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == ""
    
    def test_optional_with_false_default(self):
        def func(x: bool | None = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is False
    
    def test_optional_none_explicit_default(self):
        def func(x: int | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default is None


class TestInvalidOptional:
    def test_only_none_type(self):
        def func(x: None): pass
        
        with pytest.raises(TypeError, match="cannot have only None type"):
            analyze_function(func)
    
    def test_annotated_none_duplicate(self):
        from pytypeinput.types import _OptionalEnabledMarker, _OptionalDisabledMarker
        
        def func(x: int | Annotated[None, _OptionalEnabledMarker()] | Annotated[None, _OptionalDisabledMarker()]): pass
        
        with pytest.raises(TypeError, match="multiple None types"):
            analyze_function(func)
    
    def test_multiple_non_none_types(self):
        def func(x: int | str | None): pass
        
        with pytest.raises(TypeError, match="multiple non-None types"):
            analyze_function(func)
    
    def test_invalid_marker(self):
        class BadMarker: pass
        def func(x: int | Annotated[None, BadMarker()]): pass
        
        with pytest.raises(TypeError, match="Invalid marker"):
            analyze_function(func)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
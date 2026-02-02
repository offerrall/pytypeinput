import pytest
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pydantic import Field, ValidationError


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


def get_constraint(field_info, name):
    if field_info is None:
        return None
    for constraint in field_info.metadata:
        if hasattr(constraint, name):
            return getattr(constraint, name)
    return None


class TestIntConstraints:
    def test_int_ge(self):
        def func(x: Annotated[int, Field(ge=0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.constraints is not None
        assert get_constraint(x.constraints, 'ge') == 0
    
    def test_int_le(self):
        def func(x: Annotated[int, Field(le=100)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'le') == 100
    
    def test_int_gt(self):
        def func(x: Annotated[int, Field(gt=0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'gt') == 0
    
    def test_int_lt(self):
        def func(x: Annotated[int, Field(lt=100)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'lt') == 100
    
    def test_int_ge_le_combined(self):
        def func(x: Annotated[int, Field(ge=0, le=100)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == 0
        assert get_constraint(x.constraints, 'le') == 100
    
    def test_int_gt_lt_combined(self):
        def func(x: Annotated[int, Field(gt=0, lt=100)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'gt') == 0
        assert get_constraint(x.constraints, 'lt') == 100
    
    def test_int_with_valid_default_ge(self):
        def func(x: Annotated[int, Field(ge=0)] = 5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 5
    
    def test_int_with_valid_default_le(self):
        def func(x: Annotated[int, Field(le=100)] = 50): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 50
    
    def test_int_with_valid_default_range(self):
        def func(x: Annotated[int, Field(ge=0, le=100)] = 50): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 50
    
    def test_int_with_boundary_default_ge(self):
        def func(x: Annotated[int, Field(ge=0)] = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0
    
    def test_int_with_boundary_default_le(self):
        def func(x: Annotated[int, Field(le=100)] = 100): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 100
    
    def test_int_negative_constraints(self):
        def func(x: Annotated[int, Field(ge=-100, le=-10)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == -100
        assert get_constraint(x.constraints, 'le') == -10


class TestFloatConstraints:
    def test_float_ge(self):
        def func(x: Annotated[float, Field(ge=0.0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert get_constraint(x.constraints, 'ge') == 0.0
    
    def test_float_le(self):
        def func(x: Annotated[float, Field(le=100.0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'le') == 100.0
    
    def test_float_gt(self):
        def func(x: Annotated[float, Field(gt=0.0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'gt') == 0.0
    
    def test_float_lt(self):
        def func(x: Annotated[float, Field(lt=100.0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'lt') == 100.0
    
    def test_float_range(self):
        def func(x: Annotated[float, Field(ge=0.0, le=1.0)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == 0.0
        assert get_constraint(x.constraints, 'le') == 1.0
    
    def test_float_with_valid_default(self):
        def func(x: Annotated[float, Field(ge=0.0, le=100.0)] = 50.5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 50.5
    
    def test_float_with_boundary_default(self):
        def func(x: Annotated[float, Field(ge=0.0)] = 0.0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0.0
    
    def test_float_negative_range(self):
        def func(x: Annotated[float, Field(ge=-10.5, le=-0.5)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == -10.5
        assert get_constraint(x.constraints, 'le') == -0.5


class TestStringConstraints:
    def test_str_min_length(self):
        def func(x: Annotated[str, Field(min_length=3)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert get_constraint(x.constraints, 'min_length') == 3
    
    def test_str_max_length(self):
        def func(x: Annotated[str, Field(max_length=20)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'max_length') == 20
    
    def test_str_min_max_length(self):
        def func(x: Annotated[str, Field(min_length=3, max_length=20)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'min_length') == 3
        assert get_constraint(x.constraints, 'max_length') == 20
    
    def test_str_pattern(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$')]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'pattern') == r'^[a-z]+$'
    
    def test_str_pattern_email(self):
        def func(x: Annotated[str, Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'pattern') == r'^[^@]+@[^@]+\.[^@]+$'
    
    def test_str_pattern_and_length(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$', min_length=3, max_length=10)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'pattern') == r'^[a-z]+$'
        assert get_constraint(x.constraints, 'min_length') == 3
        assert get_constraint(x.constraints, 'max_length') == 10
    
    def test_str_with_valid_default_min_length(self):
        def func(x: Annotated[str, Field(min_length=3)] = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello"
    
    def test_str_with_valid_default_max_length(self):
        def func(x: Annotated[str, Field(max_length=10)] = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello"
    
    def test_str_with_valid_default_pattern(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$')] = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello"
    
    def test_str_with_boundary_default_min_length(self):
        def func(x: Annotated[str, Field(min_length=3)] = "abc"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "abc"
    
    def test_str_with_boundary_default_max_length(self):
        def func(x: Annotated[str, Field(max_length=5)] = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello"


class TestDateTimeConstraints:
    def test_date_ge(self):
        from datetime import date
        def func(x: Annotated[date, Field(ge=date(2020, 1, 1))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == date
        assert get_constraint(x.constraints, 'ge') == date(2020, 1, 1)
    
    def test_date_le(self):
        from datetime import date
        def func(x: Annotated[date, Field(le=date(2030, 12, 31))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'le') == date(2030, 12, 31)
    
    def test_date_range(self):
        from datetime import date
        def func(x: Annotated[date, Field(ge=date(2020, 1, 1), le=date(2030, 12, 31))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == date(2020, 1, 1)
        assert get_constraint(x.constraints, 'le') == date(2030, 12, 31)
    
    def test_time_ge(self):
        from datetime import time
        def func(x: Annotated[time, Field(ge=time(9, 0))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == time
        assert get_constraint(x.constraints, 'ge') == time(9, 0)
    
    def test_time_le(self):
        from datetime import time
        def func(x: Annotated[time, Field(le=time(17, 0))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'le') == time(17, 0)


class TestMultipleConstraints:
    def test_multiple_params_different_constraints(self):
        def func(
            a: Annotated[int, Field(ge=0)],
            b: Annotated[str, Field(min_length=3)],
            c: Annotated[float, Field(le=100.0)]
        ): pass
        result = analyze_function(func)
        
        assert get_constraint(get_param(result, 'a').constraints, 'ge') == 0
        assert get_constraint(get_param(result, 'b').constraints, 'min_length') == 3
        assert get_constraint(get_param(result, 'c').constraints, 'le') == 100.0
    
    def test_mixed_constrained_and_basic(self):
        def func(
            a: int,
            b: Annotated[int, Field(ge=0)],
            c: str,
            d: Annotated[str, Field(min_length=3)]
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').constraints is None
        assert get_constraint(get_param(result, 'b').constraints, 'ge') == 0
        assert get_param(result, 'c').constraints is None
        assert get_constraint(get_param(result, 'd').constraints, 'min_length') == 3
    
    def test_all_types_with_constraints(self):
        from datetime import date, time
        def func(
            a: Annotated[int, Field(ge=0, le=100)],
            b: Annotated[float, Field(gt=0.0, lt=1.0)],
            c: Annotated[str, Field(min_length=3, max_length=20)],
            d: Annotated[date, Field(ge=date(2020, 1, 1))],
            e: Annotated[time, Field(ge=time(9, 0))]
        ): pass
        result = analyze_function(func)
        
        a = get_param(result, 'a')
        assert get_constraint(a.constraints, 'ge') == 0
        assert get_constraint(a.constraints, 'le') == 100
        
        b = get_param(result, 'b')
        assert get_constraint(b.constraints, 'gt') == 0.0
        assert get_constraint(b.constraints, 'lt') == 1.0
        
        c = get_param(result, 'c')
        assert get_constraint(c.constraints, 'min_length') == 3
        assert get_constraint(c.constraints, 'max_length') == 20
        
        d = get_param(result, 'd')
        assert get_constraint(d.constraints, 'ge') == date(2020, 1, 1)
        
        e = get_param(result, 'e')
        assert get_constraint(e.constraints, 'ge') == time(9, 0)


class TestInvalidConstraints:
    def test_int_invalid_default_below_ge(self):
        def func(x: Annotated[int, Field(ge=0)] = -5): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_int_invalid_default_above_le(self):
        def func(x: Annotated[int, Field(le=100)] = 150): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_int_invalid_default_below_gt(self):
        def func(x: Annotated[int, Field(gt=0)] = 0): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_int_invalid_default_above_lt(self):
        def func(x: Annotated[int, Field(lt=100)] = 100): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_int_invalid_default_outside_range(self):
        def func(x: Annotated[int, Field(ge=0, le=100)] = 150): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_float_invalid_default_below_ge(self):
        def func(x: Annotated[float, Field(ge=0.0)] = -1.5): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_float_invalid_default_above_le(self):
        def func(x: Annotated[float, Field(le=100.0)] = 150.5): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_str_invalid_default_too_short(self):
        def func(x: Annotated[str, Field(min_length=5)] = "hi"): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_str_invalid_default_too_long(self):
        def func(x: Annotated[str, Field(max_length=5)] = "toolongstring"): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_str_invalid_default_pattern_mismatch(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$')] = "HELLO"): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_str_invalid_default_pattern_numbers(self):
        def func(x: Annotated[str, Field(pattern=r'^[a-z]+$')] = "hello123"): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_date_invalid_default_before_ge(self):
        from datetime import date
        def func(x: Annotated[date, Field(ge=date(2020, 1, 1))] = date(2019, 12, 31)): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_date_invalid_default_after_le(self):
        from datetime import date
        def func(x: Annotated[date, Field(le=date(2030, 12, 31))] = date(2031, 1, 1)): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
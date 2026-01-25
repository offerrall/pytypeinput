import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzer import analyze_function


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestBasicInt:
    def test_int_no_default(self):
        def func(x: int): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.name == 'x'
        assert x.param_type == int
        assert x.default is None
        assert x.constraints is None
        assert x.optional is None
        assert x.list is None
    
    def test_int_with_default(self):
        def func(x: int = 5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 5
        assert x.optional is None
    
    def test_int_zero_default(self):
        def func(x: int = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0
    
    def test_int_negative_default(self):
        def func(x: int = -10): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == -10


class TestBasicFloat:
    def test_float_no_default(self):
        def func(x: float): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.default is None
    
    def test_float_with_default(self):
        def func(x: float = 3.14): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 3.14
    
    def test_float_negative_default(self):
        def func(x: float = -2.5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == -2.5
    
    def test_float_zero_default(self):
        def func(x: float = 0.0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0.0


class TestBasicStr:
    def test_str_no_default(self):
        def func(x: str): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.default is None
    
    def test_str_with_default(self):
        def func(x: str = "hello"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello"
    
    def test_str_empty_default(self):
        def func(x: str = ""): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ""
    
    def test_str_multiline_default(self):
        def func(x: str = "hello\nworld"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello\nworld"


class TestBasicBool:
    def test_bool_no_default(self):
        def func(x: bool): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.default is None
    
    def test_bool_true_default(self):
        def func(x: bool = True): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is True
    
    def test_bool_false_default(self):
        def func(x: bool = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is False


class TestBasicDate:
    def test_date_no_default(self):
        from datetime import date
        def func(x: date): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == date
        assert x.default is None
    
    def test_date_with_default(self):
        from datetime import date
        def func(x: date = date(2025, 1, 1)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == date(2025, 1, 1)
    
    def test_date_today_default(self):
        from datetime import date
        today = date.today()
        def func(x: date = today): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == today


class TestBasicTime:
    def test_time_no_default(self):
        from datetime import time
        def func(x: time): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == time
        assert x.default is None
    
    def test_time_with_default(self):
        from datetime import time
        def func(x: time = time(14, 30)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == time(14, 30)
    
    def test_time_with_seconds(self):
        from datetime import time
        def func(x: time = time(14, 30, 45)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == time(14, 30, 45)
    
    def test_time_midnight_default(self):
        from datetime import time
        def func(x: time = time(0, 0)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == time(0, 0)


class TestMultipleParameters:
    def test_mixed_types(self):
        from datetime import date, time
        def func(a: int, b: str, c: float, d: bool, e: date, f: time): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').param_type == int
        assert get_param(result, 'b').param_type == str
        assert get_param(result, 'c').param_type == float
        assert get_param(result, 'd').param_type == bool
        assert get_param(result, 'e').param_type == date
        assert get_param(result, 'f').param_type == time
    
    def test_mixed_with_defaults(self):
        def func(a: int = 1, b: str = "test", c: float = 2.5): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').default == 1
        assert get_param(result, 'b').default == "test"
        assert get_param(result, 'c').default == 2.5
    
    def test_required_and_optional_mixed(self):
        def func(a: int, c: float, b: str = "default", d: bool = True): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').default is None
        assert get_param(result, 'b').default == "default"
        assert get_param(result, 'c').default is None
        assert get_param(result, 'd').default is True
    
    def test_many_parameters(self):
        def func(a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int, i: int, j: int): pass
        result = analyze_function(func)
        
        assert len(result) == 10
        assert all(param.param_type == int for param in result)


class TestInvalidTypes:
    def test_no_type_hint(self):
        def func(x): pass
        
        with pytest.raises(TypeError, match="has no type hint"):
            analyze_function(func)
    
    def test_unsupported_type_dict(self):
        def func(x: dict): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_unsupported_type_list_bare(self):
        def func(x: list): pass
        
        with pytest.raises(TypeError, match="must have a type argument"):
            analyze_function(func)
    
    def test_unsupported_type_tuple(self):
        def func(x: tuple): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_unsupported_type_set(self):
        def func(x: set): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_unsupported_type_custom_class(self):
        class MyClass: pass
        def func(x: MyClass): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_multiple_params_one_invalid(self):
        def func(a: int, b: dict, c: str): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
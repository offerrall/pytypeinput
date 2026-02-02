import pytest
import sys
from pathlib import Path
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time, datetime
from decimal import Decimal
from uuid import UUID
from pathlib import Path as PathType

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pytypeinput.types import Color, Email, OptionalEnabled, OptionalDisabled, Dropdown
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestUnsupportedPythonFeatures:
    
    def test_function_with_args(self):
        def func(x: int, *args): pass
        
        with pytest.raises(TypeError, match=r"\*args not supported"):
            analyze_function(func)
    
    def test_function_with_kwargs(self):
        def func(x: int, **kwargs): pass
        
        with pytest.raises(TypeError, match=r"\*\*kwargs not supported"):
            analyze_function(func)
    
    def test_function_with_both_args_kwargs(self):
        def func(x: int, *args, **kwargs): pass
        
        with pytest.raises(TypeError, match=r"\*args not supported"):
            analyze_function(func)
    
    def test_positional_only_parameters(self):
        def func(x: int, /, y: str): pass
        result = analyze_function(func)
        
        assert len(result) == 2
    
    def test_keyword_only_parameters(self):
        def func(x: int, *, y: str): pass
        result = analyze_function(func)
        
        assert len(result) == 2


class TestUnsupportedTypes:
    
    def test_datetime_not_supported(self):
        def func(dt: datetime): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_decimal_not_supported(self):
        def func(amount: Decimal): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_uuid_not_supported(self):
        def func(id: UUID): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_path_not_supported(self):
        def func(filepath: PathType): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_any_not_supported(self):
        from typing import Any
        def func(x: Any): pass
        
        with pytest.raises(TypeError):
            analyze_function(func)
    
    def test_union_non_optional_not_supported(self):
        def func(x: int | str): pass
        
        with pytest.raises(TypeError, match="multiple non-None types"):
            analyze_function(func)


class TestMethodsVsFunctions:
    
    def test_static_method(self):
        class MyClass:
            @staticmethod
            def my_method(x: int, y: str):
                pass
        
        result = analyze_function(MyClass.my_method)
        assert len(result) == 2


class TestComplexNesting:
    
    def test_triple_annotated_nesting(self):
        def func(x: Annotated[Annotated[Annotated[int, Field(ge=0)], Field(le=100)], Field(gt=-1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.constraints is not None
    
    def test_optional_of_list_of_annotated(self):
        def func(x: list[Annotated[int, Field(ge=0)]] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.list is not None
        assert x.optional is not None
        assert x.constraints is not None


class TestEmptyAndDefaultEdgeCases:
    
    def test_empty_list_with_constraints_becomes_none(self):
        def func(x: Annotated[list[int], Field(min_length=1)] = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
    
    def test_whitespace_only_string_default(self):
        def func(x: str = "   "): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "   "
    
    def test_newline_only_string_default(self):
        def func(x: str = "\n"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "\n"


class TestConstraintCombinations:
    
    def test_ge_and_gt_together(self):
        def func(x: Annotated[int, Field(ge=0, gt=-1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_le_and_lt_together(self):
        def func(x: Annotated[int, Field(le=100, lt=101)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_all_four_constraints_together(self):
        def func(x: Annotated[float, Field(ge=0.0, gt=-0.1, le=100.0, lt=100.1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None


class TestDefaultValidationEdgeCases:
    
    def test_float_precision_in_validation(self):
        def func(x: Annotated[float, Field(ge=0.0)] = 0.0000001): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0.0000001
    
    def test_negative_zero_float(self):
        def func(x: float = -0.0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0.0
    
    def test_date_at_min_boundary(self):
        def func(x: Annotated[date, Field(ge=date(2020, 1, 1))] = date(2020, 1, 1)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == date(2020, 1, 1)
    
    def test_time_at_max_boundary(self):
        def func(x: Annotated[time, Field(le=time(23, 59, 59))] = time(23, 59, 59)): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == time(23, 59, 59)


class TestSpecialCharactersInDefaults:
    
    def test_null_byte_in_string(self):
        def func(x: str = "hello\x00world"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "hello\x00world"
    
    def test_unicode_emoji_in_default(self):
        def func(x: str = "Hello 👋 World 🌍"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "Hello 👋 World 🌍"
    
    def test_escape_sequences_in_default(self):
        def func(x: str = "Line1\tTabbed\nLine2\rCarriage"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert "\t" in x.default
        assert "\n" in x.default


class TestTypeAliases:
    
    def test_type_alias_basic(self):
        UserId = int
        def func(user_id: UserId): pass
        result = analyze_function(func)
        
        user_id = get_param(result, 'user_id')
        assert user_id.param_type == int
    
    def test_type_alias_with_annotation(self):
        UserId = Annotated[int, Field(ge=0)]
        def func(user_id: UserId): pass
        result = analyze_function(func)
        
        user_id = get_param(result, 'user_id')
        assert user_id.param_type == int
        assert user_id.constraints is not None


class TestLiteralExtremeEdgeCases:
    
    def test_literal_with_backslashes(self):
        def func(x: Literal['C:\\Users\\test', 'D:\\Data']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'C:\\Users\\test' in x.choices.options
    
    def test_literal_with_quotes_mixed(self):
        def func(x: Literal["He said 'hello'", 'She said "goodbye"']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 2
    
    def test_literal_very_large_int(self):
        huge = 10**100
        def func(x: Literal[0, huge]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert huge in x.choices.options


class TestEnumExtremeEdgeCases:
    
    def test_enum_with_unicode_values(self):
        class Language(Enum):
            SPANISH = 'Español'
            CHINESE = '中文'
            ARABIC = 'العربية'
        
        def func(lang: Language): pass
        result = analyze_function(func)
        
        lang = get_param(result, 'lang')
        assert 'Español' in lang.choices.options
    
    def test_enum_with_special_char_values(self):
        class Symbol(Enum):
            AT = '@'
            HASH = '#'
            DOLLAR = '$'
        
        def func(symbol: Symbol): pass
        result = analyze_function(func)
        
        symbol = get_param(result, 'symbol')
        assert '@' in symbol.choices.options


class TestDropdownExtremeEdgeCases:
    
    def test_dropdown_with_side_effects(self):
        calls = []
        def track_calls():
            calls.append(1)
            return ['a', 'b']
        
        def func(x: Annotated[str, Dropdown(track_calls)]): pass
        result = analyze_function(func)
        
        assert len(calls) == 1
    
    def test_dropdown_returns_very_large_list(self):
        def huge_list():
            return [f'option_{i}' for i in range(1000)]
        
        def func(x: Annotated[str, Dropdown(huge_list)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
import pytest
import sys
from pathlib import Path
from typing import Annotated, Literal
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pytypeinput.types import Dropdown
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestLiteralBasic:
    
    def test_literal_str_basic(self):
        def func(x: Literal['a', 'b', 'c']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices is not None
        assert x.choices.options == ('a', 'b', 'c')
        assert x.choices.options_function is None
        assert x.choices.enum_class is None
        assert x.default is None
    
    def test_literal_int_basic(self):
        def func(x: Literal[1, 2, 3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.choices.options == (1, 2, 3)
        assert x.choices.options_function is None
        assert x.choices.enum_class is None
    
    def test_literal_bool_basic(self):
        def func(x: Literal[True, False]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.choices.options == (True, False)
    
    def test_literal_float_basic(self):
        def func(x: Literal[1.5, 2.5, 3.5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.choices.options == (1.5, 2.5, 3.5)
    
    def test_literal_single_option(self):
        def func(x: Literal['only']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices.options == ('only',)
        assert len(x.choices.options) == 1
    
    def test_literal_two_options(self):
        def func(x: Literal['yes', 'no']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('yes', 'no')
        assert len(x.choices.options) == 2
    
    def test_literal_many_options(self):
        def func(x: Literal['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 10
        assert x.choices.options[0] == 'a'
        assert x.choices.options[9] == 'j'
    
    def test_literal_preserves_order(self):
        def func(x: Literal['z', 'a', 'm', 'b']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('z', 'a', 'm', 'b')
        assert x.choices.options[0] == 'z'
        assert x.choices.options[3] == 'b'


class TestLiteralStrings:
    
    def test_literal_str_lowercase(self):
        def func(x: Literal['apple', 'banana', 'cherry']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert 'apple' in x.choices.options
    
    def test_literal_str_uppercase(self):
        def func(x: Literal['RED', 'GREEN', 'BLUE']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('RED', 'GREEN', 'BLUE')
    
    def test_literal_str_mixed_case(self):
        def func(x: Literal['Light', 'Dark', 'AUTO']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('Light', 'Dark', 'AUTO')
    
    def test_literal_str_with_spaces(self):
        def func(x: Literal['Option A', 'Option B', 'Option C']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('Option A', 'Option B', 'Option C')
    
    def test_literal_str_with_special_chars(self):
        def func(x: Literal['hello-world', 'test_value', 'option.1']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('hello-world', 'test_value', 'option.1')
    
    def test_literal_str_empty_string(self):
        def func(x: Literal['', 'something']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('', 'something')
        assert '' in x.choices.options
    
    def test_literal_str_numbers_as_strings(self):
        def func(x: Literal['1', '2', '3']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices.options == ('1', '2', '3')
    
    def test_literal_str_long_strings(self):
        def func(x: Literal['This is a very long option', 'Another long option here']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 2


class TestLiteralNumbers:
    
    def test_literal_int_positive(self):
        def func(x: Literal[1, 2, 3, 4, 5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.choices.options == (1, 2, 3, 4, 5)
    
    def test_literal_int_negative(self):
        def func(x: Literal[-1, -2, -3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (-1, -2, -3)
    
    def test_literal_int_mixed_sign(self):
        def func(x: Literal[-2, -1, 0, 1, 2]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (-2, -1, 0, 1, 2)
    
    def test_literal_int_zero(self):
        def func(x: Literal[0, 1, 2]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 0 in x.choices.options
    
    def test_literal_int_large_numbers(self):
        def func(x: Literal[100, 1000, 10000]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (100, 1000, 10000)
    
    def test_literal_float_positive(self):
        def func(x: Literal[1.0, 2.5, 3.14]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.choices.options == (1.0, 2.5, 3.14)
    
    def test_literal_float_negative(self):
        def func(x: Literal[-1.5, -2.5, -3.5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (-1.5, -2.5, -3.5)
    
    def test_literal_float_with_zero(self):
        def func(x: Literal[0.0, 1.0, 2.0]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 0.0 in x.choices.options
    
    def test_literal_float_precision(self):
        def func(x: Literal[0.1, 0.01, 0.001]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (0.1, 0.01, 0.001)
    
    def test_literal_float_scientific(self):
        def func(x: Literal[1e-3, 1e-2, 1e-1]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert len(x.choices.options) == 3


class TestLiteralBooleans:
    
    def test_literal_bool_both(self):
        def func(x: Literal[True, False]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.choices.options == (True, False)
    
    def test_literal_bool_true_only(self):
        def func(x: Literal[True]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (True,)
    
    def test_literal_bool_false_only(self):
        def func(x: Literal[False]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (False,)
    
    def test_literal_bool_reversed_order(self):
        def func(x: Literal[False, True]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == (False, True)


class TestLiteralWithDefaults:
    
    def test_literal_str_with_valid_default_first(self):
        def func(x: Literal['light', 'dark', 'auto'] = 'light'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'light'
        assert x.choices.options == ('light', 'dark', 'auto')
    
    def test_literal_str_with_valid_default_middle(self):
        def func(x: Literal['a', 'b', 'c'] = 'b'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'b'
    
    def test_literal_str_with_valid_default_last(self):
        def func(x: Literal['first', 'second', 'third'] = 'third'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'third'
    
    def test_literal_int_with_valid_default(self):
        def func(x: Literal[1, 2, 3] = 2): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 2
        assert x.param_type == int
    
    def test_literal_float_with_valid_default(self):
        def func(x: Literal[1.0, 2.0, 3.0] = 2.0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 2.0
    
    def test_literal_bool_with_valid_default_true(self):
        def func(x: Literal[True, False] = True): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is True
    
    def test_literal_bool_with_valid_default_false(self):
        def func(x: Literal[True, False] = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is False
    
    def test_literal_single_option_with_default(self):
        def func(x: Literal['only'] = 'only'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'only'
    
    def test_literal_str_empty_string_default(self):
        def func(x: Literal['', 'a', 'b'] = ''): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ''
    
    def test_literal_int_zero_default(self):
        def func(x: Literal[0, 1, 2] = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0
    
    def test_literal_int_negative_default(self):
        def func(x: Literal[-5, -3, -1] = -3): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == -3


class TestLiteralWithOptional:
    
    def test_literal_str_optional_no_default(self):
        def func(x: Literal['a', 'b'] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices.options == ('a', 'b')
        assert x.optional is not None
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_literal_int_optional_no_default(self):
        def func(x: Literal[1, 2, 3] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.optional.enabled is False
    
    def test_literal_optional_with_valid_default(self):
        def func(x: Literal['x', 'y', 'z'] | None = 'y'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'y'
        assert x.optional.enabled is True
    
    def test_literal_optional_with_none_default(self):
        def func(x: Literal['a', 'b'] | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is False
    
    def test_literal_optional_enabled_no_default(self):
        from pytypeinput.types import OptionalEnabled
        def func(x: Literal['opt1', 'opt2'] | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is None
    
    def test_literal_optional_disabled_with_default(self):
        from pytypeinput.types import OptionalDisabled
        def func(x: Literal['a', 'b', 'c'] | OptionalDisabled = 'a'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == 'a'


class TestLiteralWithConstraints:
    
    def test_literal_str_no_field_constraints(self):
        def func(x: Literal['short', 'medium', 'looooong']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is None
        assert x.choices.options == ('short', 'medium', 'looooong')
    
    def test_literal_int_no_field_constraints(self):
        def func(x: Literal[1, 50, 100]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is None
        assert x.choices.options == (1, 50, 100)


class TestMultipleLiteralParameters:
    
    def test_two_literal_params_different_types(self):
        def func(
            x: Literal['a', 'b'],
            y: Literal[1, 2]
        ): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        y = get_param(result, 'y')
        assert x.param_type == str
        assert y.param_type == int
        assert x.choices.options == ('a', 'b')
        assert y.choices.options == (1, 2)
    
    def test_two_literal_params_same_type(self):
        def func(
            theme: Literal['light', 'dark'],
            size: Literal['small', 'large']
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        size = get_param(result, 'size')
        assert theme.choices.options == ('light', 'dark')
        assert size.choices.options == ('small', 'large')
    
    def test_three_literal_params_with_defaults(self):
        def func(
            x: Literal['a', 'b'] = 'a',
            y: Literal[1, 2] = 1,
            z: Literal[True, False] = True
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'x').default == 'a'
        assert get_param(result, 'y').default == 1
        assert get_param(result, 'z').default is True
    
    def test_literal_and_regular_params_mixed(self):
        def func(
            name: str,
            theme: Literal['light', 'dark'],
            age: int
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'name').choices is None
        assert get_param(result, 'theme').choices.options == ('light', 'dark')
        assert get_param(result, 'age').choices is None


class TestInvalidLiteral:
    
    def test_literal_empty(self):
        def func(x: Literal[()]): pass
        
        with pytest.raises(ValueError, match="must have at least one option"):
            analyze_function(func)
    
    def test_literal_mixed_types_str_int(self):
        def func(x: Literal['a', 1]): pass
        
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func)
    
    def test_literal_mixed_types_int_float(self):
        def func(x: Literal[1, 2.5]): pass
        
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func)
    
    def test_literal_mixed_types_str_bool(self):
        def func(x: Literal['yes', True]): pass
        
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func)
    
    def test_literal_mixed_types_three_types(self):
        def func(x: Literal['a', 1, True]): pass
        
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func)
    
    def test_literal_invalid_default_not_in_options(self):
        def func(x: Literal['a', 'b', 'c'] = 'd'): pass
        
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func)
    
    def test_literal_invalid_default_wrong_type(self):
        def func(x: Literal['a', 'b'] = 1): pass
        
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func)
    
    def test_literal_int_invalid_default(self):
        def func(x: Literal[1, 2, 3] = 5): pass
        
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func)
    
    def test_literal_bool_invalid_default(self):
        def func(x: Literal[True] = False): pass
        
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func)
    
    def test_literal_str_case_sensitive_default(self):
        def func(x: Literal['light', 'dark'] = 'Light'): pass
        
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func)


class TestLiteralEdgeCases:
    
    def test_literal_duplicate_values(self):
        def func(x: Literal['a', 'b', 'a']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'a' in x.choices.options
        assert 'b' in x.choices.options
    
    def test_literal_unicode_strings(self):
        def func(x: Literal['こんにちは', '世界', 'ñ']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('こんにちは', '世界', 'ñ')
    
    def test_literal_very_long_option_count(self):
        def func(x: Literal[
            'o1', 'o2', 'o3', 'o4', 'o5', 'o6', 'o7', 'o8', 'o9', 'o10',
            'o11', 'o12', 'o13', 'o14', 'o15', 'o16', 'o17', 'o18', 'o19', 'o20'
        ]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 20
    
    def test_literal_preserves_exact_float_values(self):
        def func(x: Literal[0.1, 0.2, 0.3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 0.1 in x.choices.options
        assert 0.2 in x.choices.options


class TestEnumBasic:
    
    def test_enum_str_values(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
            AUTO = 'auto'
        
        def func(x: Theme): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices.options == ('light', 'dark', 'auto')
        assert x.choices.enum_class == Theme
        assert x.choices.options_function is None
        assert x.default is None
    
    def test_enum_int_values(self):
        class Priority(Enum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3
        
        def func(x: Priority): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.choices.options == (1, 2, 3)
        assert x.choices.enum_class == Priority
    
    def test_enum_bool_values(self):
        class Status(Enum):
            ACTIVE = True
            INACTIVE = False
        
        def func(x: Status): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.choices.options == (True, False)
    
    def test_enum_float_values(self):
        class Rating(Enum):
            LOW = 1.5
            MEDIUM = 3.0
            HIGH = 4.5
        
        def func(x: Rating): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.choices.options == (1.5, 3.0, 4.5)
    
    def test_enum_single_value(self):
        class Single(Enum):
            ONLY = 'only'
        
        def func(x: Single): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('only',)
        assert len(x.choices.options) == 1
    
    def test_enum_many_values(self):
        class Days(Enum):
            MON = 1
            TUE = 2
            WED = 3
            THU = 4
            FRI = 5
            SAT = 6
            SUN = 7
        
        def func(x: Days): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 7
        assert x.choices.options == (1, 2, 3, 4, 5, 6, 7)


class TestEnumWithDefaults:
    
    def test_enum_str_with_valid_default(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
            AUTO = 'auto'
        
        def func(x: Theme = Theme.LIGHT): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'light'
        assert x.choices.enum_class == Theme
    
    def test_enum_int_with_valid_default(self):
        class Priority(Enum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3
        
        def func(x: Priority = Priority.MEDIUM): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 2
    
    def test_enum_first_value_default(self):
        class Status(Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            DONE = 'done'
        
        def func(x: Status = Status.PENDING): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'pending'
    
    def test_enum_last_value_default(self):
        class Status(Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            DONE = 'done'
        
        def func(x: Status = Status.DONE): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'done'
    
    def test_enum_bool_true_default(self):
        class Toggle(Enum):
            ON = True
            OFF = False
        
        def func(x: Toggle = Toggle.ON): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is True
    
    def test_enum_bool_false_default(self):
        class Toggle(Enum):
            ON = True
            OFF = False
        
        def func(x: Toggle = Toggle.OFF): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is False


class TestEnumWithOptional:
    
    def test_enum_optional_no_default(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        def func(x: Theme | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.enum_class == Theme
        assert x.optional is not None
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_enum_optional_with_enum_default(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(x: Priority | None = Priority.LOW): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 1
        assert x.optional.enabled is True
    
    def test_enum_optional_with_none_default(self):
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        def func(x: Status | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is False
    
    def test_enum_optional_enabled(self):
        from pytypeinput.types import OptionalEnabled
        
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        def func(x: Theme | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is None
    
    def test_enum_optional_disabled_with_default(self):
        from pytypeinput.types import OptionalDisabled
        
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(x: Priority | OptionalDisabled = Priority.HIGH): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == 2


class TestMultipleEnumParameters:
    
    def test_two_enum_params_different_enums(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(theme: Theme, priority: Priority): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        priority = get_param(result, 'priority')
        assert theme.choices.enum_class == Theme
        assert priority.choices.enum_class == Priority
        assert theme.param_type == str
        assert priority.param_type == int
    
    def test_enum_and_literal_mixed(self):
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        def func(
            status: Status,
            theme: Literal['light', 'dark']
        ): pass
        result = analyze_function(func)
        
        status = get_param(result, 'status')
        theme = get_param(result, 'theme')
        assert status.choices.enum_class == Status
        assert theme.choices.enum_class is None
        assert status.choices.options == ('active', 'inactive')
        assert theme.choices.options == ('light', 'dark')
    
    def test_enum_and_regular_params(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(
            name: str,
            priority: Priority,
            age: int
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'priority').choices.enum_class == Priority
        assert get_param(result, 'name').choices is None
        assert get_param(result, 'age').choices is None


class TestInvalidEnum:
    
    def test_enum_empty(self):
        class Empty(Enum):
            pass
        
        def func(x: Empty): pass
        
        with pytest.raises(ValueError, match="must have at least one value"):
            analyze_function(func)
    
    def test_enum_mixed_types(self):
        class Mixed(Enum):
            A = 'string'
            B = 123
        
        def func(x: Mixed): pass
        
        with pytest.raises(TypeError, match="must be same type"):
            analyze_function(func)
    
    def test_enum_mixed_types_str_bool(self):
        class Mixed(Enum):
            A = 'yes'
            B = True
        
        def func(x: Mixed): pass
        
        with pytest.raises(TypeError, match="must be same type"):
            analyze_function(func)
    
    def test_enum_mixed_types_int_float(self):
        class Mixed(Enum):
            A = 1
            B = 2.5
        
        def func(x: Mixed): pass
        
        with pytest.raises(TypeError, match="must be same type"):
            analyze_function(func)
    
    def test_enum_invalid_default_not_member(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        def func(x: Theme = 'light'): pass
        
        with pytest.raises(TypeError, match="default must be Theme instance"):
            analyze_function(func)
    
    def test_enum_invalid_default_wrong_enum(self):
        class Theme(Enum):
            LIGHT = 'light'
        
        class Other(Enum):
            DARK = 'dark'
        
        def func(x: Theme = Other.DARK): pass
        
        with pytest.raises(TypeError, match="default must be Theme instance"):
            analyze_function(func)
    
    def test_enum_invalid_default_wrong_type(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(x: Priority = 1): pass
        
        with pytest.raises(TypeError, match="default must be Priority instance"):
            analyze_function(func)


class TestDropdownBasic:
    
    def test_dropdown_str_basic(self):
        def get_options():
            return ['option1', 'option2', 'option3']
        
        def func(x: Annotated[str, Dropdown(get_options)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.choices.options == ('option1', 'option2', 'option3')
        assert x.choices.options_function == get_options
        assert x.choices.enum_class is None
    
    def test_dropdown_int_basic(self):
        def get_numbers():
            return [1, 2, 3, 4, 5]
        
        def func(x: Annotated[int, Dropdown(get_numbers)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.choices.options == (1, 2, 3, 4, 5)
        assert x.choices.options_function == get_numbers
    
    def test_dropdown_bool_basic(self):
        def get_bools():
            return [True, False]
        
        def func(x: Annotated[bool, Dropdown(get_bools)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.choices.options == (True, False)
    
    def test_dropdown_float_basic(self):
        def get_floats():
            return [1.5, 2.5, 3.5]
        
        def func(x: Annotated[float, Dropdown(get_floats)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.choices.options == (1.5, 2.5, 3.5)
    
    def test_dropdown_returns_tuple(self):
        def get_options():
            return ('a', 'b', 'c')
        
        def func(x: Annotated[str, Dropdown(get_options)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('a', 'b', 'c')
    
    def test_dropdown_single_option(self):
        def get_single():
            return ['only']
        
        def func(x: Annotated[str, Dropdown(get_single)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('only',)
    
    def test_dropdown_many_options(self):
        def get_many():
            return [f'opt{i}' for i in range(20)]
        
        def func(x: Annotated[str, Dropdown(get_many)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert len(x.choices.options) == 20


class TestDropdownWithDefaults:
    
    def test_dropdown_str_with_valid_default(self):
        def get_themes():
            return ['light', 'dark', 'auto']
        
        def func(x: Annotated[str, Dropdown(get_themes)] = 'dark'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'dark'
        assert x.choices.options == ('light', 'dark', 'auto')
    
    def test_dropdown_int_with_valid_default(self):
        def get_nums():
            return [10, 20, 30]
        
        def func(x: Annotated[int, Dropdown(get_nums)] = 20): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 20
    
    def test_dropdown_first_option_default(self):
        def get_opts():
            return ['first', 'second', 'third']
        
        def func(x: Annotated[str, Dropdown(get_opts)] = 'first'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'first'
    
    def test_dropdown_last_option_default(self):
        def get_opts():
            return ['first', 'second', 'third']
        
        def func(x: Annotated[str, Dropdown(get_opts)] = 'third'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'third'


class TestDropdownWithOptional:
    
    def test_dropdown_optional_no_default(self):
        def get_themes():
            return ['light', 'dark']
        
        def func(x: Annotated[str, Dropdown(get_themes)] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options_function == get_themes
        assert x.optional is not None
        assert x.optional.enabled is False
    
    def test_dropdown_optional_with_default(self):
        def get_opts():
            return ['a', 'b', 'c']
        
        def func(x: Annotated[str, Dropdown(get_opts)] | None = 'b'): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 'b'
        assert x.optional.enabled is True
    
    def test_dropdown_optional_with_none_default(self):
        def get_opts():
            return [1, 2, 3]
        
        def func(x: Annotated[int, Dropdown(get_opts)] | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is False


class TestDropdownDynamic:
    
    def test_dropdown_callable_stored(self):
        def get_random():
            import random
            return random.sample(['a', 'b', 'c', 'd'], k=2)
        
        def func(x: Annotated[str, Dropdown(get_random)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options_function == get_random
        assert callable(x.choices.options_function)
        
        new_opts = x.choices.options_function()
        assert isinstance(new_opts, list)
        assert len(new_opts) == 2
    
    def test_dropdown_stateful_function(self):
        counter = {'count': 0}
        
        def get_options():
            counter['count'] += 1
            return [f'call_{counter["count"]}']
        
        def func(x: Annotated[str, Dropdown(get_options)]): pass
        result = analyze_function(func)
        
        assert counter['count'] == 1
        
        x = get_param(result, 'x')
        x.choices.options_function()
        assert counter['count'] == 2


class TestInvalidDropdown:
    
    def test_dropdown_not_callable(self):
        with pytest.raises(TypeError, match="must be callable"):
            Dropdown("not_a_function")
    
    def test_dropdown_function_raises_error(self):
        def bad_func():
            raise RuntimeError("Something went wrong")
        
        def func(x: Annotated[str, Dropdown(bad_func)]): pass
        
        with pytest.raises(ValueError, match="Dropdown function failed"):
            analyze_function(func)
    
    def test_dropdown_returns_non_list_non_tuple(self):
        def bad_return():
            return "not a list"
        
        def func(x: Annotated[str, Dropdown(bad_return)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_returns_dict(self):
        def returns_dict():
            return {'a': 1, 'b': 2}
        
        def func(x: Annotated[str, Dropdown(returns_dict)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_returns_empty(self):
        def returns_empty():
            return []
        
        def func(x: Annotated[str, Dropdown(returns_empty)]): pass
        
        with pytest.raises(ValueError, match="returned empty list"):
            analyze_function(func)
    
    def test_dropdown_mixed_types(self):
        def mixed_types():
            return ['string', 123, True]
        
        def func(x: Annotated[str, Dropdown(mixed_types)]): pass
        
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func)
    
    def test_dropdown_type_mismatch(self):
        def returns_ints():
            return [1, 2, 3]
        
        def func(x: Annotated[str, Dropdown(returns_ints)]): pass
        
        with pytest.raises(TypeError, match="type mismatch"):
            analyze_function(func)
    
    def test_dropdown_invalid_default_not_in_options(self):
        def get_opts():
            return ['a', 'b', 'c']
        
        def func(x: Annotated[str, Dropdown(get_opts)] = 'z'): pass
        
        with pytest.raises(ValueError, match="default not in Dropdown options"):
            analyze_function(func)


class TestMixedDropdownTypes:
    
    def test_literal_and_enum_in_same_function(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(
            theme: Literal['light', 'dark'],
            priority: Priority
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        priority = get_param(result, 'priority')
        assert theme.choices.enum_class is None
        assert priority.choices.enum_class == Priority
        assert theme.choices.options == ('light', 'dark')
        assert priority.choices.options == (1, 2)
    
    def test_literal_and_dropdown_in_same_function(self):
        def get_sizes():
            return ['S', 'M', 'L']
        
        def func(
            theme: Literal['light', 'dark'],
            size: Annotated[str, Dropdown(get_sizes)]
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        size = get_param(result, 'size')
        assert theme.choices.options_function is None
        assert size.choices.options_function == get_sizes
    
    def test_enum_and_dropdown_in_same_function(self):
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        def get_priorities():
            return [1, 2, 3]
        
        def func(
            status: Status,
            priority: Annotated[int, Dropdown(get_priorities)]
        ): pass
        result = analyze_function(func)
        
        status = get_param(result, 'status')
        priority = get_param(result, 'priority')
        assert status.choices.enum_class == Status
        assert priority.choices.enum_class is None
        assert priority.choices.options_function == get_priorities
    
    def test_all_three_dropdown_types(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        def get_sizes():
            return ['S', 'M', 'L', 'XL']
        
        def func(
            theme: Theme,
            status: Literal['active', 'pending', 'done'],
            size: Annotated[str, Dropdown(get_sizes)],
            priority: Literal[1, 2, 3] = 2
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        status = get_param(result, 'status')
        size = get_param(result, 'size')
        priority = get_param(result, 'priority')
        
        assert theme.choices.enum_class == Theme
        assert theme.choices.options_function is None
        
        assert status.choices.enum_class is None
        assert status.choices.options_function is None
        assert status.choices.options == ('active', 'pending', 'done')
        
        assert size.choices.enum_class is None
        assert size.choices.options_function == get_sizes
        
        assert priority.default == 2


class TestDropdownEdgeCases:
    
    def test_enum_with_numeric_string_values(self):
        class Numbers(Enum):
            ONE = '1'
            TWO = '2'
            THREE = '3'
        
        def func(x: Numbers): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert '1' in x.choices.options
    
    def test_dropdown_with_special_characters(self):
        def get_special():
            return ['hello-world', 'test_value', 'option.1']
        
        def func(x: Annotated[str, Dropdown(get_special)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'hello-world' in x.choices.options
        assert 'test_value' in x.choices.options
    
    def test_dropdown_with_unicode(self):
        def get_unicode():
            return ['こんにちは', '世界', 'ñoño']
        
        def func(x: Annotated[str, Dropdown(get_unicode)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'こんにちは' in x.choices.options
    
    def test_dropdown_with_empty_string(self):
        def get_with_empty():
            return ['', 'something']
        
        def func(x: Annotated[str, Dropdown(get_with_empty)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert '' in x.choices.options
    
    def test_dropdown_lambda_function(self):
        def func(x: Annotated[str, Dropdown(lambda: ['a', 'b'])]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('a', 'b')
        assert callable(x.choices.options_function)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
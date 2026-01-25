import pytest
import sys
from pathlib import Path
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzer import analyze_function
from pytypeinput.types import (
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File,
    OptionalEnabled, OptionalDisabled, Dropdown
)
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestLiteralMegaIntegration:
    
    def test_literal_optional_with_list_params_mixed(self):
        def func(
            theme: Literal['light', 'dark', 'auto'] = 'light',
            tags: list[str] | None = None,
            priority: Literal[1, 2, 3] | None = None,
            name: str = "default",
            enabled: Literal[True, False] = True,
            scores: list[int] = [1, 2, 3]
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.choices.options == ('light', 'dark', 'auto')
        assert theme.default == 'light'
        assert theme.optional is None
        
        tags = get_param(result, 'tags')
        assert tags.list is not None
        assert tags.optional is not None
        assert tags.optional.enabled is False
        
        priority = get_param(result, 'priority')
        assert priority.choices is not None
        assert priority.choices.options == (1, 2, 3)
        assert priority.optional.enabled is False
        assert priority.default is None
        
        name = get_param(result, 'name')
        assert name.choices is None
        assert name.default == "default"
        
        enabled = get_param(result, 'enabled')
        assert enabled.choices is not None
        assert enabled.choices.options == (True, False)
        assert enabled.default is True
        
        scores = get_param(result, 'scores')
        assert scores.list is not None
        assert scores.default == [1, 2, 3]
    
    def test_literal_with_constraints_on_other_params(self):
        def func(
            theme: Literal['dark', 'light'],
            age: Annotated[int, Field(ge=0, le=120)],
            email: Annotated[str, Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')],
            priority: Literal[1, 2, 3, 4, 5],
            status: Literal['active', 'inactive', 'pending'] = 'active'
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.choices.options == ('dark', 'light')
        assert theme.constraints is None
        
        status = get_param(result, 'status')
        assert status.choices.options == ('active', 'inactive', 'pending')
        
        priority = get_param(result, 'priority')
        assert priority.choices.options == (1, 2, 3, 4, 5)
        
        age = get_param(result, 'age')
        assert age.constraints is not None
        
        email_param = get_param(result, 'email')
        assert email_param.constraints is not None
        
        assert age.choices is None
        assert email_param.choices is None
    
    def test_all_literal_types_in_one_function(self):
        def func(
            str_lit: Literal['a', 'b', 'c'],
            int_lit: Literal[1, 2, 3],
            float_lit: Literal[1.1, 2.2, 3.3],
            bool_lit: Literal[True, False],
            str_opt: Literal['x', 'y'] | None = None,
            int_opt: Literal[10, 20] | None = None,
            float_opt: Literal[0.5, 1.5] | None = None,
            bool_opt: Literal[True, False] | None = None
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'str_lit').param_type == str
        assert get_param(result, 'int_lit').param_type == int
        assert get_param(result, 'float_lit').param_type == float
        assert get_param(result, 'bool_lit').param_type == bool
        assert get_param(result, 'str_opt').param_type == str
        assert get_param(result, 'int_opt').param_type == int
        assert get_param(result, 'float_opt').param_type == float
        assert get_param(result, 'bool_opt').param_type == bool
        
        for param in result:
            assert param.choices is not None
            assert param.choices.options is not None
        
        assert get_param(result, 'str_opt').optional is not None
        assert get_param(result, 'int_opt').optional is not None
        assert get_param(result, 'float_opt').optional is not None
        assert get_param(result, 'bool_opt').optional is not None
    
    def test_literal_extreme_edge_cases_combined(self):
        def func(
            empty_str: Literal['', 'a'],
            zero_int: Literal[0, 1],
            zero_float: Literal[0.0, 1.0],
            negative_int: Literal[-5, -3, -1, 0, 1, 3, 5],
            negative_float: Literal[-1.5, 0.0, 1.5],
            single_option: Literal['only'],
            many_options: Literal['o1', 'o2', 'o3', 'o4', 'o5', 'o6', 'o7', 'o8', 'o9', 'o10'],
            unicode_str: Literal['こんにちは', 'мир', 'ñoño'],
            special_chars: Literal['hello-world', 'test_value', 'option.1', 'path/to/file']
        ): pass
        result = analyze_function(func)
        
        assert '' in get_param(result, 'empty_str').choices.options
        assert len(get_param(result, 'empty_str').choices.options) == 2
        
        assert 0 in get_param(result, 'zero_int').choices.options
        assert 0.0 in get_param(result, 'zero_float').choices.options
        
        assert -5 in get_param(result, 'negative_int').choices.options
        assert -1.5 in get_param(result, 'negative_float').choices.options
        
        assert len(get_param(result, 'single_option').choices.options) == 1
        
        assert len(get_param(result, 'many_options').choices.options) == 10
        
        assert 'こんにちは' in get_param(result, 'unicode_str').choices.options
        
        assert 'hello-world' in get_param(result, 'special_chars').choices.options
        assert 'path/to/file' in get_param(result, 'special_chars').choices.options
    
    def test_literal_all_defaults_edge_cases(self):
        def func(
            first: Literal['a', 'b', 'c'] = 'a',
            middle: Literal['x', 'y', 'z'] = 'y',
            last: Literal['1', '2', '3'] = '3',
            empty: Literal['', 'a'] = '',
            zero_int: Literal[0, 1, 2] = 0,
            zero_float: Literal[0.0, 1.0] = 0.0,
            negative: Literal[-5, -3, -1] = -3,
            true_val: Literal[True, False] = True,
            false_val: Literal[True, False] = False,
            single: Literal['only'] = 'only'
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'first').default == 'a'
        assert get_param(result, 'middle').default == 'y'
        assert get_param(result, 'last').default == '3'
        assert get_param(result, 'empty').default == ''
        assert get_param(result, 'zero_int').default == 0
        assert get_param(result, 'zero_float').default == 0.0
        assert get_param(result, 'negative').default == -3
        assert get_param(result, 'true_val').default is True
        assert get_param(result, 'false_val').default is False
        assert get_param(result, 'single').default == 'only'
    
    def test_literal_optional_all_combinations(self):
        def func(
            opt_none_no_def: Literal['a', 'b'] | None,
            opt_enabled_no_def: Literal['p', 'q'] | OptionalEnabled,
            opt_disabled_no_def: Literal['t', 'u'] | OptionalDisabled,
            opt_none_with_def: Literal['x', 'y'] | None = 'x',
            opt_none_none_def: Literal['m', 'n'] | None = None,
            opt_enabled_with_def: Literal['r', 's'] | OptionalEnabled = 'r',
            opt_disabled_with_def: Literal['v', 'w'] | OptionalDisabled = 'v'
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'opt_none_no_def').optional.enabled is False
        assert get_param(result, 'opt_none_no_def').default is None
        
        assert get_param(result, 'opt_none_with_def').optional.enabled is True
        assert get_param(result, 'opt_none_with_def').default == 'x'
        
        assert get_param(result, 'opt_none_none_def').optional.enabled is False
        assert get_param(result, 'opt_none_none_def').default is None
        
        assert get_param(result, 'opt_enabled_no_def').optional.enabled is True
        assert get_param(result, 'opt_enabled_no_def').default is None
        
        assert get_param(result, 'opt_enabled_with_def').optional.enabled is True
        assert get_param(result, 'opt_enabled_with_def').default == 'r'
        
        assert get_param(result, 'opt_disabled_no_def').optional.enabled is False
        assert get_param(result, 'opt_disabled_no_def').default is None
        
        assert get_param(result, 'opt_disabled_with_def').optional.enabled is False
        assert get_param(result, 'opt_disabled_with_def').default == 'v'
    
    def test_literal_stress_test_20_params(self):
        def func(
            p1: Literal['a', 'b'],
            p2: Literal[1, 2],
            p3: Literal[True, False],
            p6: Literal['opt1', 'opt2'] | None,
            p7: Literal[100, 200] | None,
            p9: Literal[0.1, 0.2, 0.3],
            p14: Literal['unicode', 'ñ', '世界'],
            p16: Literal['long-option-name', 'another-long-one'],
            p17: Literal[999, 1000, 1001],
            p19: Literal['a1', 'a2', 'a3', 'a4', 'a5'],
            p4: Literal['x', 'y', 'z'] = 'x',
            p5: Literal[10, 20, 30] = 10,
            p8: Literal['m', 'n'] = 'm',
            p10: Literal['test', 'prod', 'dev'] = 'dev',
            p11: Literal[True] = True,
            p12: Literal['', 'nonempty'] = '',
            p13: Literal[-1, 0, 1] = 0,
            p15: Literal[1.1, 2.2] | None = 1.1,
            p18: Literal[False] = False,
            p20: Literal['final'] = 'final'
        ): pass
        result = analyze_function(func)
        
        assert len(result) == 20
        
        for param in result:
            assert param.choices is not None, f"{param.name} missing choices"
            assert param.choices.options is not None, f"{param.name} missing options"
        
        assert get_param(result, 'p1').param_type == str
        assert get_param(result, 'p2').param_type == int
        assert get_param(result, 'p3').param_type == bool
        assert get_param(result, 'p4').default == 'x'
        assert get_param(result, 'p6').optional is not None
        assert get_param(result, 'p9').param_type == float
        assert get_param(result, 'p12').default == ''
        assert get_param(result, 'p13').default == 0
        assert '世界' in get_param(result, 'p14').choices.options
        assert get_param(result, 'p20').default == 'final'
    
    def test_literal_chaos_invalid_combinations(self):
        def func1(x: Literal['a', 1, True]): pass
        with pytest.raises(TypeError, match="has mixed types"):
            analyze_function(func1)
        
        def func2(x: Literal['a', 'b'] = 'c'): pass
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func2)
        
        def func3(x: Literal[1, 2, 3] = 'not_int'): pass
        with pytest.raises(ValueError, match="default not in Literal options"):
            analyze_function(func3)
        
        def func4(x: Literal[()]): pass
        with pytest.raises(ValueError, match="must have at least one option"):
            analyze_function(func4)
    
    def test_literal_with_type_aliases_and_special_types(self):
        def func(
            theme: Literal['light', 'dark'],
            color: Color,
            email: Email,
            size: Literal['S', 'M', 'L', 'XL'],
            priority: Literal[1, 2, 3] = 2
        ): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.choices.options == ('light', 'dark')
        
        priority = get_param(result, 'priority')
        assert priority.choices.options == (1, 2, 3)
        
        size = get_param(result, 'size')
        assert size.choices.options == ('S', 'M', 'L', 'XL')
        
        color = get_param(result, 'color')
        assert color.choices is None
        assert color.constraints is not None
        
        email_param = get_param(result, 'email')
        assert email_param.choices is None
        assert email_param.constraints is not None
    
    def test_literal_boundary_values_all_types(self):
        def func(
            int_boundaries: Literal[-2147483648, 0, 2147483647],
            float_boundaries: Literal[-1.7976931348623157e+308, 0.0, 1.7976931348623157e+308],
            small_floats: Literal[1e-10, 1e-5, 1e-1],
            large_ints: Literal[1000000, 10000000, 100000000]
        ): pass
        result = analyze_function(func)
        
        int_boundaries = get_param(result, 'int_boundaries')
        assert int_boundaries.param_type == int
        assert 0 in int_boundaries.choices.options
        
        float_boundaries = get_param(result, 'float_boundaries')
        assert float_boundaries.param_type == float
        assert 0.0 in float_boundaries.choices.options
        
        small_floats = get_param(result, 'small_floats')
        assert small_floats.param_type == float
        assert 1e-10 in small_floats.choices.options
        
        large_ints = get_param(result, 'large_ints')
        assert large_ints.param_type == int
        assert 100000000 in large_ints.choices.options
    
    def test_literal_preserves_metadata_through_pipeline(self):
        def func(
            b: Literal[1, 2, 3],
            a: Literal['opt1', 'opt2', 'opt3'] | None = 'opt1'
        ): pass
        result = analyze_function(func)
        
        a = get_param(result, 'a')
        assert a.choices is not None
        assert a.choices.options == ('opt1', 'opt2', 'opt3')
        assert a.optional is not None
        assert a.optional.enabled is True
        assert a.default == 'opt1'
        assert a.param_type == str
        assert a.choices.options_function is None
        assert a.choices.enum_class is None
        
        b = get_param(result, 'b')
        assert b.choices is not None
        assert b.choices.options == (1, 2, 3)
        assert b.optional is None
        assert b.default is None
        assert b.param_type == int
    
    def test_literal_function_with_everything(self):
        def func(
            priority: Literal[1, 2, 3, 4, 5],
            scores: list[Annotated[int, Field(ge=0, le=100)]],
            name: Annotated[str, Field(min_length=2, max_length=50)],
            email: Email,
            status: Literal['active', 'inactive', 'pending'] | None,
            theme: Literal['light', 'dark', 'auto'] = 'light',
            enabled: Literal[True, False] = True,
            ratio: Literal[0.25, 0.5, 0.75, 1.0] = 0.5,
            level: Literal[1, 2, 3] | OptionalEnabled = 2,
            flag: Literal[True, False] | OptionalDisabled = False,
            tags: list[str] | None = None,
            numbers: list[int] = [1, 2, 3],
            age: Annotated[int, Field(ge=0, le=120)] = 25,
            color: Color = "#FF0000",
            count: int = 0,
            description: str | None = None
        ): pass
        
        result = analyze_function(func)
        
        assert len(result) == 16
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.choices.options == ('light', 'dark', 'auto')
        
        priority = get_param(result, 'priority')
        assert priority.choices.options == (1, 2, 3, 4, 5)
        
        enabled = get_param(result, 'enabled')
        assert enabled.choices.options == (True, False)
        
        ratio = get_param(result, 'ratio')
        assert ratio.choices.options == (0.25, 0.5, 0.75, 1.0)
        
        status = get_param(result, 'status')
        assert status.choices is not None
        assert status.choices.options == ('active', 'inactive', 'pending')
        assert status.optional.enabled is False
        
        level = get_param(result, 'level')
        assert level.optional.enabled is True
        assert level.default == 2
        
        flag = get_param(result, 'flag')
        assert flag.optional.enabled is False
        assert flag.default is False
        
        tags = get_param(result, 'tags')
        assert tags.list is not None
        assert tags.optional.enabled is False
        
        numbers = get_param(result, 'numbers')
        assert numbers.list is not None
        assert numbers.default == [1, 2, 3]
        
        scores_param = get_param(result, 'scores')
        assert scores_param.list is not None
        assert scores_param.constraints is not None
        
        age_param = get_param(result, 'age')
        assert age_param.constraints is not None
        assert age_param.default == 25
        
        name_param = get_param(result, 'name')
        assert name_param.constraints is not None
        
        color_param = get_param(result, 'color')
        assert color_param.constraints is not None
        assert color_param.default == "#FF0000"
        
        email_param = get_param(result, 'email')
        assert email_param.constraints is not None
        
        count = get_param(result, 'count')
        assert count.choices is None
        assert count.default == 0
        
        description = get_param(result, 'description')
        assert description.optional.enabled is False


class TestSpecialTypesComplexCombinations:
    def test_color_optional_list_with_default(self):
        def func(colors: list[Color] | None = ["#FF0000", "#00FF00"]): pass
        result = analyze_function(func)
        
        colors = get_param(result, 'colors')
        assert colors.widget_type == 'Color'
        assert colors.list is not None
        assert colors.optional.enabled is True
        assert colors.default == ["#FF0000", "#00FF00"]
    
    def test_email_list_with_constraints(self):
        def func(emails: Annotated[list[Email], Field(min_length=1, max_length=5)]): pass
        result = analyze_function(func)
        
        emails = get_param(result, 'emails')
        assert emails.widget_type == 'Email'
        assert emails.list is not None
        assert emails.list.constraints is not None
    
    def test_image_optional_enabled_no_default(self):
        def func(avatar: ImageFile | OptionalEnabled): pass
        result = analyze_function(func)
        
        avatar = get_param(result, 'avatar')
        assert avatar.widget_type == 'ImageFile'
        assert avatar.optional.enabled is True
        assert avatar.default is None
    
    def test_file_optional_disabled_with_default(self):
        def func(attachment: File | OptionalDisabled = "default.txt"): pass
        result = analyze_function(func)
        
        attachment = get_param(result, 'attachment')
        assert attachment.widget_type == 'File'
        assert attachment.optional.enabled is False
        assert attachment.default == "default.txt"
    
    def test_color_short_hex_default(self):
        def func(color: Color = "#F00"): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        assert color.widget_type == 'Color'
        assert color.default == "#F00"
    
    def test_multiple_special_types_optional(self):
        def func(
            color: Color | None = None,
            email: Email | None = None,
            photo: ImageFile | None = None
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'color').widget_type == 'Color'
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'photo').widget_type == 'ImageFile'
        for param in result:
            assert param.optional.enabled is False


class TestLiteralComplexCombinations:
    
    def test_literal_optional_enabled_with_default(self):
        def func(theme: Literal['light', 'dark'] | OptionalEnabled = 'light'): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.optional.enabled is True
        assert theme.default == 'light'
    
    def test_literal_optional_disabled_with_default(self):
        def func(mode: Literal['auto', 'manual'] | OptionalDisabled = 'auto'): pass
        result = analyze_function(func)
        
        mode = get_param(result, 'mode')
        assert mode.choices is not None
        assert mode.optional.enabled is False
        assert mode.default == 'auto'
    
    def test_literal_single_value_optional(self):
        def func(fixed: Literal['only_option'] | None): pass
        result = analyze_function(func)
        
        fixed = get_param(result, 'fixed')
        assert fixed.choices.options == ('only_option',)
        assert fixed.optional.enabled is False
    
    def test_literal_many_values_with_default_last(self):
        def func(
            priority: Literal['lowest', 'low', 'medium', 'high', 'highest'] = 'highest'
        ): pass
        result = analyze_function(func)
        
        priority = get_param(result, 'priority')
        assert priority.default == 'highest'
        assert len(priority.choices.options) == 5


class TestEnumComplexCombinations:
    def test_enum_optional_enabled(self):
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        def func(status: Status | OptionalEnabled): pass
        result = analyze_function(func)
        
        status = get_param(result, 'status')
        assert status.choices.enum_class == Status
        assert status.optional.enabled is True
        assert status.default is None
    
    def test_enum_optional_disabled_with_default(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(priority: Priority | OptionalDisabled = Priority.LOW): pass
        result = analyze_function(func)
        
        priority = get_param(result, 'priority')
        assert priority.choices.enum_class == Priority
        assert priority.optional.enabled is False
        assert priority.default == 1
    
    def test_enum_single_member(self):
        class Single(Enum):
            ONLY = 'only'
        
        def func(x: Single): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.enum_class == Single
        assert x.choices.options == ('only',)
    
    def test_enum_negative_int_values(self):
        class Temperature(Enum):
            COLD = -10
            NORMAL = 0
            HOT = 10
        
        def func(temp: Temperature): pass
        result = analyze_function(func)
        
        temp = get_param(result, 'temp')
        assert temp.param_type == int
        assert temp.choices.options == (-10, 0, 10)
    
    def test_enum_float_values(self):
        class Rating(Enum):
            BAD = 1.5
            GOOD = 3.0
            EXCELLENT = 5.0
        
        def func(rating: Rating): pass
        result = analyze_function(func)
        
        rating = get_param(result, 'rating')
        assert rating.param_type == float
        assert rating.choices.options == (1.5, 3.0, 5.0)


class TestDropdownComplexCombinations:
    def test_dropdown_optional_enabled(self):
        def get_options():
            return ['opt1', 'opt2']
        
        def func(x: Annotated[str, Dropdown(get_options)] | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options_function == get_options
        assert x.optional.enabled is True
    
    def test_dropdown_optional_with_default(self):
        def get_themes():
            return ['light', 'dark', 'auto']
        
        def func(theme: Annotated[str, Dropdown(get_themes)] | None = 'dark'): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices.options_function == get_themes
        assert theme.optional.enabled is True
        assert theme.default == 'dark'
    
    def test_dropdown_lambda(self):
        def func(x: Annotated[str, Dropdown(lambda: ['a', 'b', 'c'])]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert callable(x.choices.options_function)
        assert x.choices.options == ('a', 'b', 'c')
    
    def test_dropdown_int_values(self):
        def get_numbers():
            return [1, 2, 3, 4, 5]
        
        def func(num: Annotated[int, Dropdown(get_numbers)] = 3): pass
        result = analyze_function(func)
        
        num = get_param(result, 'num')
        assert num.param_type == int
        assert num.default == 3
    
    def test_dropdown_single_value(self):
        def get_single():
            return ['only']
        
        def func(x: Annotated[str, Dropdown(get_single)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('only',)


class TestListBoundaryCases:
    def test_list_min_length_zero(self):
        def func(items: Annotated[list[int], Field(min_length=0)]): pass
        result = analyze_function(func)
        
        items = get_param(result, 'items')
        assert items.list is not None
        assert items.list.constraints is not None
    
    def test_list_max_length_one(self):
        def func(items: Annotated[list[str], Field(max_length=1)]): pass
        result = analyze_function(func)
        
        items = get_param(result, 'items')
        assert items.list is not None
    
    def test_list_exact_length(self):
        def func(pair: Annotated[list[int], Field(min_length=2, max_length=2)]): pass
        result = analyze_function(func)
        
        pair = get_param(result, 'pair')
        assert pair.list.constraints is not None
    
    def test_list_with_default_empty_becomes_none(self):
        def func(items: list[int] = []): pass
        result = analyze_function(func)
        
        items = get_param(result, 'items')
        assert items.default is None
    
    def test_list_with_default_single_item(self):
        def func(items: list[str] = ["single"]): pass
        result = analyze_function(func)
        
        items = get_param(result, 'items')
        assert items.default == ["single"]
    
    def test_list_optional_enabled_empty_default(self):
        def func(items: list[int] | OptionalEnabled = []): pass
        result = analyze_function(func)
        
        items = get_param(result, 'items')
        assert items.optional.enabled is True
        assert items.default is None
    
    def test_list_item_and_list_constraints_extreme(self):
        def func(
            scores: Annotated[
                list[Annotated[int, Field(ge=0, le=100)]],
                Field(min_length=1, max_length=100)
            ]
        ): pass
        result = analyze_function(func)
        
        scores = get_param(result, 'scores')
        assert scores.constraints is not None
        assert scores.list.constraints is not None


class TestOptionalContradictions:
    def test_optional_enabled_with_none_default(self):
        def func(x: int | OptionalEnabled = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is None
    
    def test_optional_disabled_with_value_default(self):
        def func(x: int | OptionalDisabled = 42): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default == 42
    
    def test_optional_none_explicit_none_default(self):
        def func(x: str | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
        assert x.default is None
    
    def test_optional_auto_enabled_with_zero(self):
        def func(x: int | None = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == 0
    
    def test_optional_auto_enabled_with_empty_string(self):
        def func(x: str | None = ""): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default == ""
    
    def test_optional_auto_enabled_with_false(self):
        def func(x: bool | None = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True
        assert x.default is False


class TestFieldConstraintsBoundaries:
    def test_int_ge_equals_le(self):
        def func(x: Annotated[int, Field(ge=5, le=5)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_float_gt_lt_tiny_range(self):
        def func(x: Annotated[float, Field(gt=0.0, lt=0.1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_str_min_equals_max_length(self):
        def func(code: Annotated[str, Field(min_length=5, max_length=5)]): pass
        result = analyze_function(func)
        
        code = get_param(result, 'code')
        assert code.constraints is not None
    
    def test_int_with_default_at_boundary_ge(self):
        def func(x: Annotated[int, Field(ge=10)] = 10): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 10
    
    def test_int_with_default_at_boundary_le(self):
        def func(x: Annotated[int, Field(le=100)] = 100): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 100
    
    def test_str_with_default_at_min_length(self):
        def func(x: Annotated[str, Field(min_length=3)] = "abc"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "abc"
    
    def test_str_with_default_at_max_length(self):
        def func(x: Annotated[str, Field(max_length=5)] = "abcde"): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == "abcde"


class TestInvalidComplexCombinations:
    def test_list_of_list_not_supported(self):
        def func(matrix: list[list[int]]): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_union_three_types(self):
        def func(x: int | str | float): pass
        
        with pytest.raises(TypeError, match="multiple non-None types"):
            analyze_function(func)
    
    def test_union_two_non_none_types(self):
        def func(x: int | str): pass
        
        with pytest.raises(TypeError, match="multiple non-None types"):
            analyze_function(func)
    
    def test_optional_with_invalid_marker(self):
        class BadMarker:
            pass
        
        def func(x: int | Annotated[None, BadMarker()]): pass
        
        with pytest.raises(TypeError, match="Invalid marker"):
            analyze_function(func)
    
    def test_dropdown_returns_dict(self):
        def bad_func():
            return {'key': 'value'}
        
        def func(x: Annotated[str, Dropdown(bad_func)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_returns_none(self):
        def bad_func():
            return None
        
        def func(x: Annotated[str, Dropdown(bad_func)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_not_callable(self):
        with pytest.raises(TypeError, match="must be callable"):
            def func(x: Annotated[str, Dropdown("not_a_function")]): pass
    
    def test_enum_empty(self):
        class Empty(Enum):
            pass
        
        def func(x: Empty): pass
        
        with pytest.raises(ValueError, match="must have at least one value"):
            analyze_function(func)
    
    def test_literal_empty(self):
        def func(x: Literal[()]): pass
        
        with pytest.raises(ValueError, match="must have at least one option"):
            analyze_function(func)


class TestMegaCombinations:
    def test_everything_together_max_complexity(self):
        def func(
            color: Color,
            email: Email | None,
            tags: list[str],
            priority: Literal[1, 2, 3] = 2,
            active: bool = True,
            scores: Annotated[list[Annotated[int, Field(ge=0, le=100)]], Field(min_length=1)] | None = None,
            theme: Literal['light', 'dark'] | OptionalEnabled = 'light',
            photos: list[ImageFile] | None = None
        ): pass
        result = analyze_function(func)
        
        assert len(result) == 8
        assert get_param(result, 'color').widget_type == 'Color'
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'email').optional.enabled is False
        assert get_param(result, 'tags').list is not None
        assert get_param(result, 'priority').choices is not None
        assert get_param(result, 'priority').default == 2
        assert get_param(result, 'scores').list is not None
        assert get_param(result, 'scores').optional is not None
        assert get_param(result, 'theme').optional.enabled is True
        assert get_param(result, 'photos').widget_type == 'ImageFile'
    
    def test_all_types_with_all_modifiers(self):
        def func(
            a: int,
            b: int | None,
            d: Annotated[int, Field(ge=0)],
            f: list[int],
            e: Annotated[int, Field(ge=0)] | None,
            g: list[int] | None,
            h: list[Annotated[int, Field(ge=0)]],
            i: Literal[1, 2, 3],
            j: Literal[1, 2] | None,
            c: int = 5,
        ): pass
        result = analyze_function(func)
        
        assert len(result) == 10
        assert get_param(result, 'a').optional is None
        assert get_param(result, 'b').optional.enabled is False
        assert get_param(result, 'c').default == 5
        assert get_param(result, 'd').constraints is not None
        assert get_param(result, 'e').constraints is not None
        assert get_param(result, 'e').optional.enabled is False
        assert get_param(result, 'f').list is not None
        assert get_param(result, 'g').list is not None
        assert get_param(result, 'g').optional is not None
        assert get_param(result, 'h').constraints is not None
        assert get_param(result, 'i').choices is not None
        assert get_param(result, 'j').choices is not None
        assert get_param(result, 'j').optional.enabled is False
    
    def test_special_types_all_combinations(self):
        def func(
            c1: Color,
            c2: Color | None,
            c4: list[Color],
            e1: Email,
            e2: Email | OptionalEnabled,
            c5: list[Color] | None,
            c3: Color = "#FFF",
            i1: ImageFile | None = None
        ): pass
        result = analyze_function(func)
        
        for param in result:
            assert param.widget_type in ['Color', 'Email', 'ImageFile']


class TestDateTimeBoundaries:
    def test_date_with_constraints(self):
        def func(birth_date: Annotated[date, Field(ge=date(1900, 1, 1), le=date(2100, 12, 31))]): pass
        result = analyze_function(func)
        
        birth_date = get_param(result, 'birth_date')
        assert birth_date.param_type == date
        assert birth_date.constraints is not None
    
    def test_time_with_constraints(self):
        def func(start_time: Annotated[time, Field(ge=time(9, 0), le=time(17, 0))]): pass
        result = analyze_function(func)
        
        start_time = get_param(result, 'start_time')
        assert start_time.param_type == time
        assert start_time.constraints is not None
    
    def test_date_optional_with_default(self):
        def func(deadline: date | None = date(2025, 12, 31)): pass
        result = analyze_function(func)
        
        deadline = get_param(result, 'deadline')
        assert deadline.optional.enabled is True
        assert deadline.default == date(2025, 12, 31)
    
    def test_time_list(self):
        def func(schedule: list[time]): pass
        result = analyze_function(func)
        
        schedule = get_param(result, 'schedule')
        assert schedule.param_type == time
        assert schedule.list is not None


class TestBoolEdgeCases:
    def test_bool_with_true_default(self):
        def func(active: bool = True): pass
        result = analyze_function(func)
        
        active = get_param(result, 'active')
        assert active.default is True
    
    def test_bool_with_false_default(self):
        def func(disabled: bool = False): pass
        result = analyze_function(func)
        
        disabled = get_param(result, 'disabled')
        assert disabled.default is False
    
    def test_bool_optional_true_default(self):
        def func(flag: bool | None = True): pass
        result = analyze_function(func)
        
        flag = get_param(result, 'flag')
        assert flag.optional.enabled is True
        assert flag.default is True
    
    def test_bool_optional_false_default(self):
        def func(flag: bool | None = False): pass
        result = analyze_function(func)
        
        flag = get_param(result, 'flag')
        assert flag.optional.enabled is True
        assert flag.default is False
    
    def test_bool_literal(self):
        def func(flag: Literal[True, False]): pass
        result = analyze_function(func)
        
        flag = get_param(result, 'flag')
        assert flag.param_type == bool
        assert flag.choices is not None


class TestFloatEdgeCases:
    def test_float_negative_range(self):
        def func(temp: Annotated[float, Field(ge=-273.15, le=0.0)]): pass
        result = analyze_function(func)
        
        temp = get_param(result, 'temp')
        assert temp.constraints is not None
    
    def test_float_scientific_notation_default(self):
        def func(epsilon: float = 1e-6): pass
        result = analyze_function(func)
        
        epsilon = get_param(result, 'epsilon')
        assert epsilon.default == 1e-6
    
    def test_float_zero_default(self):
        def func(offset: float = 0.0): pass
        result = analyze_function(func)
        
        offset = get_param(result, 'offset')
        assert offset.default == 0.0
    
    def test_float_percentage_range(self):
        def func(percent: Annotated[float, Field(ge=0.0, le=1.0)]): pass
        result = analyze_function(func)
        
        percent = get_param(result, 'percent')
        assert percent.constraints is not None


class TestStringEdgeCases:
    def test_str_empty_default(self):
        def func(text: str = ""): pass
        result = analyze_function(func)
        
        text = get_param(result, 'text')
        assert text.default == ""
    
    def test_str_multiline_default(self):
        def func(bio: str = "Line 1\nLine 2\nLine 3"): pass
        result = analyze_function(func)
        
        bio = get_param(result, 'bio')
        assert bio.default == "Line 1\nLine 2\nLine 3"
    
    def test_str_unicode_default(self):
        def func(name: str = "José García"): pass
        result = analyze_function(func)
        
        name = get_param(result, 'name')
        assert name.default == "José García"
    
    def test_str_special_chars_default(self):
        def func(symbols: str = "!@#$%^&*()"): pass
        result = analyze_function(func)
        
        symbols = get_param(result, 'symbols')
        assert symbols.default == "!@#$%^&*()"
    
    def test_str_pattern_url(self):
        def func(url: Annotated[str, Field(pattern=r'^https?://')]): pass
        result = analyze_function(func)
        
        url = get_param(result, 'url')
        assert url.constraints is not None
        assert url.widget_type is None


class TestResultStructure:
    def test_param_name_always_set(self):
        def func(username: str, age: int, email: str): pass
        result = analyze_function(func)
        
        assert get_param(result, 'username').name == 'username'
        assert get_param(result, 'age').name == 'age'
        assert get_param(result, 'email').name == 'email'
    
    def test_type_always_set_all_types(self):
        def func(a: int, b: str, c: float, d: bool, e: date, f: time): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').param_type == int
        assert get_param(result, 'b').param_type == str
        assert get_param(result, 'c').param_type == float
        assert get_param(result, 'd').param_type == bool
        assert get_param(result, 'e').param_type == date
        assert get_param(result, 'f').param_type == time
    
    def test_all_fields_present_on_every_param(self):
        def func(x: int): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert hasattr(x, 'name')
        assert hasattr(x, 'param_type')
        assert hasattr(x, 'default')
        assert hasattr(x, 'constraints')
        assert hasattr(x, 'widget_type')
        assert hasattr(x, 'optional')
        assert hasattr(x, 'list')
        assert hasattr(x, 'choices')
    
    def test_none_values_when_not_applicable(self):
        def func(x: int = 5): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is None
        assert x.widget_type is None
        assert x.optional is None
        assert x.list is None
        assert x.choices is None
    
    def test_result_is_list(self):
        def func(a: int, b: str): pass
        result = analyze_function(func)
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_empty_list_for_no_params(self):
        def func(): pass
        result = analyze_function(func)
        
        assert result == []
        assert len(result) == 0


class TestEmptyAndSpecialFunctions:
    def test_function_no_parameters(self):
        def func(): pass
        result = analyze_function(func)
        
        assert result == []
        assert len(result) == 0
    
    def test_function_only_return_annotation(self):
        def func() -> str: 
            return "hello"
        result = analyze_function(func)
        
        assert result == []
    
    def test_function_with_docstring_no_params(self):
        def func():
            """This function does nothing"""
            pass
        result = analyze_function(func)
        
        assert result == []
    
    def test_lambda_function(self):
        func = lambda x: x
        
        with pytest.raises(TypeError):
            analyze_function(func)


class TestParameterOrder:
    def test_preserves_parameter_order(self):
        def func(z: str, a: int, m: float, b: bool): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert names == ['z', 'a', 'm', 'b']
    
    def test_required_before_optional_order(self):
        def func(req1: int, req2: str, opt1: int = 5, opt2: str = "test"): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert names == ['req1', 'req2', 'opt1', 'opt2']
    
    def test_alphabetical_not_enforced(self):
        def func(zebra: str, apple: int, banana: float): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert names == ['zebra', 'apple', 'banana']
    
    def test_single_character_param_names(self):
        def func(a: int, b: int, c: int, x: str, y: str, z: str): pass
        result = analyze_function(func)
        
        assert len(result) == 6
        names = [param.name for param in result]
        assert names == ['a', 'b', 'c', 'x', 'y', 'z']


class TestUnicodeAndSpecialNames:
    def test_unicode_parameter_names(self):
        def func(año: int, nombre: str, contraseña: str): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert 'año' in names
        assert 'nombre' in names
        assert 'contraseña' in names
    
    def test_chinese_characters_param_names(self):
        def func(姓名: str, 年龄: int): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert '姓名' in names
        assert '年龄' in names
    
    def test_underscore_param_names(self):
        def func(_private: int, normal_: float): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert '_private' in names
        assert 'normal_' in names
    
    def test_long_parameter_name(self):
        def func(this_is_a_very_long_parameter_name_for_testing_purposes: int): pass
        result = analyze_function(func)
        
        names = [param.name for param in result]
        assert 'this_is_a_very_long_parameter_name_for_testing_purposes' in names


class TestEnumParamVsSpecialTypeMutualExclusivity:
    def test_color_has_special_type_not_enum(self):
        def func(color: Color): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        assert color.widget_type == 'Color'
        assert color.choices is None
    
    def test_email_has_special_type_not_enum(self):
        def func(email: Email): pass
        result = analyze_function(func)
        
        email = get_param(result, 'email')
        assert email.widget_type == 'Email'
        assert email.choices is None
    
    def test_literal_has_enum_not_special_type(self):
        def func(theme: Literal['light', 'dark']): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.choices is not None
        assert theme.widget_type is None
    
    def test_enum_has_enum_param_not_special_type(self):
        class Status(Enum):
            ACTIVE = 'active'
        
        def func(status: Status): pass
        result = analyze_function(func)
        
        status = get_param(result, 'status')
        assert status.choices is not None
        assert status.widget_type is None
    
    def test_dropdown_has_enum_not_special_type(self):
        def get_opts():
            return ['a', 'b']
        
        def func(x: Annotated[str, Dropdown(get_opts)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices is not None
        assert x.widget_type is None
    
    def test_regular_param_has_neither(self):
        def func(name: str): pass
        result = analyze_function(func)
        
        name = get_param(result, 'name')
        assert name.widget_type is None
        assert name.choices is None


class TestEnumDefaultConversion:
    def test_enum_default_converted_to_value(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(priority: Priority = Priority.LOW): pass
        result = analyze_function(func)
        
        priority = get_param(result, 'priority')
        assert priority.default == 1
        assert isinstance(priority.default, int)
        assert priority.default is not Priority.LOW
    
    def test_enum_str_value_converted(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
        
        def func(theme: Theme = Theme.DARK): pass
        result = analyze_function(func)
        
        theme = get_param(result, 'theme')
        assert theme.default == 'dark'
        assert isinstance(theme.default, str)
    
    def test_enum_bool_value_converted(self):
        class Toggle(Enum):
            ON = True
            OFF = False
        
        def func(toggle: Toggle = Toggle.ON): pass
        result = analyze_function(func)
        
        toggle = get_param(result, 'toggle')
        assert toggle.default is True
        assert isinstance(toggle.default, bool)
    
    def test_enum_float_value_converted(self):
        class Rating(Enum):
            LOW = 1.5
            HIGH = 4.5
        
        def func(rating: Rating = Rating.HIGH): pass
        result = analyze_function(func)
        
        rating = get_param(result, 'rating')
        assert rating.default == 4.5
        assert isinstance(rating.default, float)


class TestErrorMessages:
    def test_no_type_hint_shows_parameter_name(self):
        def func(missing_hint): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        assert 'missing_hint' in str(exc.value)
        assert 'has no type hint' in str(exc.value)
    
    def test_invalid_type_shows_parameter_name(self):
        def func(bad_type: dict): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        assert 'bad_type' in str(exc.value)
        assert 'are supported' in str(exc.value)
    
    def test_invalid_default_shows_parameter_name(self):
        def func(x: Annotated[int, Field(ge=0)] = -5): pass
        
        with pytest.raises(ValueError) as exc:
            analyze_function(func)
        assert 'x' in str(exc.value)
        assert 'does not satisfy' in str(exc.value)
    
    def test_literal_mixed_types_helpful_message(self):
        def func(x: Literal['a', 1]): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        assert 'x' in str(exc.value)
        assert 'mixed types' in str(exc.value).lower()
    
    def test_union_multiple_types_helpful_message(self):
        def func(x: int | str | float): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        assert 'x' in str(exc.value)
        assert 'only [type | None]' in str(exc.value)
    
    def test_enum_empty_helpful_message(self):
        class Empty(Enum):
            pass
        
        def func(x: Empty): pass
        
        with pytest.raises(ValueError) as exc:
            analyze_function(func)
        assert 'x' in str(exc.value)
        assert 'at least one value' in str(exc.value)
    
    def test_dropdown_not_callable_helpful_message(self):
        with pytest.raises(TypeError) as exc:
            def func(x: Annotated[str, Dropdown("not_callable")]): pass
        
        assert 'callable' in str(exc.value)
    
    def test_list_no_type_helpful_message(self):
        def func(x: list): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        assert 'x' in str(exc.value)
        assert 'must have a type argument' in str(exc.value)


class TestDefaultNoneVsAbsent:
    def test_no_default_is_none(self):
        def func(x: int): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
    
    def test_explicit_none_default_optional(self):
        def func(x: int | None = None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is False
    
    def test_no_default_vs_none_default_distinguishable(self):
        def func(a: int, b: int | None = None): pass
        result = analyze_function(func)
        
        a = get_param(result, 'a')
        assert a.default is None
        assert a.optional is None
        
        b = get_param(result, 'b')
        assert b.default is None
        assert b.optional is not None
    
    def test_zero_default_not_none(self):
        def func(x: int = 0): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == 0
        assert x.default is not None
    
    def test_empty_string_default_not_none(self):
        def func(x: str = ""): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ""
        assert x.default is not None
    
    def test_false_default_not_none(self):
        def func(x: bool = False): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is False
        assert x.default is not None


class TestEmptyListConversion:
    def test_empty_list_converts_to_none(self):
        def func(x: list[int] = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
    
    def test_empty_list_with_optional(self):
        def func(x: list[int] | None = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is True
    
    def test_empty_list_with_optional_enabled(self):
        def func(x: list[int] | OptionalEnabled = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
        assert x.optional.enabled is True
    
    def test_non_empty_list_not_converted(self):
        def func(x: list[int] = [1]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [1]
        assert x.default is not None


class TestSpecialTypesWithLists:
    def test_color_list_preserves_special_type(self):
        def func(colors: list[Color]): pass
        result = analyze_function(func)
        
        colors = get_param(result, 'colors')
        assert colors.widget_type == 'Color'
        assert colors.list is not None
    
    def test_email_list_preserves_special_type(self):
        def func(emails: list[Email]): pass
        result = analyze_function(func)
        
        emails = get_param(result, 'emails')
        assert emails.widget_type == 'Email'
        assert emails.list is not None
    
    def test_image_list_preserves_special_type(self):
        def func(images: list[ImageFile]): pass
        result = analyze_function(func)
        
        images = get_param(result, 'images')
        assert images.widget_type == 'ImageFile'
        assert images.list is not None
    
    def test_all_file_types_in_list(self):
        def func(
            images: list[ImageFile],
            videos: list[VideoFile],
            audios: list[AudioFile],
            datas: list[DataFile],
            texts: list[TextFile],
            docs: list[DocumentFile],
            files: list[File]
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'images').widget_type == 'ImageFile'
        assert get_param(result, 'videos').widget_type == 'VideoFile'
        assert get_param(result, 'audios').widget_type == 'AudioFile'
        assert get_param(result, 'datas').widget_type == 'DataFile'
        assert get_param(result, 'texts').widget_type == 'TextFile'
        assert get_param(result, 'docs').widget_type == 'DocumentFile'
        assert get_param(result, 'files').widget_type == 'File'


class TestLiteralExtremeValues:
    def test_literal_very_long_strings(self):
        long_str = 'a' * 1000
        def func(x: Literal['short', 'medium']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options == ('short', 'medium')
    
    def test_literal_newlines_in_strings(self):
        def func(x: Literal['line1\nline2', 'line3\nline4']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'line1\nline2' in x.choices.options
    
    def test_literal_tabs_in_strings(self):
        def func(x: Literal['col1\tcol2', 'col3\tcol4']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 'col1\tcol2' in x.choices.options
    
    def test_literal_quotes_in_strings(self):
        def func(x: Literal["it's", 'say "hello"']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert "it's" in x.choices.options
        assert 'say "hello"' in x.choices.options
    
    def test_literal_max_int(self):
        def func(x: Literal[2147483647, -2147483648]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 2147483647 in x.choices.options
        assert -2147483648 in x.choices.options
    
    def test_literal_scientific_notation_floats(self):
        def func(x: Literal[1e10, 1e-10, 1.23e5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert 1e10 in x.choices.options
        assert 1e-10 in x.choices.options


class TestDropdownExtremeEdgeCases:
    def test_dropdown_returns_generator(self):
        def get_gen():
            return (x for x in ['a', 'b'])
        
        def func(x: Annotated[str, Dropdown(get_gen)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_returns_set(self):
        def get_set():
            return {'a', 'b', 'c'}
        
        def func(x: Annotated[str, Dropdown(get_set)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_callable_class(self):
        class CallableClass:
            def __call__(self):
                return ['option1', 'option2']
        
        instance = CallableClass()
        def func(x: Annotated[str, Dropdown(instance)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.options_function == instance
        assert x.choices.options == ('option1', 'option2')
    
    def test_dropdown_with_closure(self):
        counter = [0]
        def get_opts():
            counter[0] += 1
            return [f'opt_{counter[0]}']
        
        def func(x: Annotated[str, Dropdown(get_opts)]): pass
        result = analyze_function(func)
        
        assert counter[0] == 1
        x = get_param(result, 'x')
        assert callable(x.choices.options_function)
    
    def test_dropdown_returns_none_list(self):
        def returns_none():
            return None
        
        def func(x: Annotated[str, Dropdown(returns_none)]): pass
        
        with pytest.raises(TypeError, match="must return a list or tuple"):
            analyze_function(func)
    
    def test_dropdown_raises_exception(self):
        def raises_exc():
            raise ValueError("Intentional error")
        
        def func(x: Annotated[str, Dropdown(raises_exc)]): pass
        
        with pytest.raises(ValueError, match="Dropdown function failed"):
            analyze_function(func)


class TestFieldConstraintsExtreme:
    def test_int_constraint_at_python_limit(self):
        huge = 10**100
        def func(x: Annotated[int, Field(le=huge)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_float_constraint_very_small(self):
        def func(x: Annotated[float, Field(ge=1e-100, le=1e-99)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_str_constraint_max_length_huge(self):
        def func(x: Annotated[str, Field(max_length=1000000)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_str_pattern_complex_regex(self):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        def func(x: Annotated[str, Field(pattern=pattern)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_date_constraint_very_old(self):
        def func(x: Annotated[date, Field(ge=date(1, 1, 1))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None
    
    def test_date_constraint_far_future(self):
        def func(x: Annotated[date, Field(le=date(9999, 12, 31))]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.constraints is not None


class TestMultipleEnumsInFunction:
    def test_two_different_enums(self):
        class Color(Enum):
            RED = 'red'
            BLUE = 'blue'
        
        class Size(Enum):
            SMALL = 1
            LARGE = 2
        
        def func(color: Color, size: Size): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        size = get_param(result, 'size')
        assert color.choices.enum_class == Color
        assert size.choices.enum_class == Size
        assert color.param_type == str
        assert size.param_type == int
    
    def test_enum_and_literal_and_dropdown(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def get_themes():
            return ['light', 'dark']
        
        def func(
            priority: Priority,
            status: Literal['active', 'inactive'],
            theme: Annotated[str, Dropdown(get_themes)]
        ): pass
        result = analyze_function(func)
        
        priority = get_param(result, 'priority')
        status = get_param(result, 'status')
        theme = get_param(result, 'theme')
        
        assert priority.choices.enum_class == Priority
        assert status.choices.options == ('active', 'inactive')
        assert theme.choices.options_function == get_themes
        
        assert priority.choices.options_function is None
        assert status.choices.enum_class is None
        assert theme.choices.enum_class is None


class TestNoneInDifferentContexts:
    def test_none_as_only_type_fails(self):
        def func(x: None): pass
        
        with pytest.raises(TypeError, match="cannot have only None type"):
            analyze_function(func)


class TestComplexNestedAnnotations:
    def test_annotated_in_annotated(self):
        def func(x: Annotated[Annotated[int, Field(ge=0)], Field(le=100)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.constraints is not None
    
    def test_list_of_annotated_special_type(self):
        def func(emails: list[Email]): pass
        result = analyze_function(func)
        
        emails = get_param(result, 'emails')
        assert emails.widget_type == 'Email'
        assert emails.list is not None


class TestAllTypeCombinationsInOneFunction:
    def test_every_feature_combined(self):
        class Status(Enum):
            ACTIVE = 'active'
            INACTIVE = 'inactive'
        
        def get_sizes():
            return ['S', 'M', 'L']
        
        def func(
            name: str,
            age: Annotated[int, Field(ge=0, le=120)],
            email: Email,
            color: Color,
            status: Status,
            priority: Literal[1, 2, 3],
            size: Annotated[str, Dropdown(get_sizes)],
            tags: list[str],
            scores: list[Annotated[int, Field(ge=0, le=100)]],
            files: list[ImageFile],
            bio: Annotated[str, Field(max_length=500)] | None = None,
            theme: Literal['light', 'dark'] | OptionalEnabled = 'light',
            enabled: bool = True,
            count: int = 0
        ): pass
        result = analyze_function(func)
        
        assert len(result) == 14
        assert get_param(result, 'name').param_type == str
        assert get_param(result, 'age').constraints is not None
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'color').widget_type == 'Color'
        assert get_param(result, 'status').choices.enum_class == Status
        assert get_param(result, 'priority').choices.options == (1, 2, 3)
        assert get_param(result, 'size').choices.options_function == get_sizes
        assert get_param(result, 'tags').list is not None
        assert get_param(result, 'scores').list is not None
        assert get_param(result, 'files').widget_type == 'ImageFile'
        assert get_param(result, 'bio').optional.enabled is False
        assert get_param(result, 'theme').optional.enabled is True
        assert get_param(result, 'enabled').default is True
        assert get_param(result, 'count').default == 0


class TestReturnValueIgnored:
    def test_function_with_return_type(self):
        def func(x: int) -> str:
            return "hello"
        result = analyze_function(func)
        
        assert len(result) == 1
        assert get_param(result, 'x').param_type == int
    
    def test_function_with_complex_return_type(self):
        def func(x: int) -> list[dict[str, int]]:
            return []
        result = analyze_function(func)
        
        assert len(result) == 1


class TestDefaultValidationOrder:
    def test_enum_converted_before_literal_check(self):
        class Priority(Enum):
            LOW = 1
            HIGH = 2
        
        def func(priority: Priority = Priority.LOW): pass
        result = analyze_function(func)
        
        priority = get_param(result, 'priority')
        assert priority.default == 1
        assert priority.default in priority.choices.options
    
    def test_empty_list_converted_before_list_validation(self):
        def func(x: Annotated[list[int], Field(min_length=1)] = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None


class TestOptionalParamStructure:
    def test_optional_param_has_enabled_field(self):
        def func(x: int | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert hasattr(x.optional, 'enabled')
        assert isinstance(x.optional.enabled, bool)
    
    def test_optional_disabled_structure(self):
        def func(x: int | OptionalDisabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is False
    
    def test_optional_enabled_structure(self):
        def func(x: int | OptionalEnabled): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.optional.enabled is True


class TestListParamStructure:
    def test_list_param_has_field_info(self):
        def func(x: Annotated[list[int], Field(min_length=1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert hasattr(x.list, 'constraints')
        assert x.list.constraints is not None
    
    def test_list_param_without_constraints(self):
        def func(x: list[int]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.list.constraints is None


class TestEnumParamStructure:
    def test_enum_param_has_all_fields(self):
        def func(x: Literal['a', 'b']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert hasattr(x.choices, 'enum_class')
        assert hasattr(x.choices, 'options_function')
        assert hasattr(x.choices, 'options')
    
    def test_literal_enum_param_structure(self):
        def func(x: Literal['a', 'b']): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.enum_class is None
        assert x.choices.options_function is None
        assert x.choices.options == ('a', 'b')
    
    def test_enum_enum_param_structure(self):
        class Status(Enum):
            ACTIVE = 'active'
        
        def func(x: Status): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.enum_class == Status
        assert x.choices.options_function is None
        assert x.choices.options == ('active',)
    
    def test_dropdown_enum_param_structure(self):
        def get_opts():
            return ['a', 'b']
        
        def func(x: Annotated[str, Dropdown(get_opts)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.choices.enum_class is None
        assert x.choices.options_function == get_opts
        assert x.choices.options == ('a', 'b')


class TestStressTestMassiveFunction:
    def test_50_parameters_mixed_types(self):
        def func(
            p1: int, p2: str, p3: float, p4: bool, p5: date,
            p6: int = 1, p7: str = "a", p8: float = 1.0, p9: bool = True, p10: time = time(12, 0),
            p11: int | None = None, p12: str | None = None, p13: Literal['a', 'b'] = 'a',
            p14: list[int] = [1], p15: list[str] = ["a"], p16: Annotated[int, Field(ge=0)] = 5,
            p17: Email = "test@test.com", p18: Color = "#FFF", p19: ImageFile | None = None,
            p20: int = 20, p21: str = "21", p22: float = 22.0, p23: bool = False,
            p24: date = date(2025, 1, 1), p25: time = time(0, 0),
            p26: int | None = 26, p27: str | None = "27", p28: Literal[1, 2] = 1,
            p29: list[int] = [29], p30: list[str] = ["30"],
            p31: int = 31, p32: str = "32", p33: float = 33.0, p34: bool = True,
            p35: int = 35, p36: str = "36", p37: float = 37.0, p38: bool = False,
            p39: int = 39, p40: str = "40", p41: float = 41.0, p42: bool = True,
            p43: int = 43, p44: str = "44", p45: float = 45.0, p46: bool = False,
            p47: int = 47, p48: str = "48", p49: float = 49.0, p50: bool = True
        ): pass
        result = analyze_function(func)
        
        assert len(result) == 50
        names = [param.name for param in result]
        assert all(f'p{i}' in names for i in range(1, 51))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
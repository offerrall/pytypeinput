import pytest
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pydantic import Field


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


class TestBasicLists:
    def test_list_int_no_default(self):
        def func(x: list[int]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.list is not None
        assert x.list.constraints is None
        assert x.default is None
    
    def test_list_str_no_default(self):
        def func(x: list[str]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.list is not None
    
    def test_list_float_no_default(self):
        def func(x: list[float]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == float
        assert x.list is not None
    
    def test_list_bool_no_default(self):
        def func(x: list[bool]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == bool
        assert x.list is not None
    
    def test_list_date_no_default(self):
        from datetime import date
        def func(x: list[date]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == date
        assert x.list is not None
    
    def test_list_time_no_default(self):
        from datetime import time
        def func(x: list[time]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == time
        assert x.list is not None


class TestListsWithDefaults:
    def test_list_int_with_default(self):
        def func(x: list[int] = [1, 2, 3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.default == [1, 2, 3]
    
    def test_list_str_with_default(self):
        def func(x: list[str] = ["a", "b", "c"]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ["a", "b", "c"]
    
    def test_list_float_with_default(self):
        def func(x: list[float] = [1.5, 2.5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [1.5, 2.5]
    
    def test_list_bool_with_default(self):
        def func(x: list[bool] = [True, False]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [True, False]
    
    def test_list_with_single_item_default(self):
        def func(x: list[int] = [5]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [5]
    
    def test_list_with_empty_default(self):
        def func(x: list[int] = []): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default is None
    
    def test_list_date_with_default(self):
        from datetime import date
        def func(x: list[date] = [date(2025, 1, 1), date(2025, 12, 31)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [date(2025, 1, 1), date(2025, 12, 31)]


class TestListItemConstraints:
    def test_list_int_item_ge(self):
        def func(x: list[Annotated[int, Field(ge=0)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.constraints is not None
        assert get_constraint(x.constraints, 'ge') == 0
        assert x.list is not None
        assert x.list.constraints is None
    
    def test_list_int_item_le(self):
        def func(x: list[Annotated[int, Field(le=100)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'le') == 100
    
    def test_list_int_item_range(self):
        def func(x: list[Annotated[int, Field(ge=0, le=100)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == 0
        assert get_constraint(x.constraints, 'le') == 100
    
    def test_list_str_item_min_length(self):
        def func(x: list[Annotated[str, Field(min_length=3)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert get_constraint(x.constraints, 'min_length') == 3
    
    def test_list_str_item_max_length(self):
        def func(x: list[Annotated[str, Field(max_length=20)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'max_length') == 20
    
    def test_list_str_item_pattern(self):
        def func(x: list[Annotated[str, Field(pattern=r'^[a-z]+$')]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'pattern') == r'^[a-z]+$'
    
    def test_list_float_item_range(self):
        def func(x: list[Annotated[float, Field(ge=0.0, le=1.0)]]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == 0.0
        assert get_constraint(x.constraints, 'le') == 1.0


class TestListLevelConstraints:
    def test_list_min_length(self):
        def func(x: Annotated[list[int], Field(min_length=2)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert x.list is not None
        assert x.list.constraints is not None
        assert get_constraint(x.list.constraints, 'min_length') == 2
        assert x.constraints is None
    
    def test_list_max_length(self):
        def func(x: Annotated[list[int], Field(max_length=10)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.list.constraints, 'max_length') == 10
    
    def test_list_min_max_length(self):
        def func(x: Annotated[list[str], Field(min_length=2, max_length=5)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.list.constraints, 'min_length') == 2
        assert get_constraint(x.list.constraints, 'max_length') == 5


class TestCombinedListConstraints:
    def test_list_with_both_constraints(self):
        def func(x: Annotated[list[Annotated[int, Field(ge=0, le=100)]], Field(min_length=3, max_length=10)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == int
        assert get_constraint(x.constraints, 'ge') == 0
        assert get_constraint(x.constraints, 'le') == 100
        
        assert x.list is not None
        assert get_constraint(x.list.constraints, 'min_length') == 3
        assert get_constraint(x.list.constraints, 'max_length') == 10
    
    def test_list_str_both_constraints(self):
        def func(x: Annotated[list[Annotated[str, Field(min_length=3, max_length=20)]], Field(min_length=2, max_length=5)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'min_length') == 3
        assert get_constraint(x.constraints, 'max_length') == 20
        
        assert get_constraint(x.list.constraints, 'min_length') == 2
        assert get_constraint(x.list.constraints, 'max_length') == 5
    
    def test_list_float_both_constraints(self):
        def func(x: Annotated[list[Annotated[float, Field(ge=0.0)]], Field(min_length=1)]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert get_constraint(x.constraints, 'ge') == 0.0
        assert get_constraint(x.list.constraints, 'min_length') == 1


class TestListsWithDefaultsAndConstraints:
    def test_list_int_item_constraint_valid_default(self):
        def func(x: list[Annotated[int, Field(ge=0)]] = [1, 2, 3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [1, 2, 3]
        assert get_constraint(x.constraints, 'ge') == 0
    
    def test_list_str_item_constraint_valid_default(self):
        def func(x: list[Annotated[str, Field(min_length=3)]] = ["hello", "world"]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ["hello", "world"]
    
    def test_list_level_constraint_valid_default(self):
        def func(x: Annotated[list[int], Field(min_length=2)] = [1, 2, 3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [1, 2, 3]
    
    def test_both_constraints_valid_default(self):
        def func(x: Annotated[list[Annotated[int, Field(ge=0)]], Field(min_length=2)] = [1, 2, 3]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == [1, 2, 3]


class TestMultipleListParameters:
    def test_multiple_different_list_types(self):
        def func(a: list[int], b: list[str], c: list[float]): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').param_type == int
        assert get_param(result, 'b').param_type == str
        assert get_param(result, 'c').param_type == float
    
    def test_mixed_list_and_regular(self):
        def func(a: int, b: list[int], c: str, d: list[str]): pass
        result = analyze_function(func)
        
        assert get_param(result, 'a').list is None
        assert get_param(result, 'b').list is not None
        assert get_param(result, 'c').list is None
        assert get_param(result, 'd').list is not None
    
    def test_multiple_lists_with_constraints(self):
        def func(
            a: list[Annotated[int, Field(ge=0)]],
            b: Annotated[list[str], Field(min_length=2)],
            c: Annotated[list[Annotated[float, Field(gt=0.0)]], Field(max_length=5)]
        ): pass
        result = analyze_function(func)
        
        a = get_param(result, 'a')
        assert get_constraint(a.constraints, 'ge') == 0
        
        b = get_param(result, 'b')
        assert get_constraint(b.list.constraints, 'min_length') == 2
        
        c = get_param(result, 'c')
        assert get_constraint(c.constraints, 'gt') == 0.0
        assert get_constraint(c.list.constraints, 'max_length') == 5


class TestInvalidLists:
    def test_list_no_type_parameter(self):
        def func(x: list): pass
        
        with pytest.raises(TypeError, match="must have a type argument"):
            analyze_function(func)
    
    def test_list_unsupported_item_type(self):
        def func(x: list[dict]): pass
        
        with pytest.raises(TypeError, match="are supported"):
            analyze_function(func)
    
    def test_list_invalid_default_not_list(self):
        def func(x: list[int] = 5): pass
        
        with pytest.raises(TypeError, match="default must be a list"):
            analyze_function(func)
    
    def test_list_invalid_default_wrong_item_type(self):
        def func(x: list[int] = ["a", "b"]): pass
        
        with pytest.raises(TypeError, match="list item type mismatch"):
            analyze_function(func)
    
    def test_list_invalid_default_item_violates_constraint(self):
        def func(x: list[Annotated[int, Field(ge=0)]] = [-1, 2, 3]): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)
    
    def test_list_invalid_default_too_short(self):
        def func(x: Annotated[list[int], Field(min_length=3)] = [1, 2]): pass
        
        with pytest.raises(ValueError, match="list default does not satisfy constraints"):
            analyze_function(func)
    
    def test_list_invalid_default_too_long(self):
        def func(x: Annotated[list[int], Field(max_length=2)] = [1, 2, 3]): pass
        
        with pytest.raises(ValueError, match="list default does not satisfy constraints"):
            analyze_function(func)
    
    def test_list_str_item_too_short(self):
        def func(x: list[Annotated[str, Field(min_length=5)]] = ["hi", "hello"]): pass
        
        with pytest.raises(ValueError, match="does not satisfy"):
            analyze_function(func)

    def test_list_optional(self):
        def func(x: list[int] | None): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.list is not None
        assert x.optional is not None

class TestFileListConstraints:
    """Tests for file type lists with constraints (should fail)."""
    
    def test_image_file_list_no_constraint_succeeds(self):
        """File lists without constraints should work."""
        from pytypeinput.types import ImageFile
        
        def func(x: list[ImageFile]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.param_type == str
        assert x.list is not None
        assert x.list.constraints is None
        assert x.widget_type == 'ImageFile'
    
    def test_image_file_list_with_default_no_constraint_succeeds(self):
        """File lists with defaults but no constraints should work."""
        from pytypeinput.types import ImageFile
        
        def func(x: list[ImageFile] = ["photo1.jpg", "photo2.png"]): pass
        result = analyze_function(func)
        
        x = get_param(result, 'x')
        assert x.default == ["photo1.jpg", "photo2.png"]
        assert x.list.constraints is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
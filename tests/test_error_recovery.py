import pytest
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzer import analyze_function
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestGracefulFailures:
    
    def test_multiple_errors_in_one_function(self):
        def func(
            x,
            y: dict,
            z: int = "wrong"
        ): pass
        
        with pytest.raises(TypeError):
            analyze_function(func)
    
    def test_error_includes_param_name(self):
        def func(problematic_parameter: dict): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(func)
        
        assert 'problematic_parameter' in str(exc.value)
    
    def test_error_includes_function_name(self):
        def my_special_function(x: dict): pass
        
        with pytest.raises(TypeError) as exc:
            analyze_function(my_special_function)
        
        assert 'dict' in str(exc.value).lower() or 'supported' in str(exc.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
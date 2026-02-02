import inspect
from typing import Any, Callable

from pydantic import BaseModel
from pydantic.fields import PydanticUndefined

from .param import ParamMetadata
from .analyzer import analyze_parameter

def analyze_function(func: Callable[..., Any], enable_warnings: bool = True) -> list[ParamMetadata]:
    sig = inspect.signature(func)
    return [analyze_parameter(param, enable_warnings) for param in sig.parameters.values()]


def analyze_type(annotation: Any, name: str = "field", enable_warnings: bool = True) -> ParamMetadata:
    fake_param = inspect.Parameter(
        name=name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=annotation,
        default=inspect.Parameter.empty
    )
    return analyze_parameter(fake_param, enable_warnings)

def analyze_pydantic_model(model: type[BaseModel], enable_warnings: bool = True) -> list[ParamMetadata]:

    if not issubclass(model, BaseModel):
        raise TypeError(f"{model.__name__} must be a Pydantic BaseModel")
    
    params = []
    
    for field_name, field_info in model.model_fields.items():
        annotation = model.__annotations__.get(field_name, field_info.annotation)
        
        fake_param = inspect.Parameter(
            name=field_name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotation,
            default=field_info.default if field_info.default is not PydanticUndefined else inspect.Parameter.empty
        )
        
        try:
            param_metadata = analyze_parameter(fake_param, enable_warnings)
            params.append(param_metadata)
        except TypeError as e:
            print(f"Warning: Skipping field '{field_name}': {e}")
            continue
    
    return params

def analyze_dataclass(cls: type, enable_warnings: bool = True) -> list[ParamMetadata]:
    from dataclasses import is_dataclass, fields, MISSING
    
    if not is_dataclass(cls):
        raise TypeError(f"'{cls.__name__}' is not a dataclass. Use @dataclass decorator.")
    
    params = []
    
    for dc_field in fields(cls):
        if not dc_field.init:
            continue
        
        annotation = dc_field.type
        
        if dc_field.default is not MISSING:
            default_value = dc_field.default
        elif dc_field.default_factory is not MISSING:
            try:
                default_value = dc_field.default_factory()
            except Exception as e:
                print(f"Warning: default_factory for '{dc_field.name}' failed: {e}")
                default_value = inspect.Parameter.empty
        else:
            default_value = inspect.Parameter.empty
        
        fake_param = inspect.Parameter(
            name=dc_field.name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotation,
            default=default_value
        )
        
        try:
            param_metadata = analyze_parameter(fake_param, enable_warnings)
            params.append(param_metadata)
        except TypeError as e:
            print(f"Warning: Skipping field '{dc_field.name}': {e}")
            continue
    
    return params


def analyze_class_init(cls: type, enable_warnings: bool = True) -> list[ParamMetadata]:
    if not hasattr(cls, '__init__'):
        raise TypeError(f"'{cls.__name__}' has no __init__ method")
    
    sig = inspect.signature(cls.__init__)
    
    params = []
    for param in sig.parameters.values():
        if param.name == 'self':
            continue
        
        try:
            param_metadata = analyze_parameter(param, enable_warnings)
            params.append(param_metadata)
        except TypeError as e:
            raise TypeError(f"In {cls.__name__}.__init__: {e}")
    
    return params
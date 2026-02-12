import inspect
from typing import Any, Callable, get_type_hints
from dataclasses import is_dataclass, fields, MISSING

from pydantic import BaseModel
from pydantic.fields import PydanticUndefined

from .param import ParamMetadata
from .analyzer import analyze_type


def analyze_function(func: Callable[..., Any]) -> list[ParamMetadata]:
    hints = get_type_hints(func, include_extras=True)
    sig = inspect.signature(func)
    return [
        analyze_type(
            annotation=hints[p.name],
            name=p.name,
            default=p.default,
        )
        for p in sig.parameters.values()
        if p.name in hints
    ]


def analyze_pydantic_model(model: type) -> list[ParamMetadata]:
    if not issubclass(model, BaseModel):
        raise TypeError(f"{model.__name__} is not a Pydantic BaseModel")

    return [
        analyze_type(
            annotation=info.annotation,
            name=name,
            default=info.default if info.default is not PydanticUndefined else inspect.Parameter.empty,
        )
        for name, info in model.model_fields.items()
    ]


def analyze_dataclass(cls: type) -> list[ParamMetadata]:
    if not is_dataclass(cls):
        raise TypeError(f"'{cls.__name__}' is not a dataclass")

    hints = get_type_hints(cls, include_extras=True)
    results = []
    for f in fields(cls):
        if not f.init:
            continue

        if f.default is not MISSING:
            default = f.default
        elif f.default_factory is not MISSING:
            default = f.default_factory()
        else:
            default = inspect.Parameter.empty

        results.append(analyze_type(
            annotation=hints[f.name],
            name=f.name,
            default=default,
        ))
    return results


def analyze_class_init(cls: type) -> list[ParamMetadata]:
    if not hasattr(cls, '__init__'):
        raise TypeError(f"'{cls.__name__}' has no __init__ method")

    hints = get_type_hints(cls.__init__, include_extras=True)
    sig = inspect.signature(cls.__init__)
    return [
        analyze_type(
            annotation=hints[p.name],
            name=p.name,
            default=p.default,
        )
        for p in sig.parameters.values()
        if p.name != 'self' and p.name in hints
    ]
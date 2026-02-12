import inspect
from typing import Any, Union, get_origin, get_args, Annotated
import types

from ..param import OptionalMetadata
from ..types import _OptionalEnabledMarker, _OptionalDisabledMarker


def extract_optional(
    annotation: Any, 
    default: Any
) -> tuple[Any, OptionalMetadata | None]:
    if get_origin(annotation) not in (Union, types.UnionType):
        return annotation, None
    
    union_args = get_args(annotation)
    none_count = 0
    non_none = []
    explicit_marker = None
    
    for arg in union_args:
        if arg is type(None):
            none_count += 1
        elif get_origin(arg) is Annotated and get_args(arg)[0] is type(None):
            none_count += 1
            for m in get_args(arg)[1:]:
                if isinstance(m, _OptionalEnabledMarker):
                    explicit_marker = True
                elif isinstance(m, _OptionalDisabledMarker):
                    explicit_marker = False
        else:
            non_none.append(arg)
    
    if none_count == 0:
        return annotation, None
    
    if explicit_marker is not None:
        enabled = explicit_marker
    elif default is inspect.Parameter.empty or default is None:
        enabled = False
    else:
        enabled = True
    
    return non_none[0], OptionalMetadata(enabled=enabled)
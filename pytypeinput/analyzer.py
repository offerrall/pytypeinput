import inspect
from typing import get_origin, get_args, Annotated, Union, Any
import types
from datetime import date, time
from typing import Literal
from enum import Enum
import warnings

from pydantic.fields import FieldInfo

from .param import ParamMetadata, OptionalMetadata, ListMetadata, ChoiceMetadata, UIMetadata
from .types import (
    _OptionalEnabledMarker, 
    _OptionalDisabledMarker, 
    Dropdown, 
    SPECIAL_TYPES,
    FILE_TYPE_PATTERNS
)
from .types import Step, IsPassword, Slider, Placeholder, PatternMessage, Description, Label, Rows


_VALID_TYPES = {int, float, str, bool, date, time}


def _is_file_type_pattern(pattern: str) -> bool:
    return pattern in FILE_TYPE_PATTERNS


def _detect_special_type(field_info: FieldInfo | None) -> str | None:
    if field_info is None:
        return None
    
    for constraint in field_info.metadata:
        if hasattr(constraint, 'pattern'):
            widget = SPECIAL_TYPES.get(constraint.pattern)
            if widget:
                return widget
    
    return None

def _extract_ui_metadata(annotation) -> UIMetadata | None:
    if get_origin(annotation) is not Annotated:
        return None
    
    args = get_args(annotation)
    metadata = {}
    has_custom = False
    
    for m in args[1:]:
        if isinstance(m, Step):
            metadata['step'] = m.value
            has_custom = True
        elif isinstance(m, type) and issubclass(m, IsPassword):
            metadata['is_password'] = True
            has_custom = True
        elif isinstance(m, IsPassword):
            metadata['is_password'] = True
            has_custom = True
        elif isinstance(m, Slider):
            metadata['is_slider'] = True
            metadata['show_slider_value'] = m.show_value
            has_custom = True
        elif isinstance(m, Placeholder):
            metadata['placeholder'] = m.text
            has_custom = True
        elif isinstance(m, PatternMessage):
            metadata['pattern_message'] = m.message
            has_custom = True
        elif isinstance(m, Description):
            metadata['description'] = m.text
            has_custom = True
        elif isinstance(m, Label):
            metadata['label'] = m.text
            has_custom = True
        elif isinstance(m, Rows):
            metadata['rows'] = m.count
            has_custom = True
    
    return UIMetadata(**metadata) if has_custom else None


def _extract_dropdown(annotation, param_name: str, default) -> tuple[Any, ChoiceMetadata | None, Any]:
    base = annotation
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        base = args[0]
        
        for m in args[1:]:
            if isinstance(m, Dropdown):
                if not callable(m.options_function):
                    raise TypeError(
                        f"Parameter '{param_name}': Dropdown must receive a callable function"
                    )

                try:
                    opts = m.options_function()
                except Exception as e:
                    raise ValueError(
                        f"Parameter '{param_name}': Dropdown function failed: {e}"
                    )

                if not isinstance(opts, (list, tuple)):
                    raise TypeError(
                        f"Parameter '{param_name}': Dropdown must return a list or tuple"
                    )
                
                if not opts:
                    raise ValueError(
                        f"Parameter '{param_name}': Dropdown returned empty list"
                    )

                types_set = {type(o) for o in opts}
                if len(types_set) > 1:
                    raise TypeError(
                        f"Parameter '{param_name}': Dropdown has mixed types"
                    )
                
                returned_type = types_set.pop()

                if returned_type != base:
                    raise TypeError(
                        f"Parameter '{param_name}': Dropdown type mismatch. "
                        f"Expected {base.__name__}, got {returned_type.__name__}"
                    )

                if default is not None and default not in opts:
                    raise ValueError(
                        f"Parameter '{param_name}': default not in Dropdown options"
                    )

                choice_metadata = ChoiceMetadata(
                    enum_class=None,
                    options_function=m.options_function,
                    options=tuple(opts)
                )
                return base, choice_metadata, default

    if isinstance(base, type) and issubclass(base, Enum):
        opts = tuple(e.value for e in base)
        
        if not opts:
            raise ValueError(
                f"Parameter '{param_name}': Enum must have at least one value"
            )
        
        types_set = {type(v) for v in opts}
        if len(types_set) > 1:
            raise TypeError(
                f"Parameter '{param_name}': Enum values must be same type"
            )

        if default is not None:
            if not isinstance(default, base):
                raise TypeError(
                    f"Parameter '{param_name}': default must be {base.__name__} instance"
                )
            default = default.value
        
        base_type = types_set.pop()
        
        choice_metadata = ChoiceMetadata(
            enum_class=base,
            options_function=None,
            options=opts
        )
        return base_type, choice_metadata, default

    if get_origin(base) is Literal:
        opts = get_args(base)
        
        if len(opts) == 0:
            raise ValueError(
                f"Parameter '{param_name}': Literal must have at least one option"
            )
        
        types_set = {type(o) for o in opts}
        if len(types_set) > 1:
            raise TypeError(
                f"Parameter '{param_name}': Literal has mixed types"
            )

        if default is not None and default not in opts:
            raise ValueError(
                f"Parameter '{param_name}': default not in Literal options"
            )
        
        base_type = types_set.pop()
        
        choice_metadata = ChoiceMetadata(
            enum_class=None,
            options_function=None,
            options=opts
        )
        return base_type, choice_metadata, default

    return annotation, None, default


def _extract_optional(annotation, default, param_name: str) -> tuple[Any, OptionalMetadata | None]:
    if annotation is None or annotation is type(None):
        raise TypeError(f"Parameter '{param_name}' cannot have only None type")
   
    if get_origin(annotation) not in (Union, types.UnionType):
        return annotation, None
    
    union_args = get_args(annotation)
    has_none = type(None) in union_args
    explicit_marker = None
    none_count = 0
    
    for arg in union_args:
        if arg is type(None):
            none_count += 1
            continue
        
        if get_origin(arg) is Annotated:
            annotated_args = get_args(arg)
            if annotated_args[0] is type(None):
                none_count += 1
                for marker in annotated_args[1:]:
                    if isinstance(marker, _OptionalEnabledMarker):
                        explicit_marker = True
                    elif isinstance(marker, _OptionalDisabledMarker):
                        explicit_marker = False
                    else:
                        raise TypeError(
                            f"Parameter '{param_name}': Invalid marker in Annotated[None, ...]. "
                            f"Only OptionalEnabled/OptionalDisabled allowed"
                        )
    
    if none_count > 1:
        raise TypeError(f"Parameter '{param_name}' has multiple None types in Union")
    
    if not has_none and explicit_marker is None:
        non_none_count = len([arg for arg in union_args if arg is not type(None)])
        if non_none_count > 1:
            types_str = ' | '.join(
                arg.__name__ if hasattr(arg, '__name__') else str(arg) 
                for arg in union_args if arg is not type(None)
            )
            raise TypeError(
                f"Parameter '{param_name}': Union with multiple non-None types not supported, "
                f"only [type | None], not [type | type | ...]. Got: {types_str}"
            )
        return annotation, None
    
    non_none_types = []
    for arg in union_args:
        if arg is type(None):
            continue
        
        if get_origin(arg) is Annotated:
            annotated_args = get_args(arg)
            if annotated_args[0] is type(None):
                continue
        
        non_none_types.append(arg)
    
    if len(non_none_types) == 0:
        raise TypeError(f"Parameter '{param_name}' cannot have only None type")
    
    if len(non_none_types) > 1:
        raise TypeError(f"Parameter '{param_name}' has multiple non-None types in Union")
    
    enabled = explicit_marker if explicit_marker is not None else (default is not None)
    
    return non_none_types[0], OptionalMetadata(enabled=enabled)

def _extract_field(annotation) -> FieldInfo | None:
    if get_origin(annotation) is not Annotated:
        return None
    
    args = get_args(annotation)
    all_fields = []
    
    for m in args[1:]:
        if isinstance(m, FieldInfo):
            all_fields.append(m)
    
    base_type = args[0]
    if get_origin(base_type) is Annotated:
        base_field = _extract_field(base_type)
        if base_field:
            all_fields.append(base_field)
    
    if not all_fields:
        return None
    
    constraint_map = {}
    other_metadata = {}
    
    for field in all_fields:
        for metadata_item in field.metadata:
            constraint_key = None
            
            if hasattr(metadata_item, 'pattern'):
                constraint_key = 'pattern'
            elif hasattr(metadata_item, 'min_length'):
                constraint_key = 'min_length'
            elif hasattr(metadata_item, 'max_length'):
                constraint_key = 'max_length'
            elif hasattr(metadata_item, 'ge'):
                constraint_key = 'ge'
            elif hasattr(metadata_item, 'le'):
                constraint_key = 'le'
            elif hasattr(metadata_item, 'gt'):
                constraint_key = 'gt'
            elif hasattr(metadata_item, 'lt'):
                constraint_key = 'lt'
            
            if constraint_key:
                constraint_map[constraint_key] = metadata_item
            else:
                metadata_type = type(metadata_item).__name__
                if metadata_type not in other_metadata:
                    other_metadata[metadata_type] = []
                other_metadata[metadata_type].append(metadata_item)

    final_metadata = []

    final_metadata.extend(constraint_map.values())

    for metadata_list in other_metadata.values():
        final_metadata.extend(metadata_list)

    result = FieldInfo(
        annotation=all_fields[0].annotation,
        default=all_fields[0].default,
        default_factory=all_fields[0].default_factory,
    )
    result.metadata = final_metadata
    
    return result


def _extract_list(annotation, param_name: str, enable_warnings: bool = True) -> tuple[Any, ListMetadata | None]:
    list_constraints = _extract_field(annotation)
    
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        inner = args[0]
        
        if get_origin(inner) is list:
            annotation = inner
    
    if get_origin(annotation) is list:
        list_args = get_args(annotation)
        
        if len(list_args) == 0:
            raise TypeError(
                f"Parameter '{param_name}': list must have a type argument (e.g., list[int])"
            )
        
        if len(list_args) > 1:
            raise TypeError(
                f"Parameter '{param_name}': list can only have one type argument"
            )
        
        item_type = list_args[0]
        
        if list_constraints is not None and enable_warnings:
            field_info = _extract_field(item_type)
            
            if field_info:
                for constraint in field_info.metadata:
                    if hasattr(constraint, 'pattern') and _is_file_type_pattern(constraint.pattern):
                        warnings.warn(
                            f"Parameter '{param_name}': File lists with min_length/max_length constraints "
                            f"are not supported by the HTML renderer. The constraints will be ignored in HTML forms. "
                            f"You can still use these constraints with custom renderers or validation.",
                            UserWarning,
                            stacklevel=3
                        )
                        break
        
        return item_type, ListMetadata(constraints=list_constraints)
    
    if annotation is list:
        raise TypeError(
            f"Parameter '{param_name}': list must have a type argument (e.g., list[int])"
        )
    
    return annotation, None


def _validate_slider_compatibility(param_name: str, ui_metadata: UIMetadata, base_type: type, 
                                    constraints: FieldInfo | None) -> None:
    if not ui_metadata or not ui_metadata.is_slider:
        return
    
    if base_type not in (int, float):
        raise TypeError(
            f"Parameter '{param_name}': Slider only supported for int/float, got {base_type.__name__}"
        )
    
    if not constraints:
        raise TypeError(
            f"Parameter '{param_name}': Slider requires Field(ge=..., le=...) constraints"
        )
    
    has_min = any(hasattr(c, 'ge') or hasattr(c, 'gt') for c in constraints.metadata)
    has_max = any(hasattr(c, 'le') or hasattr(c, 'lt') for c in constraints.metadata)
    
    if not has_min or not has_max:
        raise TypeError(
            f"Parameter '{param_name}': Slider requires both min (ge=/gt=) and max (le=/lt=) values"
        )

def analyze_parameter(param: inspect.Parameter, enable_warnings: bool = True) -> ParamMetadata:
    if param.kind == inspect.Parameter.VAR_POSITIONAL:
        raise TypeError(f"*args not supported (parameter '{param.name}')")
    if param.kind == inspect.Parameter.VAR_KEYWORD:
        raise TypeError(f"**kwargs not supported (parameter '{param.name}')")
    
    annotation = param.annotation
    
    if annotation == inspect.Parameter.empty:
        raise TypeError(f"Parameter '{param.name}' has no type hint")
    
    default = None if param.default == inspect.Parameter.empty else param.default
    
    annotation, optional = _extract_optional(annotation, default, param.name)
    
    list_ui_metadata = _extract_ui_metadata(annotation) if get_origin(annotation) is Annotated else None
    
    annotation, list_metadata = _extract_list(annotation, param.name, enable_warnings)
    
    original_annotation = annotation
    
    constraints = _extract_field(annotation)
    
    dropdown_default = None if list_metadata is not None else default
    annotation, choices, extracted_default = _extract_dropdown(annotation, param.name, dropdown_default)
    
    if list_metadata is None:
        default = extracted_default
    
    if list_metadata is not None and choices is not None and default is not None:
        if isinstance(default, list) and choices.enum_class is not None:
            default = [
                item.value if isinstance(item, choices.enum_class) else item 
                for item in default
            ]
    
    widget_type = _detect_special_type(constraints)
    
    item_ui_metadata = _extract_ui_metadata(original_annotation)
    
    if list_metadata is not None:
        if item_ui_metadata is not None:
            if item_ui_metadata.description is not None:
                raise TypeError(
                    f"Parameter '{param.name}': Description not allowed on list items. "
                    f"Use Description at list level instead."
                )
            if item_ui_metadata.label is not None:
                raise TypeError(
                    f"Parameter '{param.name}': Label not allowed on list items. "
                    f"Use Label at list level instead."
                )
        
        ui_metadata = UIMetadata(
            label=list_ui_metadata.label if list_ui_metadata else None,
            description=list_ui_metadata.description if list_ui_metadata else None,
            step=item_ui_metadata.step if item_ui_metadata else 1,
            is_password=item_ui_metadata.is_password if item_ui_metadata else False,
            is_slider=item_ui_metadata.is_slider if item_ui_metadata else False,
            show_slider_value=item_ui_metadata.show_slider_value if item_ui_metadata else True,
            placeholder=item_ui_metadata.placeholder if item_ui_metadata else None,
            pattern_message=item_ui_metadata.pattern_message if item_ui_metadata else None,
            rows=item_ui_metadata.rows if item_ui_metadata else None
        ) if (list_ui_metadata or item_ui_metadata) else None
    else:
        ui_metadata = item_ui_metadata
    
    if get_origin(annotation) is Annotated:
        base_type = get_args(annotation)[0]
    else:
        base_type = annotation
    
    if base_type not in _VALID_TYPES:
        valid_types = ', '.join(t.__name__ for t in _VALID_TYPES)
        raise TypeError(
            f"Parameter '{param.name}': Only {valid_types} types are supported, "
            f"got '{base_type.__name__}'"
        )

    _validate_slider_compatibility(param.name, ui_metadata, base_type, constraints)

    if default is not None and list_metadata is not None:
        if isinstance(default, list) and len(default) == 0:
            default = None

    return ParamMetadata(
        name=param.name,
        param_type=base_type,
        default=default,
        constraints=constraints,
        widget_type=widget_type,
        optional=optional,
        list=list_metadata,
        choices=choices,
        ui=ui_metadata,
    )

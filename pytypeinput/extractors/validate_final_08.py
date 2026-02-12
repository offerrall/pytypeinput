import inspect
from typing import Any, Annotated
from datetime import date, time
from enum import Enum

from pydantic import Field, TypeAdapter, ValidationError
from pydantic.fields import FieldInfo

from ..param import ChoiceMetadata, ConstraintsMetadata, ListMetadata, ItemUIMetadata


_VALID_TYPES = {int, float, str, bool, date, time}


def _validate_base_type(annotation: Any) -> None:
    if annotation not in _VALID_TYPES:
        valid = ", ".join(t.__name__ for t in _VALID_TYPES)
        name = getattr(annotation, '__name__', str(annotation))
        if name == 'list':
            raise TypeError(
                "Empty list type is not supported."
            )
        raise TypeError(
            f"Unsupported type: {name}. Must be one of: {valid}"
        )


def _validate_slider_bounds(
    item_ui: ItemUIMetadata | None,
    constraints: ConstraintsMetadata | None,
) -> None:
    if item_ui is None or not item_ui.is_slider:
        return
    if constraints is None:
        raise TypeError(
            "Slider requires numeric bounds (e.g., Field(ge=0, le=100))"
        )
    has_lower = constraints.ge is not None or constraints.gt is not None
    has_upper = constraints.le is not None or constraints.lt is not None
    if not has_lower or not has_upper:
        raise TypeError(
            "Slider requires both lower and upper bounds "
            "(e.g., Field(ge=0, le=100))"
        )


def _validate_dropdown_type(annotation: type, choices: ChoiceMetadata) -> None:
    option_type = type(choices.options[0])
    if option_type is not annotation:
        raise TypeError(
            f"Dropdown options are {option_type.__name__} but type is {annotation.__name__}"
        )


def _validate_default_type(default: Any, annotation: type) -> None:
    if type(default) is not annotation:
        raise TypeError(
            f"Default value {default!r} is not a valid {annotation.__name__}"
        )


def _validate_default_choices(default: Any, choices: ChoiceMetadata) -> None:
    if choices.enum_class is not None:
        if isinstance(default, choices.enum_class):
            default = default.value

    if default not in choices.options:
        raise ValueError(
            f"Default value {default!r} not in options: {choices.options}"
        )


def _constraints_to_fieldinfo(c: ConstraintsMetadata) -> FieldInfo:
    kwargs = {}
    if c.ge is not None: kwargs["ge"] = c.ge
    if c.le is not None: kwargs["le"] = c.le
    if c.gt is not None: kwargs["gt"] = c.gt
    if c.lt is not None: kwargs["lt"] = c.lt
    if c.min_length is not None: kwargs["min_length"] = c.min_length
    if c.max_length is not None: kwargs["max_length"] = c.max_length
    if c.pattern is not None: kwargs["pattern"] = c.pattern
    return Field(**kwargs)


def _build_validator(annotation: type, constraints: ConstraintsMetadata | None) -> TypeAdapter | None:
    if constraints is None:
        return None
    field_info = _constraints_to_fieldinfo(constraints)
    return TypeAdapter(Annotated[annotation, field_info])


def _validate_with_adapter(
    adapter: TypeAdapter, default: Any, annotation: type
) -> None:
    try:
        adapter.validate_python(default)
    except ValidationError as e:
        errors = e.errors()
        msg = errors[0]["msg"] if errors else str(e)
        raise ValueError(
            f"Default value {default!r} violates constraints: {msg}"
        ) from e


def _validate_list_default(
    default: Any,
    item_type: type,
    list_meta: ListMetadata | None,
    choices: ChoiceMetadata | None,
    validator: TypeAdapter | None,
) -> None:
    if not isinstance(default, (list, tuple)):
        raise TypeError(
            f"Default value {default!r} is not a valid list"
        )
    
    if list_meta is not None:
        list_len = len(default)
        
        if list_meta.min_length is not None and list_len < list_meta.min_length:
            raise ValueError(
                f"Default list length {list_len} is less than min_length {list_meta.min_length}"
            )
        
        if list_meta.max_length is not None and list_len > list_meta.max_length:
            raise ValueError(
                f"Default list length {list_len} exceeds max_length {list_meta.max_length}"
            )
    
    for i, item in enumerate(default):
        item_to_check = item
        if choices is not None and choices.enum_class is not None:
            if isinstance(item, choices.enum_class):
                item_to_check = item.value
        
        try:
            _validate_default_type(item_to_check, item_type)
        except TypeError as e:
            raise TypeError(
                f"List item [{i}] {item!r}: {e}"
            ) from e
        
        if choices is not None:
            try:
                _validate_default_choices(item_to_check, choices)
            except ValueError as e:
                raise ValueError(
                    f"List item [{i}] {item!r}: {e}"
                ) from e
        
        if validator is not None:
            try:
                _validate_with_adapter(validator, item_to_check, item_type)
            except ValueError as e:
                raise ValueError(
                    f"List item [{i}] {item!r}: {e}"
                ) from e


def validate_final(
    annotation: Any,
    default: Any = inspect.Parameter.empty,
    choices: ChoiceMetadata | None = None,
    constraints: ConstraintsMetadata | None = None,
    list_meta: ListMetadata | None = None,
    item_ui: ItemUIMetadata | None = None,
) -> TypeAdapter | None:
    _validate_base_type(annotation)

    _validate_slider_bounds(item_ui, constraints)

    if choices is not None and choices.options and choices.options_function is not None:
        _validate_dropdown_type(annotation, choices)

    validator = _build_validator(annotation, constraints)

    if default is inspect.Parameter.empty or default is None:
        return validator

    if list_meta is not None:
        _validate_list_default(default, annotation, list_meta, choices, validator)
        return validator

    if choices is not None and choices.enum_class is not None:
        if isinstance(default, Enum):
            default = default.value

    _validate_default_type(default, annotation)

    if choices is not None:
        _validate_default_choices(default, choices)

    if validator is not None:
        _validate_with_adapter(validator, default, annotation)

    return validator
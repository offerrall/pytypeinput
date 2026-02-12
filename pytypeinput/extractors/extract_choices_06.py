from typing import Any, Literal, get_origin, get_args, Annotated
from enum import Enum

from ..param import ChoiceMetadata
from ..types import Dropdown
from ..helpers import rebuild_annotated


def _extract_dropdown(metadata: list) -> tuple[list, Dropdown | None]:
    dropdown = None
    rest = []
    for item in metadata:
        if isinstance(item, Dropdown):
            dropdown = item
        else:
            rest.append(item)
    return rest, dropdown


def _resolve_dropdown(dropdown: Dropdown) -> ChoiceMetadata:
    if not callable(dropdown.options_function):
        raise TypeError("Dropdown must receive a callable function")

    try:
        opts = dropdown.options_function()
    except Exception as e:
        raise ValueError(f"Dropdown function failed: {e}") from e

    if not isinstance(opts, (list, tuple)):
        raise TypeError("Dropdown function must return a list or tuple")

    if not opts:
        raise ValueError("Dropdown function returned empty list")

    types_set = {type(o) for o in opts}
    if len(types_set) > 1:
        raise TypeError("Dropdown options must be the same type")

    return ChoiceMetadata(
        options_function=dropdown.options_function,
        options=tuple(opts),
    )


def _resolve_enum(enum_class: type) -> tuple[type, ChoiceMetadata]:
    opts = tuple(e.value for e in enum_class)

    if not opts:
        raise ValueError("Enum must have at least one value")

    types_set = {type(v) for v in opts}
    if len(types_set) > 1:
        raise TypeError("Enum values must be the same type")

    return types_set.pop(), ChoiceMetadata(
        enum_class=enum_class,
        options=opts,
    )


def _resolve_literal(annotation: Any) -> tuple[type, ChoiceMetadata]:
    opts = get_args(annotation)

    if not opts:
        raise ValueError("Literal must have at least one option")

    types_set = {type(o) for o in opts}
    if len(types_set) > 1:
        raise TypeError("Literal options must be the same type")

    return types_set.pop(), ChoiceMetadata(options=opts)


def extract_choices(annotation: Any) -> tuple[Any, ChoiceMetadata | None]:
    if get_origin(annotation) is Annotated:
        base, *metadata = get_args(annotation)
        rest, dropdown = _extract_dropdown(metadata)

        if dropdown is not None:
            clean = rebuild_annotated(base, rest)
            return clean, _resolve_dropdown(dropdown)

        annotation_for_check = base
    else:
        annotation_for_check = annotation

    if isinstance(annotation_for_check, type) and issubclass(annotation_for_check, Enum):
        base_type, choices = _resolve_enum(annotation_for_check)
        return base_type, choices

    if get_origin(annotation_for_check) is Literal:
        base_type, choices = _resolve_literal(annotation_for_check)
        return base_type, choices

    return annotation, None
from typing import Any, get_origin, get_args, Annotated

from pydantic.fields import FieldInfo

from ..param import ListMetadata


_VALID_LIST_CONSTRAINTS = {'min_length', 'max_length'}


def _extract_list_constraints(field: FieldInfo) -> dict:
    result = {}
    for m in field.metadata:
        found = False
        for attr in _VALID_LIST_CONSTRAINTS:
            val = getattr(m, attr, None)
            if val is not None:
                result[attr] = val
                found = True
        if not found:
            raise TypeError(
                f"Invalid list constraint: {type(m).__name__}. "
                f"Only min_length/max_length allowed on lists."
            )
    return result


def _check_nested_list(inner: Any) -> None:
    base = inner
    if get_origin(base) is Annotated:
        base = get_args(base)[0]
    if get_origin(base) is list:
        raise TypeError("Nested lists are not supported (list[list[...]])")


def extract_list(annotation: Any) -> tuple[Any, ListMetadata | None]:
    origin = get_origin(annotation)

    if origin is Annotated:
        base, *metadata = get_args(annotation)

        if get_origin(base) is not list:
            return annotation, None

        args = get_args(base)
        inner = args[0] if args else Any

        _check_nested_list(inner)

        merged = {}
        for item in metadata:
            if isinstance(item, FieldInfo):
                merged.update(_extract_list_constraints(item))
            else:
                raise TypeError(
                    f"Invalid metadata on list: {type(item).__name__}. "
                    f"Only Field(min_length/max_length) allowed."
                )

        return inner, ListMetadata(**merged) if merged else ListMetadata()

    if origin is list:
        args = get_args(annotation)
        inner = args[0] if args else Any

        _check_nested_list(inner)

        return inner, ListMetadata()

    return annotation, None
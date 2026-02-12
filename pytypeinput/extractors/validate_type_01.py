from typing import Union, Annotated, get_origin, get_args
import types


def _is_none_type(t) -> bool:
    if t is None or t is type(None):
        return True
    if get_origin(t) is Annotated:
        return get_args(t)[0] is type(None)
    return False


def validate_type(annotation) -> None:
    if annotation is None or annotation is type(None):
        raise TypeError("Type annotation cannot be only None")

    if get_origin(annotation) not in (Union, types.UnionType):
        return
    
    union_args = get_args(annotation)
    
    if len(union_args) > 2:
        raise TypeError(
            f"Union cannot have more than 2 types, got {len(union_args)}"
        )

    if len(union_args) == 2:
        if not any(_is_none_type(t) for t in union_args):
            raise TypeError(
                "Union of 2 types must include None "
                "(e.g., str | None, int | OptionalEnabled)"
            )
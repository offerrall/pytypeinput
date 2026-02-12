from typing import Any, get_origin, get_args, Annotated

from pydantic.fields import FieldInfo

from ..param import ConstraintsMetadata
from ..helpers import rebuild_annotated


_CONSTRAINT_ATTRS = ('ge', 'le', 'gt', 'lt', 'min_length', 'max_length', 'pattern')


def _fieldinfo_to_dict(field: FieldInfo) -> dict:
    result = {}
    for m in field.metadata:
        for attr in _CONSTRAINT_ATTRS:
            val = getattr(m, attr, None)
            if val is not None:
                result[attr] = val
    return result


def extract_constraints(annotation: Any) -> tuple[Any, ConstraintsMetadata | None]:
    if get_origin(annotation) is not Annotated:
        return annotation, None

    base, *metadata = get_args(annotation)

    fields = []
    rest = []
    for item in metadata:
        if isinstance(item, FieldInfo):
            fields.append(item)
        else:
            rest.append(item)

    if not fields:
        clean = rebuild_annotated(base, rest)
        return clean, None

    merged = {}
    for field in fields:
        merged.update(_fieldinfo_to_dict(field))

    if not merged:
        return base, None

    clean = rebuild_annotated(base, rest)
    return clean, ConstraintsMetadata(**merged)
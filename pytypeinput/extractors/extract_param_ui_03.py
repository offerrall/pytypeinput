from typing import Any, get_origin, get_args, Annotated

from ..param import ParamUIMetadata
from ..types import Label, Description
from ..helpers import rebuild_annotated


def _scan_metadata(metadata: list) -> tuple[list, str | None, str | None]:
    label = None
    description = None
    rest = []
    for item in metadata:
        if isinstance(item, Label):
            label = item.text
        elif isinstance(item, Description):
            description = item.text
        else:
            rest.append(item)
    return rest, label, description


def _strip_label_description(annotation: Any) -> Any:
    if get_origin(annotation) is Annotated:
        base, *metadata = get_args(annotation)
        rest, _, _ = _scan_metadata(metadata)
        base = _strip_label_description(base)
        return rebuild_annotated(base, rest)

    if get_origin(annotation) is list:
        args = get_args(annotation)
        if args:
            return list[_strip_label_description(args[0])]

    return annotation


def _read_from_list(annotation: Any) -> tuple[str | None, str | None]:
    base = annotation
    if get_origin(base) is Annotated:
        base = get_args(base)[0]

    if get_origin(base) is not list:
        return None, None

    args = get_args(base)
    if not args or get_origin(args[0]) is not Annotated:
        return None, None

    _, *inner_meta = get_args(args[0])
    _, label, description = _scan_metadata(inner_meta)
    return label, description


def extract_param_ui(annotation: Any) -> tuple[Any, ParamUIMetadata | None]:

    label = None
    description = None

    if get_origin(annotation) is Annotated:
        base, *metadata = get_args(annotation)
        _, label, description = _scan_metadata(metadata)

    if label is None and description is None:
        label, description = _read_from_list(annotation)

    clean = _strip_label_description(annotation)

    if label is not None or description is not None:
        return clean, ParamUIMetadata(label=label, description=description)

    return clean, None
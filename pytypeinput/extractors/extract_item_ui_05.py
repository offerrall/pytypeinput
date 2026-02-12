from typing import Any, get_origin, get_args, Annotated

from ..param import ItemUIMetadata
from ..types import (
    Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword,
)
from ..helpers import rebuild_annotated


def extract_item_ui(annotation: Any) -> tuple[Any, ItemUIMetadata | None]:
    if get_origin(annotation) is not Annotated:
        return annotation, None

    base, *metadata = get_args(annotation)

    rest = []
    kwargs = {}

    for item in metadata:
        if isinstance(item, Step):
            kwargs['step'] = item.value
        elif isinstance(item, Placeholder):
            kwargs['placeholder'] = item.text
        elif isinstance(item, PatternMessage):
            kwargs['pattern_message'] = item.message
        elif isinstance(item, Rows):
            kwargs['rows'] = item.count
        elif isinstance(item, Slider):
            kwargs['is_slider'] = True
            kwargs['show_slider_value'] = item.show_value
        elif isinstance(item, IsPassword):
            kwargs['is_password'] = True
        else:
            rest.append(item)

    if not kwargs:
        return annotation, None

    clean = rebuild_annotated(base, rest)
    return clean, ItemUIMetadata(**kwargs)
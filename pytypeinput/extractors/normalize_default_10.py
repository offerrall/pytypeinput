import inspect
from typing import Any

from ..param import ChoiceMetadata, ListMetadata


def normalize_default(
    default: Any,
    choices: ChoiceMetadata | None,
    list_meta: ListMetadata | None,
) -> Any:
    if default is inspect.Parameter.empty or default is None:
        return None

    if choices is None or choices.enum_class is None:
        return default

    if list_meta is not None:
        if isinstance(default, (list, tuple)):
            return [
                item.value if isinstance(item, choices.enum_class) else item
                for item in default
            ]
        return default

    if isinstance(default, choices.enum_class):
        return default.value

    return default
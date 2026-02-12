from datetime import date, time

from ..param import ChoiceMetadata, ItemUIMetadata, ConstraintsMetadata
from ..types import SPECIAL_TYPES


_BASE_WIDGET_MAP = {
    str: "Text",
    int: "Number",
    float: "Number",
    bool: "Checkbox",
    date: "Date",
    time: "Time",
}


def resolve_widget_type(
    param_type: type,
    constraints: ConstraintsMetadata | None = None,
    choices: ChoiceMetadata | None = None,
    item_ui: ItemUIMetadata | None = None,
) -> str | None:
    if choices is not None:
        return "Dropdown"

    if item_ui is not None and item_ui.is_slider:
        return "Slider"

    if item_ui is not None and item_ui.is_password:
        return "Password"

    if item_ui is not None and item_ui.rows is not None:
        return "Textarea"

    if constraints is not None and constraints.pattern:
        pattern = constraints.pattern
        if pattern in SPECIAL_TYPES:
            return SPECIAL_TYPES[pattern]

    return _BASE_WIDGET_MAP.get(param_type)
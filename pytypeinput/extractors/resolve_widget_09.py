from ..param import ConstraintsMetadata
from ..types import SPECIAL_TYPES


def resolve_special_widget(
    constraints: ConstraintsMetadata | None = None,
) -> str | None:
    if constraints is not None and constraints.pattern in SPECIAL_TYPES:
        return SPECIAL_TYPES[constraints.pattern]

    return None
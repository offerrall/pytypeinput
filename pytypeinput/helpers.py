from typing import Annotated
from typing import Any
from enum import Enum
from datetime import date, time

def rebuild_annotated(base, metadata: list):
    if not metadata:
        return base
    return Annotated[tuple([base, *metadata])]


def serialize_value(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, type):
        return val.__name__
    if isinstance(val, (date, time)):
        return val.isoformat()
    if isinstance(val, tuple):
        return [serialize_value(v) for v in val]
    if isinstance(val, list):
        return [serialize_value(v) for v in val]
    if callable(val):
        return None
    return val
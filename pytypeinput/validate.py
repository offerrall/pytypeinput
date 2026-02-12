from typing import Any
from datetime import date, time
from enum import Enum

from .param import ParamMetadata


def validate_value(meta: ParamMetadata, value: Any) -> Any:
    """
    Validate and convert a value according to param metadata.
    Accepts both Python-native values and JSON/form string primitives.
    Returns the native Python value (Enum instance, date object, etc.).

    - If value is None and field is optional → returns None.
    - If value is None and field is required → raises ValueError.
    - Empty string on required str → raises ValueError (use str | None for optional).
    - Empty list on required list → raises ValueError (use list[...] | None for optional).
    - If field is optional and has no value, don't call this function, just skip it.
    - Defaults are only for form pre-fill, they don't affect validation.
    - Dynamic options (Dropdown with options_function) are NOT validated against
      current options. It is the caller's responsibility to ensure the value is valid.
    - Static choices (Enum, Literal) are validated.
    """
    if value is None:
        if meta.optional is not None:
            return None
        raise ValueError("None is not allowed (not optional)")

    if meta.param_type is str and isinstance(value, str) and not value.strip():
        raise ValueError("String cannot be empty (use str | None for optional strings)")

    if meta.list is not None:
        return _validate_list(meta, value)

    return _validate_single(meta, value)


def _validate_single(meta: ParamMetadata, value: Any) -> Any:
    value = _coerce(meta, value)

    if meta.choices is not None:
        _check_choices(meta, value)

    if meta._validator is not None:
        try:
            meta._validator.validate_python(value)
        except Exception as e:
            raise ValueError(f"Constraint validation failed: {e}") from e

    return value


def _validate_list(meta: ParamMetadata, value: Any) -> list:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"Expected list, got {type(value).__name__}")

    items = list(value)

    if len(items) == 0:
        raise ValueError("List cannot be empty (use list[...] | None for optional lists)")

    if meta.list.min_length is not None and len(items) < meta.list.min_length:
        raise ValueError(f"List too short: {len(items)} < {meta.list.min_length}")

    if meta.list.max_length is not None and len(items) > meta.list.max_length:
        raise ValueError(f"List too long: {len(items)} > {meta.list.max_length}")

    return [_validate_single(meta, item) for item in items]


def _coerce(meta: ParamMetadata, value: Any) -> Any:
    t = meta.param_type

    if meta.choices is not None and meta.choices.enum_class is not None:
        enum_cls = meta.choices.enum_class
        if isinstance(value, enum_cls):
            return value
        for member in enum_cls:
            if member.value == value:
                return member
        if isinstance(value, str) and value in enum_cls.__members__:
            return enum_cls[value]
        raise ValueError(
            f"{value!r} is not a valid {enum_cls.__name__} "
            f"(options: {[m.value for m in enum_cls]})"
        )

    if isinstance(value, t) and not (t in (int, float) and isinstance(value, bool)):
        return value

    if t is date:
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Cannot parse date from {value!r} (expected YYYY-MM-DD)")
        raise TypeError(f"Expected date or ISO string, got {type(value).__name__}")

    if t is time:
        if isinstance(value, str):
            try:
                return time.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Cannot parse time from {value!r} (expected HH:MM:SS)")
        raise TypeError(f"Expected time or ISO string, got {type(value).__name__}")

    if t is int:
        if isinstance(value, float) and value == int(value):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        if isinstance(value, bool):
            raise TypeError("Expected int, got bool")
        raise TypeError(f"Expected int, got {type(value).__name__}")

    if t is float:
        if isinstance(value, (int,)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
        if isinstance(value, bool):
            raise TypeError("Expected float, got bool")
        raise TypeError(f"Expected float, got {type(value).__name__}")

    if t is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return bool(value)
        raise TypeError(f"Expected bool, got {type(value).__name__}")

    if t is str:
        if isinstance(value, str):
            return value
        raise TypeError(f"Expected str, got {type(value).__name__}")

    raise TypeError(f"Expected {t.__name__}, got {type(value).__name__}")


def _check_choices(meta: ParamMetadata, value: Any) -> None:
    if meta.choices.options_function is not None:
        return

    if meta.choices.enum_class is not None:
        if isinstance(value, Enum):
            if value.value not in meta.choices.options:
                raise ValueError(
                    f"{value!r} not in choices: {list(meta.choices.options)}"
                )
            return

    if value not in meta.choices.options:
        raise ValueError(f"{value!r} not in choices: {list(meta.choices.options)}")
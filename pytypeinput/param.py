from dataclasses import dataclass
from typing import Any
from .helpers import serialize_value


@dataclass(frozen=True)
class ConstraintsMetadata:
    ge: int | float | None = None
    le: int | float | None = None
    gt: int | float | None = None
    lt: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None

    def to_dict(self) -> dict:
        return {
            "ge": self.ge,
            "le": self.le,
            "gt": self.gt,
            "lt": self.lt,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "pattern": self.pattern,
        }


@dataclass(frozen=True)
class ListMetadata:
    min_length: int | None = None
    max_length: int | None = None

    def to_dict(self) -> dict:
        return {
            "min_length": self.min_length,
            "max_length": self.max_length,
        }


@dataclass(frozen=True)
class OptionalMetadata:
    enabled: bool = False

    def to_dict(self) -> dict:
        return {"enabled": self.enabled}


@dataclass(frozen=True)
class ChoiceMetadata:
    options: tuple
    enum_class: type | None = None
    options_function: Any = None

    def to_dict(self) -> dict:
        return {
            "enum_class": serialize_value(self.enum_class),
            "options": serialize_value(self.options),
        }


@dataclass(frozen=True)
class ItemUIMetadata:
    step: int | float | None = None
    is_password: bool = False
    is_slider: bool = False
    show_slider_value: bool = True
    placeholder: str | None = None
    pattern_message: str | None = None
    rows: int | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "is_password": self.is_password,
            "is_slider": self.is_slider,
            "show_slider_value": self.show_slider_value,
            "placeholder": self.placeholder,
            "pattern_message": self.pattern_message,
            "rows": self.rows,
        }


@dataclass(frozen=True)
class ParamUIMetadata:
    label: str | None = None
    description: str | None = None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "description": self.description,
        }


@dataclass(frozen=True)
class ParamMetadata:
    name: str
    param_type: type
    default: Any | None = None
    constraints: ConstraintsMetadata | None = None
    widget_type: str | None = None
    optional: OptionalMetadata | None = None
    list: ListMetadata | None = None
    choices: ChoiceMetadata | None = None
    item_ui: ItemUIMetadata | None = None
    param_ui: ParamUIMetadata | None = None
    _validator: Any = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "param_type": self.param_type.__name__,
            "default": serialize_value(self.default),
            "constraints": self.constraints.to_dict() if self.constraints else None,
            "widget_type": self.widget_type,
            "optional": self.optional.to_dict() if self.optional else None,
            "list": self.list.to_dict() if self.list else None,
            "choices": self.choices.to_dict() if self.choices else None,
            "item_ui": self.item_ui.to_dict() if self.item_ui else None,
            "param_ui": self.param_ui.to_dict() if self.param_ui else None,
        }

    def refresh_choices(self) -> "ParamMetadata":
        if self.choices is None or self.choices.options_function is None:
            return self

        try:
            new_opts = self.choices.options_function()
        except Exception as e:
            raise ValueError(f"Dropdown function failed: {e}") from e

        if not isinstance(new_opts, (list, tuple)):
            raise TypeError("Dropdown function must return a list or tuple")

        if not new_opts:
            raise ValueError("Dropdown function returned empty list")

        new_choices = ChoiceMetadata(
            options=tuple(new_opts),
            enum_class=self.choices.enum_class,
            options_function=self.choices.options_function,
        )

        if self.default is not None and self.default not in new_choices.options:
            raise ValueError(
                f"Default value {self.default!r} not in updated options: {new_choices.options}"
            )

        return ParamMetadata(
            name=self.name,
            param_type=self.param_type,
            default=self.default,
            constraints=self.constraints,
            widget_type=self.widget_type,
            optional=self.optional,
            list=self.list,
            choices=new_choices,
            item_ui=self.item_ui,
            param_ui=self.param_ui,
            _validator=self._validator,
        )
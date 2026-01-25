from typing import Annotated, Any

from pydantic import BaseModel, model_validator, TypeAdapter
from pydantic.config import ConfigDict
from pydantic.fields import FieldInfo


class _BaseMetadata(BaseModel):
    """Base model that allows arbitrary types (like type objects)."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ListMetadata(_BaseMetadata):
    """Metadata for list parameters.
    
    Attributes:
        constraints: Pydantic FieldInfo with min_length/max_length constraints.
    """
    
    constraints: FieldInfo | None = None


class OptionalMetadata(BaseModel):
    """Metadata for optional parameters.
    
    Attributes:
        enabled: Whether the optional field is enabled by default.
                 True if has a non-None default or OptionalEnabled marker.
    """
    
    enabled: bool = False


class ChoiceMetadata(_BaseMetadata):
    """Metadata for choice-based parameters (Enum, Literal, Dropdown).
    
    Attributes:
        enum_class: The Enum class if parameter is an Enum type.
        options_function: Function that returns options for Dropdown.
        options: Tuple of available choice values.
    """
    
    enum_class: type | None = None
    options_function: Any = None
    options: tuple | None = None


class UIMetadata(BaseModel):
    """UI customization metadata for parameters.
    
    Attributes:
        step: Step increment for number inputs (default: 1).
        is_password: Whether to render string input as password field.
        is_slider: Whether to render number input as slider widget.
        show_slider_value: Whether to display current value next to slider.
        placeholder: Placeholder text for input fields.
        pattern_message: Custom error message for pattern validation.
        description: Help text displayed below the input field.
        label: Custom label text (overrides parameter name).
        rows: Number of visible rows for textarea (multi-line input).
    """
    
    step: int | float = 1
    is_password: bool = False
    is_slider: bool = False
    show_slider_value: bool = True
    placeholder: str | None = None
    pattern_message: str | None = None
    description: str | None = None
    label: str | None = None
    rows: int | None = None


class ParamMetadata(_BaseMetadata):
    """Complete metadata for a function parameter.
    
    Stores all extracted information about a parameter including its type,
    constraints, default value, and UI customizations.
    
    Attributes:
        name: Parameter name.
        param_type: Base Python type (int, str, bool, etc.).
        default: Default value if provided.
        constraints: Pydantic FieldInfo with validation constraints.
        widget_type: Special widget type (Color, Email, ImageFile, etc.).
        optional: Optional metadata if parameter is optional.
        list: List metadata if parameter is a list.
        choices: Choice metadata if parameter has fixed options.
        ui: UI customization metadata.
    """
    
    name: str
    param_type: type
    default: Any = None
    constraints: FieldInfo | None = None
    widget_type: str | None = None
    optional: OptionalMetadata | None = None
    list: ListMetadata | None = None
    choices: ChoiceMetadata | None = None
    ui: UIMetadata | None = None
    
    def reload_choices(self, validate_default: bool = True) -> None:
        """Reload choices from Dropdown function if available.
        
        Reloads options by calling the options_function and optionally validates
        that the current default value is still in the new options.
        
        Args:
            validate_default: If True (default), validates that current default
                            is in the new options. If False, skips validation.
        
        Raises:
            RuntimeError: If parameter has no choices or choices are static (Enum/Literal).
            ValueError: If validate_default=True and default not in new options.
            TypeError: If options function returns invalid type.
        """
        if self.choices is None:
            raise RuntimeError(f"Parameter '{self.name}' has no choices to reload")
        
        if self.choices.options_function is None:
            raise RuntimeError(
                f"Parameter '{self.name}': Cannot reload choices. "
                "Choices are static (Enum or Literal). Only Dropdown-based choices can be reloaded."
            )
        
        try:
            new_options = self.choices.options_function()
        except Exception as e:
            raise ValueError(f"Parameter '{self.name}': Failed to reload options: {e}")
        
        if not isinstance(new_options, (list, tuple)):
            raise TypeError(
                f"Parameter '{self.name}': Options function must return a list or tuple"
            )
        
        if not new_options:
            raise ValueError(f"Parameter '{self.name}': Options function returned empty list")
        
        new_options_tuple = tuple(new_options)
        
        if validate_default and self.default is not None:
            if self.list is not None:
                if isinstance(self.default, list):
                    for item in self.default:
                        if item not in new_options_tuple:
                            raise ValueError(
                                f"Parameter '{self.name}': default list item '{item}' "
                                f"not in reloaded options. Available: {new_options_tuple}"
                            )
            else:
                if self.default not in new_options_tuple:
                    raise ValueError(
                        f"Parameter '{self.name}': default value '{self.default}' "
                        f"not in reloaded options. Available: {new_options_tuple}"
                    )
        
        self.choices.options = new_options_tuple
    
    @model_validator(mode='after')
    def validate_default(self):
        """Validate that default value satisfies all constraints and choices."""
        if self.default is None:
            return self
        
        if self.choices is not None:
            self._validate_choice_default()
        
        if self.list is not None:
            self._validate_list_default()
            return self
        
        if self.constraints is not None:
            self._validate_constraint_default()
        
        return self
    
    def _validate_choice_default(self):
        """Validate default value is in available choices."""
        if self.list is not None:
            if not isinstance(self.default, list):
                raise TypeError(f"Parameter '{self.name}': default must be a list")
            
            for item in self.default:
                if self.choices.options is not None and item not in self.choices.options:
                    raise ValueError(
                        f"Parameter '{self.name}': default value '{item}' not in options"
                    )
        else:
            if self.choices.enum_class is not None:
                if self.choices.options is None or self.default not in self.choices.options:
                    raise ValueError(
                        f"Parameter '{self.name}': Enum default value '{self.default}' not in options"
                    )
            else:
                if self.choices.options is not None and self.default not in self.choices.options:
                    raise ValueError(
                        f"Parameter '{self.name}': default '{self.default}' not in options"
                    )
    
    def _validate_constraint_default(self):
        """Validate default value satisfies pydantic constraints."""
        try:
            TypeAdapter(Annotated[self.param_type, self.constraints]).validate_python(self.default)
        except Exception as e:
            raise ValueError(
                f"Parameter '{self.name}': default value does not satisfy constraints: {e}"
            )
    
    def _validate_list_default(self):
        """Validate list default values satisfy all constraints."""
        if not isinstance(self.default, list):
            raise TypeError(f"Parameter '{self.name}': default must be a list")
        
        if self.list.constraints is not None:
            try:
                TypeAdapter(
                    Annotated[list[self.param_type], self.list.constraints]
                ).validate_python(self.default)
            except Exception as e:
                raise ValueError(
                    f"Parameter '{self.name}': list default does not satisfy constraints: {e}"
                )
        
        for item in self.default:
            if not isinstance(item, self.param_type):
                raise TypeError(
                    f"Parameter '{self.name}': list item type mismatch in default"
                )
            
            if self.constraints is not None:
                try:
                    TypeAdapter(
                        Annotated[self.param_type, self.constraints]
                    ).validate_python(item)
                except Exception as e:
                    raise ValueError(
                        f"Parameter '{self.name}': list item does not satisfy constraints: {e}"
                    )
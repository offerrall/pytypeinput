import inspect
from typing import Any

from .extractors.validate_type_01 import validate_type
from .extractors.validate_optional_02 import extract_optional
from .extractors.extract_param_ui_03 import extract_param_ui
from .extractors.extract_list_04 import extract_list
from .extractors.extract_item_ui_05 import extract_item_ui
from .extractors.extract_choices_06 import extract_choices
from .extractors.extract_constraints_07 import extract_constraints
from .extractors.validate_final_08 import validate_final
from .extractors.resolve_widget_09 import resolve_special_widget
from .extractors.normalize_default_10 import normalize_default

from .param import ParamMetadata

def analyze_type(
    annotation: Any,
    name: str = "field",
    default: Any = inspect.Parameter.empty
) -> ParamMetadata:
    """Analyze a type annotation and return complete metadata."""

    if not isinstance(name, str):
        raise TypeError(f"name must be str, got {type(name).__name__}")

    try:
        # 01. Validate type
        validate_type(annotation)

        # 02. Extract optional
        annotation, optional = extract_optional(annotation, default)

        # 03. Extract param UI (Label, Description)
        annotation, param_ui = extract_param_ui(annotation)

        # 04. Extract list
        annotation, list_meta = extract_list(annotation)

        # 05. Extract item UI (Slider, Step, Placeholder, etc.)
        annotation, item_ui = extract_item_ui(annotation)

        # 06. Extract choices (Enum, Literal, Dropdown)
        annotation, choices = extract_choices(annotation)

        # 07. Extract constraints (Field)
        annotation, constraints = extract_constraints(annotation)

        # 08. Validate final (base type, default, choices, constraints)
        #     Returns precompiled TypeAdapter for constraints validation
        validator = validate_final(annotation, default, choices, constraints, list_meta, item_ui)

        # 09. Resolve special widget (Color, File)
        special_widget = resolve_special_widget(constraints)
        
        # 10. Normalize default (Enum instances to values)
        normalized_default = normalize_default(default, choices, list_meta)

        return ParamMetadata(
            name=name,
            param_type=annotation,
            default=normalized_default,
            optional=optional,
            param_ui=param_ui,
            list=list_meta,
            item_ui=item_ui,
            choices=choices,
            constraints=constraints,
            special_widget=special_widget,
            _validator=validator,
        )

    except TypeError as e:
        raise TypeError(f"[{name}] {e}") from e
    except ValueError as e:
        raise ValueError(f"[{name}] {e}") from e
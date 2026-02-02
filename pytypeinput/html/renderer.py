from datetime import date, time, timedelta
import re

from ..param import ParamMetadata
from ..types import FILE_WIDGET_TYPES, WIDGET_TYPE_COLOR, WIDGET_TYPE_EMAIL, FILE_ACCEPT_EXTENSIONS

from .templates import (
    DEFAULT_INT_TEMPLATE,
    DEFAULT_STR_TEMPLATE,
    DEFAULT_STR_TEXTAREA_TEMPLATE,
    DEFAULT_FLOAT_TEMPLATE,
    DEFAULT_BOOL_TEMPLATE,
    DEFAULT_DATE_TEMPLATE,
    DEFAULT_TIME_TEMPLATE,
    DEFAULT_SELECT_TEMPLATE,
    DEFAULT_FILE_TEMPLATE,
    DEFAULT_SLIDER_INT_TEMPLATE,
    DEFAULT_SLIDER_FLOAT_TEMPLATE
)
from .assets import DEFAULT_STYLES, DEFAULT_VALIDATION_SCRIPT


def _extract_constraints(param: ParamMetadata) -> dict:
    """Extract all constraints from parameter metadata into a flat dictionary.
    
    Converts Pydantic constraints (ge, gt, le, lt, min_length, max_length, pattern)
    into a format usable by Jinja2 templates. For gt/lt constraints, uses a minimal
    epsilon value to represent exclusive boundaries in HTML inputs.
    
    Args:
        param: Parameter metadata containing constraints.
    
    Returns:
        Dictionary with keys: min, max, min_items, max_items, pattern.
    """
    result = {
        'min': None, 
        'max': None, 
        'min_items': None, 
        'max_items': None, 
        'pattern': None
    }
    
    def get_epsilon(param_type):
        """Get smallest representable value for exclusive boundaries."""
        if param_type == int:
            return 1
        else:
            return 0.000001
    
    epsilon = get_epsilon(param.param_type)
    
    value_mappings = [
        ('ge', 'min', lambda x: x),
        ('gt', 'min', lambda x: x + epsilon),
        ('le', 'max', lambda x: x),
        ('lt', 'max', lambda x: x - epsilon),
        ('min_length', 'min', lambda x: x),
        ('max_length', 'max', lambda x: x),
        ('pattern', 'pattern', lambda x: x),
    ]
    
    list_mappings = [
        ('min_length', 'min_items', lambda x: x),
        ('max_length', 'max_items', lambda x: x),
    ]
    
    def apply_mappings(constraints, mappings):
        """Apply constraint mappings to result dictionary."""
        if not constraints:
            return
        for constraint in constraints.metadata:
            for attr, key, transform in mappings:
                if hasattr(constraint, attr):
                    result[key] = transform(getattr(constraint, attr))
    
    apply_mappings(param.constraints, value_mappings)
    apply_mappings(param.list.constraints if param.list else None, list_mappings)
    
    return result


def _build_base_context(param: ParamMetadata, **extra) -> dict:
    """Build base template context from parameter metadata.
    
    Creates a dictionary with all common template variables:
    - name, label, default, default_values
    - is_optional, optional_enabled, is_list
    - Extracted constraints (min, max, pattern, etc.)
    - File accept patterns for file inputs
    - Placeholder for string, int, and float inputs
    
    Args:
        param: Parameter metadata.
        **extra: Additional context variables to merge.
    
    Returns:
        Dictionary for Jinja2 template rendering.
    """
    # Use custom label if provided, otherwise auto-generate from parameter name
    label = param.ui.label if (param.ui and param.ui.label) else param.name.replace('_', ' ').title()
    
    context = {
        'name': param.name,
        'label': label,
        'default': param.default if not param.list else None,
        'default_values': param.default if param.list else [],
        'is_optional': param.optional is not None,
        'optional_enabled': param.optional.enabled if param.optional else False,
        'is_list': param.list is not None,
        'description': param.ui.description if param.ui else None,
        **_extract_constraints(param),
        **extra,
    }
    
    # Placeholder for str, int, float
    if param.param_type in (str, int, float):
        context['placeholder'] = param.ui.placeholder if param.ui else None
    
    # Pattern and pattern_message only for strings
    if param.param_type == str:
        context['pattern_message'] = param.ui.pattern_message if param.ui else None
        
        if param.widget_type in FILE_WIDGET_TYPES:
            context['pattern'] = FILE_ACCEPT_EXTENSIONS.get(param.widget_type, '*')
    
    return context


def render_integer(param: ParamMetadata) -> str:
    """Render integer parameter as HTML.
    
    Uses select dropdown if choices are defined, slider if Slider() is used,
    otherwise renders number input with increment/decrement controls.
    
    Args:
        param: Integer parameter metadata.
    
    Returns:
        HTML string.
    """
    if param.choices:
        return render_select(param)
    
    step = param.ui.step if param.ui else 1
    
    if param.ui and param.ui.is_slider:
        show_value = param.ui.show_slider_value if param.ui else True
        return DEFAULT_SLIDER_INT_TEMPLATE.render(**_build_base_context(param, step=step, show_value=show_value))
    
    return DEFAULT_INT_TEMPLATE.render(**_build_base_context(param, step=step))


def render_float(param: ParamMetadata) -> str:
    """Render float parameter as HTML.
    
    Uses select dropdown if choices are defined, slider if Slider() is used,
    otherwise renders number input with decimal support and increment/decrement controls.
    
    Args:
        param: Float parameter metadata.
    
    Returns:
        HTML string.
    """
    if param.choices:
        return render_select(param)
    
    step = param.ui.step if param.ui and param.ui.step != 1 else 0.1
    
    if param.ui and param.ui.is_slider:
        show_value = param.ui.show_slider_value if param.ui else True
        return DEFAULT_SLIDER_FLOAT_TEMPLATE.render(**_build_base_context(param, step=step, show_value=show_value))
    
    return DEFAULT_FLOAT_TEMPLATE.render(**_build_base_context(param, step=step))


def render_string(param: ParamMetadata) -> str:
    """Render string parameter as HTML.
    
    Renders different input types based on widget_type:
    - File types: file input with preview
    - Color: color picker (cannot be textarea)
    - Email: email input with validation (cannot be textarea)
    - Textarea: multi-line text input (if Rows specified and no special type)
    - Password: password input (masked)
    - Default: text input
    
    Uses select dropdown if choices are defined.
    
    Args:
        param: String parameter metadata.
    
    Returns:
        HTML string.
    """
    if param.choices:
        return render_select(param)
    
    # File input types (highest priority)
    if param.widget_type in FILE_WIDGET_TYPES:
        return render_file(param)
    
    # Special widget types (Color, Email) - cannot be textarea
    if param.widget_type == WIDGET_TYPE_COLOR:
        return DEFAULT_STR_TEMPLATE.render(**_build_base_context(param, input_type='color'))
    
    if param.widget_type == WIDGET_TYPE_EMAIL:
        return DEFAULT_STR_TEMPLATE.render(**_build_base_context(param, input_type='email'))
    
    # Textarea (only for normal strings, not special types)
    if param.ui and param.ui.rows is not None:
        return DEFAULT_STR_TEXTAREA_TEMPLATE.render(**_build_base_context(param, rows=param.ui.rows))
    
    # Password (only for normal strings)
    if param.ui and param.ui.is_password:
        return DEFAULT_STR_TEMPLATE.render(**_build_base_context(param, input_type='password'))
    
    # Default text input
    return DEFAULT_STR_TEMPLATE.render(**_build_base_context(param, input_type='text'))


def render_boolean(param: ParamMetadata) -> str:
    """Render boolean parameter as HTML toggle switch.
    
    Args:
        param: Boolean parameter metadata.
    
    Returns:
        HTML string.
    """
    return DEFAULT_BOOL_TEMPLATE.render(**_build_base_context(param))

def render_date(param: ParamMetadata) -> str:
    """Render date parameter as HTML date picker.
    
    Default value: today's date if not specified.
    Supports ge/le/gt/lt constraints (gt/lt add/subtract 1 day for HTML compatibility).
    """
    context = _build_base_context(param)
    today = date.today().isoformat()
    
    if context['default'] is not None:
        context['default'] = context['default'].isoformat()
    else:
        context['default'] = today
    
    if context['default_values']:
        context['default_values'] = [d.isoformat() for d in context['default_values']]
    
    # Convert date constraints to ISO format for HTML
    if context['min'] is not None and isinstance(context['min'], date):
        context['min'] = context['min'].isoformat()
    
    if context['max'] is not None and isinstance(context['max'], date):
        context['max'] = context['max'].isoformat()
    
    context['list_item_default'] = today
    
    return DEFAULT_DATE_TEMPLATE.render(**context)


def render_time(param: ParamMetadata) -> str:
    """Render time parameter as HTML time picker.
    
    Default value: 12:00 (noon) if not specified.
    """
    context = _build_base_context(param)
    noon = "12:00"
    
    if context['default'] is not None:
        context['default'] = context['default'].strftime("%H:%M")
    else:
        context['default'] = noon
    
    if context['default_values']:
        context['default_values'] = [t.strftime("%H:%M") for t in context['default_values']]
    
    context['list_item_default'] = noon
    
    return DEFAULT_TIME_TEMPLATE.render(**context)


def render_select(param: ParamMetadata) -> str:
    """Render parameter as HTML select dropdown.
    
    Used for Enum, Literal, and Dropdown parameters.
    
    Args:
        param: Parameter metadata with choices defined.
    
    Returns:
        HTML string.
    """
    context = _build_base_context(param)
    context['options'] = param.choices.options
    return DEFAULT_SELECT_TEMPLATE.render(**context)


def render_file(param: ParamMetadata) -> str:
    """Render file parameter as HTML file input with preview.
    
    Supports single and multiple file selection with file list display.
    
    Args:
        param: File parameter metadata.
    
    Returns:
        HTML string.
    """
    return DEFAULT_FILE_TEMPLATE.render(**_build_base_context(param))


_TYPE_RENDERERS = {
    int: render_integer,
    float: render_float,
    str: render_string,
    bool: render_boolean,
    date: render_date,
    time: render_time,
}


class HTMLRenderer:
    """HTML form renderer with customizable styles and validation.
    
    Converts function parameters into complete HTML forms with:
    - Responsive design with CSS custom properties
    - Client-side validation
    - Support for all parameter types
    - Optional fields with toggle controls
    - List fields with add/remove functionality
    
    Attributes:
        global_styles: CSS styles to inject (default or custom).
        enable_validation: Whether to include validation JavaScript.
    """

    def __init__(self, custom_styles: str | None = None, enable_validation: bool = True):
        """Initialize HTML renderer.
        
        Args:
            custom_styles: Custom CSS to use instead of defaults.
            enable_validation: Whether to enable client-side validation.
        """
        self.global_styles = custom_styles if custom_styles is not None else DEFAULT_STYLES
        self.enable_validation = enable_validation

    @staticmethod
    def list_css_variables() -> list[str]:
        """List all user-customizable CSS custom properties.
        
        Returns only variables that users should customize:
        - Variables ending in -light or -dark (theme-specific)
        - Variables without -light/-dark suffix that don't have a pair
        
        Excludes internal "active" variables that auto-switch between themes.
        """
        pattern = r'(--pytypeinput-[\w-]+)'
        all_variables = set(re.findall(pattern, DEFAULT_STYLES))

        light_vars = {v for v in all_variables if v.endswith('-light')}
        dark_vars = {v for v in all_variables if v.endswith('-dark')}
        other_vars = {v for v in all_variables if not (v.endswith('-light') or v.endswith('-dark'))}

        light_bases = {v[:-6] for v in light_vars}
        dark_bases = {v[:-5] for v in dark_vars}
        has_theme_pair = light_bases & dark_bases
        
        customizable = light_vars | dark_vars | {v for v in other_vars if v not in has_theme_pair}
        
        return sorted(customizable)

    @staticmethod
    def get_default_styles() -> str:
        """Get default CSS styles wrapped in <style> tag.
        
        Returns:
            HTML style tag with default CSS.
        """
        return f"<style>{DEFAULT_STYLES}</style>"
    
    def get_styles(self) -> str:
        """Get current CSS styles wrapped in <style> tag.
        
        Returns:
            HTML style tag with configured CSS (custom or default).
        """
        return f"<style>{self.global_styles}</style>"
    
    def get_validation_script(self) -> str:
        """Get validation JavaScript wrapped in <script> tag.
        
        Returns:
            HTML script tag with validation code, or empty string if disabled.
        """
        return DEFAULT_VALIDATION_SCRIPT if self.enable_validation else ""
    
    def render_param(self, param: ParamMetadata) -> str:
        """Render a single parameter as HTML.
        
        Delegates to the appropriate type-specific renderer function.
        
        Args:
            param: Parameter metadata to render.
        
        Returns:
            HTML string for the parameter field.
            
        Raises:
            NotImplementedError: If parameter type is not supported.
        """
        renderer = _TYPE_RENDERERS.get(param.param_type)
        
        if renderer is None:
            raise NotImplementedError(
                f"Type '{param.param_type.__name__}' not yet supported. "
                f"Supported types: {', '.join(t.__name__ for t in _TYPE_RENDERERS.keys())}"
            )
        
        return renderer(param)
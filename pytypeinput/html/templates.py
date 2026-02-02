try:
    from jinja2 import Template
except ImportError:
    raise ImportError("Jinja2 is required to use the HTML renderer. Please install it via 'pip install Jinja2'.")

FIELD_MACROS = '''
{%- macro render_label(name, label, is_list, is_optional, optional_enabled) -%}
    {%- if is_optional -%}
        <div class="pytypeinput-optional-header">
            <label class="pytypeinput-label">{{ label }}</label>
            <label class="pytypeinput-toggle-switch">
                <input 
                    type="checkbox" 
                    class="pytypeinput-optional-toggle"
                    data-target="{{ name }}"
                    {%- if optional_enabled %} checked{%- endif %}
                >
                <span class="pytypeinput-toggle-slider"></span>
            </label>
        </div>
    {%- else -%}
        <label{%- if not is_list %} for="{{ name }}"{%- endif %} class="pytypeinput-label">
            {{ label }}
        </label>
    {%- endif -%}
{%- endmacro -%}
'''

BASE_TEMPLATE = '''
{%- set field_classes = ["pytypeinput-field"] -%}
{%- if is_list -%}
    {%- set _ = field_classes.append("pytypeinput-list-field") -%}
{%- endif -%}

{%- set list_attrs = [] -%}
{%- if is_list -%}
    {%- set _ = list_attrs.append('data-list-name="%s"' % name) -%}
    {%- if min_items is not none -%}
        {%- set _ = list_attrs.append('data-min-items="%s"' % min_items) -%}
    {%- endif -%}
    {%- if max_items is not none -%}
        {%- set _ = list_attrs.append('data-max-items="%s"' % max_items) -%}
    {%- endif -%}
{%- endif -%}

<div class="{{ field_classes|join(' ') }}"{% if list_attrs %} {{ list_attrs|join(' ')|safe }}{% endif %}>
    {{ render_label(name, label, is_list, is_optional, optional_enabled) }}
    
    {%- if description is not none -%}
    <small class="pytypeinput-description">{{ description }}</small>
    {%- endif -%}
    
    {%- if is_optional -%}
        {%- set content_classes = ["pytypeinput-optional-content"] -%}
        {%- if not optional_enabled -%}
            {%- set _ = content_classes.append("hidden") -%}
        {%- endif -%}
        <div class="{{ content_classes|join(' ') }}" data-optional-content="{{ name }}">
    {%- endif -%}
    
    {%- if is_list -%}
        <div class="pytypeinput-list-wrapper">
            <div class="pytypeinput-list-container">
                {%- if default_values -%}
                    {%- for value in default_values -%}
                        {{ render_list_item_content(value) }}
                    {%- endfor -%}
                {%- else -%}
                    {%- set initial_count = min_items if min_items is not none else 1 -%}
                    {%- for i in range(initial_count) -%}
                        {{ render_list_item_content() }}
                    {%- endfor -%}
                {%- endif -%}
            </div>
            <button type="button" class="pytypeinput-list-add-btn"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>+</button>
        </div>
    {%- else -%}
        {{ render_single_input() }}
    {%- endif -%}
    
    {%- if is_optional -%}
        </div>
    {%- endif -%}
</div>
'''

INT_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-number-wrapper">
                    <input 
                        type="number"
                        name="{{ name }}[]"
                        class="pytypeinput-input pytypeinput-list-input"
                        autocomplete="off"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                        {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
                        {%- if min is not none %} data-min="{{ min }}"{%- endif %}
                        {%- if max is not none %} data-max="{{ max }}"{%- endif %}
                        step="{{ step }}"
                    >
                    <div class="pytypeinput-number-controls">
                        <button type="button" class="pytypeinput-number-btn pytypeinput-number-up"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▲</button>
                        <button type="button" class="pytypeinput-number-btn pytypeinput-number-down"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▼</button>
                    </div>
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-number-wrapper">
        <input 
            type="number"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-input"
            autocomplete="off"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
            {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
            {%- if min is not none %} data-min="{{ min }}"{%- endif %}
            {%- if max is not none %} data-max="{{ max }}"{%- endif %}
            step="{{ step }}"
        >
        <div class="pytypeinput-number-controls">
            <button type="button" class="pytypeinput-number-btn pytypeinput-number-up"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▲</button>
            <button type="button" class="pytypeinput-number-btn pytypeinput-number-down"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▼</button>
        </div>
    </div>
{%- endmacro -%}
'''

DEFAULT_INT_TEMPLATE = Template(FIELD_MACROS + INT_MACROS + BASE_TEMPLATE)


STR_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <input 
                    type="{{ input_type }}"
                    name="{{ name }}[]"
                    class="pytypeinput-input pytypeinput-list-input"
                    autocomplete="off"
                    {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                    {%- if value is not none %} value="{{ value }}"{%- endif %}
                    {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
                    {%- if min is not none %} minlength="{{ min }}" data-minlength="{{ min }}"{%- endif %}
                    {%- if max is not none %} maxlength="{{ max }}" data-maxlength="{{ max }}"{%- endif %}
                    {%- if pattern is not none %} pattern="{{ pattern }}" data-pattern="{{ pattern }}"{%- endif %}
                    {%- if pattern_message is not none %} data-pattern-message="{{ pattern_message }}"{%- endif %}
                >
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <input 
        type="{{ input_type }}"
        id="{{ name }}"
        name="{{ name }}"
        class="pytypeinput-input"
        autocomplete="off"
        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
        {%- if default is not none %} value="{{ default }}"{%- endif %}
        {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
        {%- if min is not none %} minlength="{{ min }}" data-minlength="{{ min }}"{%- endif %}
        {%- if max is not none %} maxlength="{{ max }}" data-maxlength="{{ max }}"{%- endif %}
        {%- if pattern is not none %} pattern="{{ pattern }}" data-pattern="{{ pattern }}"{%- endif %}
        {%- if pattern_message is not none %} data-pattern-message="{{ pattern_message }}"{%- endif %}
    >
{%- endmacro -%}
'''

DEFAULT_STR_TEMPLATE = Template(FIELD_MACROS + STR_MACROS + BASE_TEMPLATE)

STR_TEXTAREA_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <textarea 
                    name="{{ name }}[]"
                    class="pytypeinput-input pytypeinput-list-input"
                    autocomplete="off"
                    {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                    {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
                    {%- if min is not none %} minlength="{{ min }}" data-minlength="{{ min }}"{%- endif %}
                    {%- if max is not none %} maxlength="{{ max }}" data-maxlength="{{ max }}"{%- endif %}
                    {%- if pattern is not none %} data-pattern="{{ pattern }}"{%- endif %}
                    {%- if pattern_message is not none %} data-pattern-message="{{ pattern_message }}"{%- endif %}
                    rows="{{ rows }}"
                >{{ value if value is not none else '' }}</textarea>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <textarea 
        id="{{ name }}"
        name="{{ name }}"
        class="pytypeinput-input"
        autocomplete="off"
        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
        {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
        {%- if min is not none %} minlength="{{ min }}" data-minlength="{{ min }}"{%- endif %}
        {%- if max is not none %} maxlength="{{ max }}" data-maxlength="{{ max }}"{%- endif %}
        {%- if pattern is not none %} data-pattern="{{ pattern }}"{%- endif %}
        {%- if pattern_message is not none %} data-pattern-message="{{ pattern_message }}"{%- endif %}
        rows="{{ rows }}"
    >{{ default if default is not none else '' }}</textarea>
{%- endmacro -%}
'''

DEFAULT_STR_TEXTAREA_TEMPLATE = Template(FIELD_MACROS + STR_TEXTAREA_MACROS + BASE_TEMPLATE)


FLOAT_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-number-wrapper">
                    <input 
                        type="number"
                        name="{{ name }}[]"
                        class="pytypeinput-input pytypeinput-list-input"
                        autocomplete="off"
                        data-float="true"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                        {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
                        {%- if min is not none %} data-min="{{ min }}"{%- endif %}
                        {%- if max is not none %} data-max="{{ max }}"{%- endif %}
                        step="{{ step }}"
                    >
                    <div class="pytypeinput-number-controls">
                        <button type="button" class="pytypeinput-number-btn pytypeinput-number-up"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▲</button>
                        <button type="button" class="pytypeinput-number-btn pytypeinput-number-down"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▼</button>
                    </div>
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-number-wrapper">
        <input 
            type="number"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-input"
            autocomplete="off"
            data-float="true"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
            {%- if placeholder is not none %} placeholder="{{ placeholder }}"{%- endif %}
            {%- if min is not none %} data-min="{{ min }}"{%- endif %}
            {%- if max is not none %} data-max="{{ max }}"{%- endif %}
            step="{{ step }}"
        >
        <div class="pytypeinput-number-controls">
            <button type="button" class="pytypeinput-number-btn pytypeinput-number-up"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▲</button>
            <button type="button" class="pytypeinput-number-btn pytypeinput-number-down"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>▼</button>
        </div>
    </div>
{%- endmacro -%}
'''

DEFAULT_FLOAT_TEMPLATE = Template(FIELD_MACROS + FLOAT_MACROS + BASE_TEMPLATE)

BOOL_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <label class="pytypeinput-toggle-switch">
                    <input 
                        type="checkbox"
                        name="{{ name }}[]"
                        class="pytypeinput-checkbox pytypeinput-list-input"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value %} checked{%- endif %}
                    >
                    <span class="pytypeinput-toggle-slider"></span>
                </label>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <label class="pytypeinput-toggle-switch">
        <input 
            type="checkbox"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-checkbox"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default %} checked{%- endif %}
        >
        <span class="pytypeinput-toggle-slider"></span>
    </label>
{%- endmacro -%}
'''

DEFAULT_BOOL_TEMPLATE = Template(FIELD_MACROS + BOOL_MACROS + BASE_TEMPLATE)

DATE_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-temporal-wrapper">
                    <input 
                        type="text"
                        class="pytypeinput-input pytypeinput-temporal-display"
                        placeholder="dd/mm/yyyy"
                        readonly
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                    >
                    <input 
                        type="date"
                        name="{{ name }}[]"
                        class="pytypeinput-temporal-real"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                        {%- if list_item_default is defined %} data-default="{{ list_item_default }}"{%- endif %}
                        {%- if min is not none %} min="{{ min }}"{%- endif %}
                        {%- if max is not none %} max="{{ max }}"{%- endif %}
                    >
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-temporal-wrapper">
        <input 
            type="text"
            class="pytypeinput-input pytypeinput-temporal-display"
            placeholder="dd/mm/yyyy"
            readonly
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
        >
        <input 
            type="date"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-temporal-real"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
            {%- if min is not none %} min="{{ min }}"{%- endif %}
            {%- if max is not none %} max="{{ max }}"{%- endif %}
        >
    </div>
{%- endmacro -%}
'''

DEFAULT_DATE_TEMPLATE = Template(FIELD_MACROS + DATE_MACROS + BASE_TEMPLATE)

TIME_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-temporal-wrapper">
                    <input 
                        type="text"
                        class="pytypeinput-input pytypeinput-temporal-display"
                        placeholder="hh:mm"
                        readonly
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                    >
                    <input 
                        type="time"
                        name="{{ name }}[]"
                        class="pytypeinput-temporal-real"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- endif %}
                        {%- if list_item_default is defined %} data-default="{{ list_item_default }}"{%- endif %}
                    >
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-temporal-wrapper">
        <input 
            type="text"
            class="pytypeinput-input pytypeinput-temporal-display"
            placeholder="hh:mm"
            readonly
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
        >
        <input 
            type="time"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-temporal-real"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- endif %}
        >
    </div>
{%- endmacro -%}
'''

DEFAULT_TIME_TEMPLATE = Template(FIELD_MACROS + TIME_MACROS + BASE_TEMPLATE)

SELECT_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <select 
                    name="{{ name }}[]"
                    class="pytypeinput-select pytypeinput-list-input"
                    {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                >
                    {%- for option in options %}
                    <option value="{{ option }}"{% if value == option %} selected{% endif %}>{{ option }}</option>
                    {%- endfor %}
                </select>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <select 
        id="{{ name }}"
        name="{{ name }}"
        class="pytypeinput-select"
        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
    >
        {%- for option in options %}
        <option value="{{ option }}"{% if default == option %} selected{% endif %}>{{ option }}</option>
        {%- endfor %}
    </select>
{%- endmacro -%}
'''

DEFAULT_SELECT_TEMPLATE = Template(FIELD_MACROS + SELECT_MACROS + BASE_TEMPLATE)


FILE_MACROS = '''
{%- macro render_label(name, label, is_list, is_optional, optional_enabled) -%}
    {%- if is_optional -%}
        <div class="pytypeinput-optional-header">
            <label class="pytypeinput-label">{{ label }}</label>
            <label class="pytypeinput-toggle-switch">
                <input 
                    type="checkbox" 
                    class="pytypeinput-optional-toggle"
                    data-target="{{ name }}"
                    {%- if optional_enabled %} checked{%- endif %}
                >
                <span class="pytypeinput-toggle-slider"></span>
            </label>
        </div>
    {%- else -%}
        <label for="{{ name }}" class="pytypeinput-label">
            {{ label }}
        </label>
    {%- endif -%}
{%- endmacro -%}
'''

FILE_TEMPLATE = '''
<div class="pytypeinput-field">
    {{ render_label(name, label, is_list, is_optional, optional_enabled) }}
    
    {%- if description is not none -%}
    <small class="pytypeinput-description">{{ description }}</small>
    {%- endif -%}
    
    {%- if is_optional -%}
        {%- set content_classes = ["pytypeinput-optional-content"] -%}
        {%- if not optional_enabled -%}
            {%- set _ = content_classes.append("hidden") -%}
        {%- endif -%}
        <div class="{{ content_classes|join(' ') }}" data-optional-content="{{ name }}">
    {%- endif -%}
    
    <div class="pytypeinput-file-input-wrapper">
        <input 
            type="file"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-input"
            data-file-input="{{ name }}"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if is_list %} multiple{%- endif %}
            {%- if pattern is not none %} accept="{{ pattern }}" data-pattern="{{ pattern }}"{%- endif %}
        >
        {%- if is_list -%}
        <button type="button" class="pytypeinput-file-add-more-btn" data-add-more-files="{{ name }}"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>+</button>
        {%- endif -%}
    </div>
    <div class="pytypeinput-file-list" id="fileList-{{ name }}"></div>
    
    {%- if is_optional -%}
        </div>
    {%- endif -%}
</div>
'''

DEFAULT_FILE_TEMPLATE = Template(FILE_MACROS + FILE_TEMPLATE)

SLIDER_INT_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-slider-wrapper">
                    <input 
                        type="range"
                        name="{{ name }}[]"
                        class="pytypeinput-slider pytypeinput-list-input"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- else %} value="{{ min if min is not none else 0 }}"{%- endif %}
                        {%- if min is not none %} min="{{ min }}"{%- endif %}
                        {%- if max is not none %} max="{{ max }}"{%- endif %}
                        step="{{ step }}"
                    >
                    {%- if show_value -%}
                    <output class="pytypeinput-slider-value">{{ value if value is not none else (min if min is not none else 0) }}</output>
                    {%- endif -%}
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-slider-wrapper">
        <input 
            type="range"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-slider"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- else %} value="{{ min if min is not none else 0 }}"{%- endif %}
            {%- if min is not none %} min="{{ min }}"{%- endif %}
            {%- if max is not none %} max="{{ max }}"{%- endif %}
            step="{{ step }}"
        >
        {%- if show_value -%}
        <output class="pytypeinput-slider-value" for="{{ name }}">{{ default if default is not none else (min if min is not none else 0) }}</output>
        {%- endif -%}
    </div>
{%- endmacro -%}
'''

DEFAULT_SLIDER_INT_TEMPLATE = Template(FIELD_MACROS + SLIDER_INT_MACROS + BASE_TEMPLATE)


SLIDER_FLOAT_MACROS = '''
{%- macro render_list_item_content(value=none) -%}
    <div class="pytypeinput-list-item-wrapper">
        <div class="pytypeinput-list-item">
            <div class="pytypeinput-list-item-content">
                <div class="pytypeinput-slider-wrapper">
                    <input 
                        type="range"
                        name="{{ name }}[]"
                        class="pytypeinput-slider pytypeinput-list-input"
                        data-float="true"
                        {%- if is_optional and not optional_enabled %} disabled{%- endif %}
                        {%- if value is not none %} value="{{ value }}"{%- else %} value="{{ min if min is not none else 0 }}"{%- endif %}
                        {%- if min is not none %} min="{{ min }}"{%- endif %}
                        {%- if max is not none %} max="{{ max }}"{%- endif %}
                        step="{{ step }}"
                    >
                    {%- if show_value -%}
                    <output class="pytypeinput-slider-value">{{ value if value is not none else (min if min is not none else 0) }}</output>
                    {%- endif -%}
                </div>
            </div>
            <button type="button" class="pytypeinput-list-remove"{%- if is_optional and not optional_enabled %} disabled{%- endif %}>×</button>
        </div>
    </div>
{%- endmacro -%}

{%- macro render_single_input() -%}
    <div class="pytypeinput-slider-wrapper">
        <input 
            type="range"
            id="{{ name }}"
            name="{{ name }}"
            class="pytypeinput-slider"
            data-float="true"
            {%- if is_optional and not optional_enabled %} disabled{%- endif %}
            {%- if default is not none %} value="{{ default }}"{%- else %} value="{{ min if min is not none else 0 }}"{%- endif %}
            {%- if min is not none %} min="{{ min }}"{%- endif %}
            {%- if max is not none %} max="{{ max }}"{%- endif %}
            step="{{ step }}"
        >
        {%- if show_value -%}
        <output class="pytypeinput-slider-value" for="{{ name }}">{{ default if default is not none else (min if min is not none else 0) }}</output>
        {%- endif -%}
    </div>
{%- endmacro -%}
'''

DEFAULT_SLIDER_FLOAT_TEMPLATE = Template(FIELD_MACROS + SLIDER_FLOAT_MACROS + BASE_TEMPLATE)
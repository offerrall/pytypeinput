# API Reference

Complete API documentation for pytypeinput.

## Analysis Functions

### analyze_function

Analyze function parameters and extract metadata.
```python
def analyze_function(func: Callable[..., Any], enable_warnings: bool = True) -> list[ParamMetadata]
```

**Parameters:**
- `func`: Function to analyze
- `enable_warnings`: Whether to emit warnings (default: `True`)

**Returns:**
- List of `ParamMetadata` objects, one for each parameter

**Example:**
```python
from pytypeinput import analyze_function, Field, Annotated

def create_user(
    username: Annotated[str, Field(min_length=3)],
    age: int,
    active: bool = True
):
    pass

params = analyze_function(create_user)

print(params[0].name)        # "username"
print(params[0].param_type)  # <class 'str'>
print(params[0].constraints) # Field(min_length=3)
print(params[1].name)        # "age"
print(params[2].default)     # True
```

---

### analyze_dataclass

Analyze Python dataclass fields.
```python
def analyze_dataclass(cls: type, enable_warnings: bool = True) -> list[ParamMetadata]
```

**Parameters:**
- `cls`: Dataclass type to analyze
- `enable_warnings`: Whether to emit warnings (default: `True`)

**Returns:**
- List of `ParamMetadata` objects, one for each field

**Raises:**
- `TypeError`: If `cls` is not a dataclass

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, Field, Annotated

@dataclass
class User:
    username: Annotated[str, Field(min_length=3)]
    age: int
    active: bool = True

params = analyze_dataclass(User)

print(params[0].name)        # "username"
print(params[0].constraints) # Field(min_length=3)
print(params[2].default)     # True
```

**Notes:**
- `field(init=False)` fields are skipped
- `field(default_factory=...)` is evaluated at analysis time
- `ClassVar` fields are skipped
- Set `enable_warnings=False` to suppress warnings about unsupported features

---

### analyze_pydantic_model

Analyze Pydantic model fields.
```python
def analyze_pydantic_model(model: type[BaseModel], enable_warnings: bool = True) -> list[ParamMetadata]
```

**Parameters:**
- `model`: Pydantic BaseModel to analyze
- `enable_warnings`: Whether to emit warnings (default: `True`)

**Returns:**
- List of `ParamMetadata` objects, one for each field

**Raises:**
- `TypeError`: If `model` is not a Pydantic BaseModel

**Example:**
```python
from pydantic import BaseModel
from pytypeinput import analyze_pydantic_model, Field, Annotated

class User(BaseModel):
    username: Annotated[str, Field(min_length=3)]
    age: int
    active: bool = True

params = analyze_pydantic_model(User)

print(params[0].name)        # "username"
print(params[0].constraints) # Field(min_length=3)
```

---

### analyze_class_init

Analyze class `__init__` method parameters.
```python
def analyze_class_init(cls: type, enable_warnings: bool = True) -> list[ParamMetadata]
```

**Parameters:**
- `cls`: Class type to analyze
- `enable_warnings`: Whether to emit warnings (default: `True`)

**Returns:**
- List of `ParamMetadata` objects for each `__init__` parameter (excluding `self`)

**Raises:**
- `TypeError`: If `cls` doesn't have `__init__` or has unsupported parameter types

**Example:**
```python
from pytypeinput import analyze_class_init, Field, Annotated

class User:
    def __init__(
        self,
        username: Annotated[str, Field(min_length=3)],
        age: int
    ):
        self.username = username
        self.age = age

params = analyze_class_init(User)

print(params[0].name)        # "username"
print(params[1].name)        # "age"
```

---

### analyze_type

Analyze a standalone type annotation.
```python
def analyze_type(annotation: Any, name: str = "field", enable_warnings: bool = True) -> ParamMetadata
```

**Parameters:**
- `annotation`: Type annotation to analyze
- `name`: Name to assign to the parameter (default: `"field"`)
- `enable_warnings`: Whether to emit warnings (default: `True`)

**Returns:**
- Single `ParamMetadata` object

**Example:**
```python
from pytypeinput import analyze_type, Field, Label, Annotated

Username = Annotated[
    str,
    Field(min_length=3, max_length=20),
    Label("Username")
]

param = analyze_type(Username, name="username")

print(param.name)        # "username"
print(param.ui.label)    # "Username"
print(param.constraints) # Field(min_length=3, max_length=20)
```

---

## Metadata Classes

### ParamMetadata

Complete metadata for a parameter.
```python
class ParamMetadata:
    name: str
    param_type: type
    default: Any = None
    constraints: FieldInfo | None = None
    widget_type: str | None = None
    optional: OptionalMetadata | None = None
    list: ListMetadata | None = None
    choices: ChoiceMetadata | None = None
    ui: UIMetadata | None = None
```

**Attributes:**
- `name`: Parameter name
- `param_type`: Base Python type (`int`, `str`, `bool`, `date`, `time`, `float`)
- `default`: Default value if provided
- `constraints`: Pydantic `FieldInfo` with validation constraints
- `widget_type`: Special widget type (`"Color"`, `"Email"`, `"ImageFile"`, etc.)
- `optional`: Optional metadata if parameter is optional
- `list`: List metadata if parameter is a list
- `choices`: Choice metadata if parameter has fixed options (Enum, Literal, Dropdown)
- `ui`: UI customization metadata

**Methods:**

#### reload_choices

Reload choices from Dropdown function if available.
```python
def reload_choices(self, validate_default: bool = True) -> None
```

**Parameters:**
- `validate_default`: If `True` (default), validates that current default is in the new options. If `False`, skips validation.

**Returns:**
- None (modifies `choices.options` in place)

**Raises:**
- `RuntimeError`: If parameter has no choices or choices are static (Enum/Literal)
- `ValueError`: If `validate_default=True` and default not in new options
- `TypeError`: If options function returns invalid type

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, Dropdown, Annotated

# Simulate dynamic database
_db_users = ["alice", "bob"]

def get_users():
    return _db_users.copy()

@dataclass
class AssignTaskForm:
    assignee: Annotated[str, Dropdown(get_users)]

# Analyze once
params = analyze_dataclass(AssignTaskForm)
print(params[0].choices.options)  # ('alice', 'bob')

# Simulate DB change
_db_users.append("charlie")

# Reload options
params[0].reload_choices()
print(params[0].choices.options)  # ('alice', 'bob', 'charlie')

# Skip validation if you'll update default separately
params[0].reload_choices(validate_default=False)
```

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, Field, Email, Annotated

@dataclass
class ContactForm:
    email: Email
    age: Annotated[int, Field(ge=18)]

params = analyze_dataclass(ContactForm)

# Email parameter
print(params[0].name)         # "email"
print(params[0].widget_type)  # "Email"
print(params[0].param_type)   # <class 'str'>

# Age parameter
print(params[1].name)         # "age"
print(params[1].param_type)   # <class 'int'>
print(params[1].constraints)  # Field(ge=18)
```

---

### ListMetadata

Metadata for list parameters.
```python
class ListMetadata:
    constraints: FieldInfo | None = None
```

**Attributes:**
- `constraints`: Pydantic `FieldInfo` with `min_length`/`max_length` for the list

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, Field, Annotated

@dataclass
class TagsForm:
    tags: Annotated[list[str], Field(min_length=1, max_length=5)]

params = analyze_dataclass(TagsForm)

print(params[0].list.constraints)  # Field(min_length=1, max_length=5)
```

---

### OptionalMetadata

Metadata for optional parameters.
```python
class OptionalMetadata:
    enabled: bool = False
```

**Attributes:**
- `enabled`: Whether the optional field is enabled by default
  - `True` if has a non-`None` default or `OptionalEnabled` marker
  - `False` if default is `None` or `OptionalDisabled` marker

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, OptionalEnabled

@dataclass
class UserForm:
    bio: str | None = None  # enabled=False
    nickname: str | None = "Guest"  # enabled=True
    middle_name: str | OptionalEnabled = None  # enabled=True

params = analyze_dataclass(UserForm)

print(params[0].optional.enabled)  # False
print(params[1].optional.enabled)  # True
print(params[2].optional.enabled)  # True
```

---

### ChoiceMetadata

Metadata for choice-based parameters (Enum, Literal, Dropdown).
```python
class ChoiceMetadata:
    enum_class: type | None = None
    options_function: Any = None
    options: tuple | None = None
```

**Attributes:**
- `enum_class`: The Enum class if parameter is an Enum type
- `options_function`: Function that returns options for `Dropdown`
- `options`: Tuple of available choice values

**Example:**
```python
from dataclasses import dataclass
from enum import Enum
from typing import Literal
from pytypeinput import analyze_dataclass, Dropdown, Annotated

class Priority(Enum):
    LOW = "Low"
    HIGH = "High"

def get_colors():
    return ["Red", "Blue", "Green"]

@dataclass
class TaskForm:
    priority: Priority
    size: Literal["S", "M", "L"]
    color: Annotated[str, Dropdown(get_colors)]

params = analyze_dataclass(TaskForm)

# Enum
print(params[0].choices.enum_class)  # <enum 'Priority'>
print(params[0].choices.options)     # ("Low", "High")

# Literal
print(params[1].choices.enum_class)  # None
print(params[1].choices.options)     # ("S", "M", "L")

# Dropdown
print(params[2].choices.options_function)  # <function get_colors>
print(params[2].choices.options)           # ("Red", "Blue", "Green")
```

---

### UIMetadata

UI customization metadata.
```python
class UIMetadata:
    step: int | float = 1
    is_password: bool = False
    is_slider: bool = False
    show_slider_value: bool = True
    placeholder: str | None = None
    pattern_message: str | None = None
    description: str | None = None
    label: str | None = None
    rows: int | None = None
```

**Attributes:**
- `step`: Step increment for number inputs (default: 1)
- `is_password`: Whether to render string input as password field
- `is_slider`: Whether to render number input as slider widget
- `show_slider_value`: Whether to display current value next to slider
- `placeholder`: Placeholder text for input fields
- `pattern_message`: Custom error message for pattern validation
- `description`: Help text displayed below the input field
- `label`: Custom label text (overrides parameter name)
- `rows`: Number of visible rows for textarea (multi-line input)

**Example:**
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass, Label, Description, Placeholder, Annotated

@dataclass
class UserForm:
    username: Annotated[
        str,
        Label("Username"),
        Description("Choose a unique username"),
        Placeholder("Enter username")
    ]

params = analyze_dataclass(UserForm)

print(params[0].ui.label)        # "Username"
print(params[0].ui.description)  # "Choose a unique username"
print(params[0].ui.placeholder)  # "Enter username"
```

---

## UI Metadata Classes

### Label

Custom label text (overrides auto-generated label).
```python
class Label:
    def __init__(self, text: str)
```

**Example:**
```python
from pytypeinput import Label, Annotated

username: Annotated[str, Label("Full Name")]
```

---

### Description

Help text displayed below the input field.
```python
class Description:
    def __init__(self, text: str)
```

**Example:**
```python
from pytypeinput import Description, Annotated

api_key: Annotated[str, Description("Your API key from the dashboard")]
```

---

### Placeholder

Placeholder text for input fields.
```python
class Placeholder:
    def __init__(self, text: str)
```

**Example:**
```python
from pytypeinput import Placeholder, Annotated

search: Annotated[str, Placeholder("Search products...")]
```

---

### PatternMessage

Custom error message for pattern validation.
```python
class PatternMessage:
    def __init__(self, message: str)
```

**Example:**
```python
from pytypeinput import Field, PatternMessage, Annotated

username: Annotated[
    str,
    Field(pattern=r'^[a-zA-Z0-9_]+$'),
    PatternMessage("Only letters, numbers, and underscores allowed")
]
```

---

### Rows

Number of visible text rows for textarea (multi-line input).
```python
class Rows:
    def __init__(self, count: int)
```

**Example:**
```python
from pytypeinput import Rows, Annotated

bio: Annotated[str, Rows(5)]
```

---

### Step

Step increment for number inputs.
```python
class Step:
    def __init__(self, value: int | float = 1)
```

**Example:**
```python
from pytypeinput import Step, Annotated

quantity: Annotated[int, Step(5)]
price: Annotated[float, Step(0.25)]
```

---

### Slider

Render number input as slider widget.

**Requires:** `Field(ge=..., le=...)` constraints
```python
class Slider:
    def __init__(self, show_value: bool = True)
```

**Parameters:**
- `show_value`: Whether to display current value next to slider (default: `True`)

**Example:**
```python
from pytypeinput import Field, Slider, Annotated

volume: Annotated[int, Field(ge=0, le=100), Slider()]
brightness: Annotated[float, Field(ge=0.0, le=1.0), Slider(show_value=False)]
```

---

### Dropdown

Dropdown selector with dynamic options from a function.
```python
class Dropdown:
    def __init__(self, options_function: Callable)
```

**Parameters:**
- `options_function`: Callable that returns a list/tuple of options

**Example:**
```python
from pytypeinput import Dropdown, Annotated

def get_countries():
    return ["USA", "Canada", "Mexico", "UK"]

country: Annotated[str, Dropdown(get_countries)]
```

---

### IsPassword

Marker to render string input as password field.
```python
class IsPassword:
    pass
```

**Example:**
```python
from pytypeinput import IsPassword, Annotated

password: Annotated[str, IsPassword]
```

---

## Special Types

### Email

Email input with validation.
```python
Email = Annotated[str, Field(pattern=...), PatternMessage(...), Placeholder(...)]
```

**Example:**
```python
from pytypeinput import Email

email: Email
```

---

### Color

Color picker input.
```python
Color = Annotated[str, Field(pattern=...)]
```

**Example:**
```python
from pytypeinput import Color

primary_color: Color
```

---

### File Types

File upload inputs with specific accept patterns:

- `File` - Any file type
- `ImageFile` - `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, etc.
- `VideoFile` - `.mp4`, `.mov`, `.avi`, `.mkv`, etc.
- `AudioFile` - `.mp3`, `.wav`, `.aac`, `.flac`, etc.
- `DataFile` - `.csv`, `.xlsx`, `.json`, `.xml`, etc.
- `TextFile` - `.txt`, `.md`, `.log`, `.rtf`
- `DocumentFile` - `.pdf`, `.doc`, `.docx`, `.ppt`, `.xls`, etc.

**Example:**
```python
from pytypeinput import ImageFile, DocumentFile

avatar: ImageFile
resume: DocumentFile
attachments: list[File]
```

---

## Optional Markers

### OptionalEnabled

Force optional field to be enabled by default.
```python
OptionalEnabled = Annotated[None, _OptionalEnabledMarker()]
```

**Example:**
```python
from pytypeinput import OptionalEnabled

nickname: str | OptionalEnabled = None  # Enabled by default
```

---

### OptionalDisabled

Force optional field to be disabled by default.
```python
OptionalDisabled = Annotated[None, _OptionalDisabledMarker()]
```

**Example:**
```python
from pytypeinput import OptionalDisabled

debug_mode: str | OptionalDisabled = "false"  # Disabled by default
```

---

## HTML Renderer

### HTMLRenderer

HTML form renderer with customizable styles and validation.
```python
class HTMLRenderer:
    def __init__(
        self,
        custom_styles: str | None = None,
        enable_validation: bool = True
    )
```

**Parameters:**
- `custom_styles`: Custom CSS to use instead of defaults
- `enable_validation`: Whether to enable client-side validation

**Methods:**

#### render_param

Render a single parameter as HTML.
```python
def render_param(self, param: ParamMetadata) -> str
```

**Returns:**
- HTML string for the parameter field

**Example:**
```python
from pytypeinput import analyze_dataclass
from pytypeinput.html import HTMLRenderer

@dataclass
class UserForm:
    username: str

params = analyze_dataclass(UserForm)
renderer = HTMLRenderer()

html = renderer.render_param(params[0])
print(html)  # <div class="pytypeinput-field">...</div>
```

---

#### get_styles

Get current CSS styles wrapped in `<style>` tag.
```python
def get_styles(self) -> str
```

**Returns:**
- HTML style tag with CSS

**Example:**
```python
renderer = HTMLRenderer()
styles = renderer.get_styles()
print(styles)  # <style>/* CSS here */</style>
```

---

#### get_validation_script

Get validation JavaScript wrapped in `<script>` tag.
```python
def get_validation_script(self) -> str
```

**Returns:**
- HTML script tag with validation code, or empty string if disabled

**Example:**
```python
renderer = HTMLRenderer()
script = renderer.get_validation_script()
print(script)  # <script>/* JS here */</script>

renderer_no_validation = HTMLRenderer(enable_validation=False)
script = renderer_no_validation.get_validation_script()
print(script)  # ""
```

---

#### get_default_styles (static)

Get default CSS styles wrapped in `<style>` tag.
```python
@staticmethod
def get_default_styles() -> str
```

**Returns:**
- HTML style tag with default CSS

**Example:**
```python
from pytypeinput.html import HTMLRenderer

styles = HTMLRenderer.get_default_styles()
print(styles)  # <style>/* Default CSS */</style>
```

---

#### list_css_variables (static)

List all available CSS custom properties.
```python
@staticmethod
def list_css_variables() -> list[str]
```

**Returns:**
- Sorted list of CSS variable names

**Example:**
```python
from pytypeinput.html import HTMLRenderer

variables = HTMLRenderer.list_css_variables()
print(variables)
# ['--pytypeinput-border-radius', '--pytypeinput-input-bg', ...]
```
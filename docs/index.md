# pytypeinput

Extract structured metadata from Python type hints for building UIs.

## Quick Example
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, Label, Description, PatternMessage, analyze_dataclass

@dataclass
class User:
    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        Label("Username"),
        Description("Choose a unique username (letters, numbers, underscore only)"),
        PatternMessage("Username can only contain letters, numbers, and underscores.")
    ]
    age: Annotated[int, Field(ge=18, le=120)]
    bio: str | None = None

# Extract metadata
params = analyze_dataclass(User)

# Now you have structured data for each field:
print(params[0].name)           # "username"
print(params[0].param_type)     # str
print(params[0].constraints)    # Field(min_length=3, max_length=20, pattern=...)
print(params[0].ui.label)       # "Username"
print(params[0].ui.description) # "Choose a unique username..."

print(params[1].name)           # "age"
print(params[1].constraints)    # Field(ge=18, le=120)

print(params[2].name)           # "bio"
print(params[2].optional)       # OptionalMetadata(enabled=False)
```

### HTML Renderer Demo

The HTML renderer generates this interactive form from the User class:

<iframe src="./demos/user_form.html" 
        width="100%" 
        height="400" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

**Try the validation:**

- Username: 3-20 characters, letters/numbers/underscore only
- Age must be 18-120
- Bio is optional (toggle it on/off)

## What Can You Analyze?

pytypeinput works with functions, dataclasses, Pydantic models, classes, and standalone types:
```python
from pytypeinput import analyze_function, analyze_dataclass, analyze_pydantic_model, analyze_class_init, analyze_type

# Functions
def create_user(username: str, age: int):
    pass
params = analyze_function(create_user)

# Dataclasses
@dataclass
class User:
    username: str
    age: int
params = analyze_dataclass(User)

# Pydantic Models
from pydantic import BaseModel
class User(BaseModel):
    username: str
    age: int
params = analyze_pydantic_model(User)

# Class __init__
class User:
    def __init__(self, username: str, age: int):
        pass
params = analyze_class_init(User)

# Standalone Types
Username = Annotated[str, Field(min_length=3)]
param = analyze_type(Username, name="username")
```

## Installation

Core only:
```bash
pip install pytypeinput
```
With HTML renderer:
```bash
pip install pytypeinput[html]
```

## Documentation

**Type System:**

- **[Basic Types](basic-types.md)** - `int`, `float`, `str`, `bool`, `date`, `time`
- **[Special Types](special-types.md)** - `Email`, `Color`, `File`, `ImageFile`, etc.
- **[Lists](lists.md)** - `list[Type]` with item and list-level validation
- **[Optionals](optionals.md)** - `Type | None` with toggle switches
- **[Choices](choices.md)** - `Literal`, `Enum`, `Dropdown(func)`

**Validation & UI:**

- **[Constraints](constraints.md)** - `Field(min=, max=, pattern=)` for validation
- **[UI Metadata](ui-metadata.md)** - Custom labels, descriptions, placeholders, sliders

**Renderers:**

- **[HTML Renderer](html-renderer.md)** - Generate forms with client-side validation

**Reference:**

- **[API Reference](api.md)** - Complete API documentation
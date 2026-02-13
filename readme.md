# PyTypeInput 1.0.2

[![PyPI version](https://img.shields.io/pypi/v/pytypeinput)](https://pypi.org/project/pytypeinput/)
[![Python](https://img.shields.io/pypi/pyversions/pytypeinput)](https://pypi.org/project/pytypeinput/)
[![Tests](https://img.shields.io/badge/tests-1778%2B-brightgreen)]()
[![License](https://img.shields.io/pypi/l/pytypeinput)](https://pypi.org/project/pytypeinput/)

**Define parameters with Python type hints. Get complete UI metadata automatically.**

PyTypeInput analyzes standard Python type annotations and extracts everything a frontend needs to render forms: types, constraints, choices, labels, defaults, and validation — all from a single source of truth.

> For interactive documentation, live examples, and full integration, see [**FuncToWeb**](https://github.com/offerrall/functoweb) — which uses PyTypeInput as its core engine.

---

## Quick Example

```python
from typing import Annotated, Literal
from pydantic import Field
from pytypeinput import analyze_function
from pytypeinput.types import Label, Slider, Email, Description, Rows

def create_user(
    name: Annotated[str, Label("Full Name"), Field(min_length=2, max_length=50)],
    email: Email,
    age: Annotated[int, Slider(), Field(ge=0, le=120)] = 25,
    role: Literal["admin", "user", "viewer"] = "user",
    bio: Annotated[str, Description("Short biography"), Rows(4)] | None = None,
):
    ...

params = analyze_function(create_user)

for p in params:
    print(p.name, "→", p.param_type.__name__)
# name  → str
# email → str
# age   → int
# role  → str
# bio   → str
```

Each `ParamMetadata` object carries the full picture: type, default, constraints, choices, labels, and a precompiled validator. The frontend resolves the appropriate widget from `param_type`, `item_ui`, `choices`, and `special_widget`.

---

## Installation

```bash
pip install pytypeinput
```

---

## Dependencies

- **Python** 3.10+
- **Pydantic** 2.x

---

## What You Can Analyze

PyTypeInput works with any of these sources — same output format regardless:

```python
from pytypeinput import analyze_function, analyze_pydantic_model, analyze_dataclass, analyze_class_init

# Functions
params = analyze_function(my_func)

# Pydantic models
params = analyze_pydantic_model(MyModel)

# Dataclasses
params = analyze_dataclass(MyDataclass)

# Any class with __init__
params = analyze_class_init(MyClass)
```

---

## Widget Resolution

The frontend determines which widget to render based on the metadata fields:

| Metadata | Widget | Example |
|---|---|---|
| `param_type` = `str` | Text input | `name: str` |
| `param_type` = `int` or `float` | Number input | `age: int` |
| `param_type` = `bool` | Checkbox | `flag: bool` |
| `param_type` = `date` | Date picker | `birthday: date` |
| `param_type` = `time` | Time picker | `meeting: time` |
| `choices` present | Dropdown | `Enum`, `Literal`, `Dropdown(func)` |
| `item_ui.is_slider` = `True` | Slider | `Annotated[int, Slider()]` |
| `item_ui.is_password` = `True` | Password | `Annotated[str, IsPassword()]` |
| `item_ui.rows` set | Textarea | `Annotated[str, Rows(4)]` |
| `special_widget` = `"Color"` | Color picker | `Color` |
| `special_widget` = `"File"` | File input | `ImageFile`, `File`, etc. |

---

## UI Metadata

Annotate parameters with descriptive metadata that frontends can use to render labels, placeholders, and more:

```python
from pytypeinput.types import Label, Description, Placeholder, Step, Rows, PatternMessage

# Label and description
name: Annotated[str, Label("Your Name"), Description("As it appears on your ID")]

# Placeholder text
city: Annotated[str, Placeholder("e.g., Madrid")]

# Numeric step
quantity: Annotated[int, Step(5)]

# Textarea
notes: Annotated[str, Rows(4)]

# Custom pattern error message
code: Annotated[str, Field(pattern=r"^\d{4}$"), PatternMessage("Must be a 4-digit code")]
```

---

## Constraints

Constraints come from Pydantic's `Field()` and are validated at analysis time and at runtime:

```python
from pydantic import Field

# Numeric bounds
age: Annotated[int, Field(ge=0, le=150)]
price: Annotated[float, Field(gt=0, lt=10000)]

# String constraints
username: Annotated[str, Field(min_length=3, max_length=20)]
hex_code: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
```

---

## Choices

Three ways to define a set of valid options:

```python
from enum import Enum
from typing import Literal
from pytypeinput.types import Dropdown

# Enum — options extracted from values
class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

color: Color = Color.RED

# Literal — inline options
size: Literal["S", "M", "L", "XL"] = "M"

# Dropdown — dynamic options from a callable
def get_users():
    return ["alice", "bob", "charlie"]

user: Annotated[str, Dropdown(get_users)]
```

Dynamic dropdowns can be refreshed at any time via `param.refresh_choices()`.

---

## Lists

Supports `list[T]` with optional length constraints. All item-level annotations (choices, constraints, UI) apply to each element:

```python
# Simple list
tags: list[str]

# List with length constraints
scores: Annotated[list[int], Field(min_length=1, max_length=10)]

# List of choices
colors: list[Literal["red", "green", "blue"]]

# Item-level constraints apply to each element
prices: list[Annotated[float, Field(ge=0.0, le=9999.99), Step(0.01)]]

# Item-level slider with bounds
volumes: list[Annotated[int, Slider(), Field(ge=0, le=100), Step(5)]]

# List constraints + item constraints combined
ratings: Annotated[list[Annotated[int, Field(ge=1, le=5)]], Field(min_length=1, max_length=10)]

# Items with special types
photos: list[ImageFile]
emails: Annotated[list[Email], Field(min_length=1, max_length=5)]

# Items with dropdown
tags: list[Annotated[str, Dropdown(get_available_tags)]]
```

**Label and Description** on lists follow a priority rule: if `Label`/`Description` is on the outer list annotation, it wins. If not, it's read from the inner item type. This means you can define reusable labeled items and the label propagates automatically:

```python
# Label on the outer level → "Scores" is used
scores: Annotated[list[int], Label("Scores")]

# Label on the inner item → "Tag Name" propagates to the list
items: list[Annotated[str, Label("Tag Name")]]

# Both levels → outer "My Tags" wins over inner "Tag Name"
items: Annotated[list[Annotated[str, Label("Tag Name")]], Label("My Tags")]
```

> Nested lists (`list[list[...]]`) are not supported by design.

---

## Optional Fields

`T | None` marks a field as optional. Control the initial toggle state with defaults or explicit markers:

```python
from pytypeinput.types import OptionalEnabled, OptionalDisabled

# Toggle off by default (no default or default is None)
nickname: str | None = None

# Toggle on by default (has a non-None default)
theme: str | None = "dark"

# Explicit control
notes: str | OptionalEnabled = None     # Toggle starts ON
code: str | OptionalDisabled = "ABC"    # Toggle starts OFF
```

---

## Validation

`validate_value` coerces and validates runtime values (including raw strings from forms) against the analyzed metadata:

```python
from pytypeinput import analyze_function
from pytypeinput.validate import validate_value

params = analyze_function(my_func)
meta = params[0]

# Coerces types: "42" → 42, "true" → True, "2024-01-15" → date(...)
value = validate_value(meta, "42")

# Validates constraints, choices, and types
# Raises ValueError or TypeError on invalid input
```

Coercion rules:
- Strings to `int`, `float`, `bool`, `date`, `time`
- Enum values or names to Enum instances
- JSON form primitives to native Python types

---

## Output Format

Every analyzed parameter returns a `ParamMetadata` dataclass:

```python
param.name             # "age"
param.param_type       # int
param.default          # 25
param.special_widget   # "Color", "File", or None
param.optional         # OptionalMetadata(enabled=False) or None
param.constraints      # ConstraintsMetadata(ge=0, le=120, ...) or None
param.choices          # ChoiceMetadata(options=(...), ...) or None
param.item_ui          # ItemUIMetadata(is_slider=True, ...) or None
param.param_ui         # ParamUIMetadata(label="Age", ...) or None
param.list             # ListMetadata(min_length=..., ...) or None

# Serialize to dict for JSON/frontend consumption
# Only non-None fields are included
param.to_dict()
```

---

## Special Types

Ready-to-use annotated types with built-in patterns and widget resolution:

```python
from pytypeinput.types import Color, Email, ImageFile, VideoFile, AudioFile, DataFile, TextFile, DocumentFile, File

avatar: ImageFile          # Accepts .png, .jpg, .webp, etc.
document: DocumentFile     # Accepts .pdf, .doc, .docx, etc.
theme_color: Color         # Hex color with picker widget
contact: Email             # Email with validation and placeholder
attachment: File           # Any file
```

---

## Composition

Types can be layered using `Annotated` to build reusable, composable building blocks. Each layer can add constraints, UI metadata, or both — and later layers override earlier ones for the same attribute.

```python
# Base constrained types
PositiveInt = Annotated[int, Field(ge=0)]
BoundedInt = Annotated[int, Field(ge=0, le=100)]
SmallStr = Annotated[str, Field(min_length=1, max_length=50)]
LongStr = Annotated[str, Field(min_length=1, max_length=5000)]
UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]

# Add UI on top of constraints
SliderInt = Annotated[BoundedInt, Slider()]
SliderStep5 = Annotated[BoundedInt, Slider(), Step(5)]
PasswordStr = Annotated[SmallStr, IsPassword()]
TextAreaStr = Annotated[LongStr, Rows(10)]
StepFloat = Annotated[UnitFloat, Step(0.01)]

# Add labels/descriptions on top of everything
LabeledSlider = Annotated[SliderInt, Label("Volume")]
FullSlider = Annotated[SliderStep5, Label("Level"), Description("Set level")]
FullPassword = Annotated[PasswordStr, Label("Password"), Description("Enter password"), Placeholder("********")]
FullTextArea = Annotated[TextAreaStr, Label("Notes"), Description("Add notes"), Placeholder("Write...")]
```

Constraints merge across layers, and **later values override earlier ones** for the same attribute:

```python
# ge=0 from PositiveInt, le=100 added → both apply
Annotated[PositiveInt, Field(le=100)]

# ge=0 from PositiveInt, then ge=10 overrides → ge=10
Annotated[PositiveInt, Field(ge=10)]

# Three levels deep: ge=0 → ge=5 → ge=10 → final ge=10
L1 = Annotated[int, Field(ge=0)]
L2 = Annotated[L1, Field(ge=5)]
L3 = Annotated[L2, Field(ge=10)]
```

This lets you define your type vocabulary once and reuse it across functions, models, and dataclasses without repeating constraints or UI hints.

---

## Project Structure

```
pytypeinput/
├── analyzer.py          # Single-type analysis pipeline
├── analyzers.py         # Function, Pydantic, dataclass, class analyzers
├── validate.py          # Runtime validation and coercion
├── param.py             # Metadata dataclasses
├── types.py             # UI markers, special types, patterns
├── helpers.py           # Annotated rebuilding, serialization
└── extractors/          # 10-step pipeline (internal)
    ├── validate_type_01.py
    ├── validate_optional_02.py
    ├── extract_param_ui_03.py
    ├── extract_list_04.py
    ├── extract_item_ui_05.py
    ├── extract_choices_06.py
    ├── extract_constraints_07.py
    ├── validate_final_08.py
    ├── resolve_widget_09.py
    └── normalize_default_10.py
```

---

## License

MIT
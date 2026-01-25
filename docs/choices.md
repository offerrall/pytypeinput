# Choices

pytypeinput supports three types of choice-based inputs: `Literal`, `Enum`, and `Dropdown`.

## Literal

Fixed string choices using `Literal`:
```python
from dataclasses import dataclass
from typing import Literal
from pytypeinput import analyze_dataclass

@dataclass
class SizeForm:
    size: Literal["Small", "Medium", "Large"]

params = analyze_dataclass(SizeForm)

print(params[0].name)     # "size"
print(params[0].choices)  # ChoiceMetadata(options=("Small", "Medium", "Large"))
```

**HTML Renderer Demo:**

<iframe src="../demos/literal_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Literal with Numbers

Literal works with integers and floats:
```python
from dataclasses import dataclass
from typing import Literal
from pytypeinput import analyze_dataclass

@dataclass
class RatingForm:
    stars: Literal[1, 2, 3, 4, 5]
    score: Literal[0.0, 2.5, 5.0, 7.5, 10.0]

params = analyze_dataclass(RatingForm)

print(params[0].choices.options)  # (1, 2, 3, 4, 5)
print(params[1].choices.options)  # (0.0, 2.5, 5.0, 7.5, 10.0)
```

**HTML Renderer Demo:**

<iframe src="../demos/literal_numbers.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Enum

Choices using Python Enum:
```python
from dataclasses import dataclass
from enum import Enum
from pytypeinput import analyze_dataclass

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

@dataclass
class TaskForm:
    priority: Priority

params = analyze_dataclass(TaskForm)

print(params[0].name)          # "priority"
print(params[0].choices.enum_class)  # <enum 'Priority'>
print(params[0].choices.options)     # ("Low", "Medium", "High")
```

**HTML Renderer Demo:**

<iframe src="../demos/enum_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Enum with Integer Values

Enums can have integer values:
```python
from dataclasses import dataclass
from enum import Enum
from pytypeinput import analyze_dataclass

class Rating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

@dataclass
class ReviewForm:
    rating: Rating

params = analyze_dataclass(ReviewForm)

print(params[0].choices.options)  # (1, 2, 3, 4, 5)
```

**HTML Renderer Demo:**

<iframe src="../demos/enum_int.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Dropdown

Dynamic choices from a function:
```python
from dataclasses import dataclass
from pytypeinput import Annotated, Dropdown, analyze_dataclass

def get_countries():
    return ["USA", "Canada", "Mexico", "UK", "Germany", "France"]

@dataclass
class LocationForm:
    country: Annotated[str, Dropdown(get_countries)]

params = analyze_dataclass(LocationForm)

print(params[0].name)     # "country"
print(params[0].choices.options_function)  # <function get_countries>
print(params[0].choices.options)  # ("USA", "Canada", ...)
```

**HTML Renderer Demo:**

<iframe src="../demos/dropdown_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Dropdown with Integers

Dropdown functions can return integers:
```python
from dataclasses import dataclass
from pytypeinput import Annotated, Dropdown, analyze_dataclass

def get_years():
    return [2020, 2021, 2022, 2023, 2024, 2025]

@dataclass
class YearForm:
    year: Annotated[int, Dropdown(get_years)]

params = analyze_dataclass(YearForm)

print(params[0].param_type)       # <class 'int'>
print(params[0].choices.options)  # (2020, 2021, 2022, ...)
```

**HTML Renderer Demo:**

<iframe src="../demos/dropdown_int.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Default Values

All choice types support defaults:
```python
from dataclasses import dataclass
from typing import Literal
from enum import Enum
from pytypeinput import Annotated, Dropdown, analyze_dataclass

class Status(Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"

def get_themes():
    return ["Light", "Dark", "Auto"]

@dataclass
class SettingsForm:
    visibility: Literal["Public", "Private"] = "Public"
    status: Status = Status.DRAFT
    theme: Annotated[str, Dropdown(get_themes)] = "Auto"

params = analyze_dataclass(SettingsForm)

print(params[0].default)  # "Public"
print(params[1].default)  # "Draft"
print(params[2].default)  # "Auto"
```

**HTML Renderer Demo:**

<iframe src="../demos/choices_defaults.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
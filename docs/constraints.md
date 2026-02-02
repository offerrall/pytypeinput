# Constraints

pytypeinput uses Pydantic's `Field` to add validation constraints to parameters.

## String Constraints

### Min/Max Length

Limit string length:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class UserForm:
    username: Annotated[str, Field(min_length=3, max_length=20)]
    bio: Annotated[str, Field(max_length=500)]

params = analyze_dataclass(UserForm)

print(params[0].constraints)  # Field(min_length=3, max_length=20)
print(params[1].constraints)  # Field(max_length=500)
```

**HTML Renderer Demo:**

<iframe src="../demos/str_constraints.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try typing less than 3 or more than 20 characters!

### Pattern (Regex)

Validate with regular expressions:
```python
from dataclasses import dataclass
from pytypeinput import Field, PatternMessage, Annotated, analyze_dataclass

@dataclass
class AccountForm:
    username: Annotated[
        str,
        Field(pattern=r'^[a-zA-Z0-9_]+$'),
        PatternMessage("Only letters, numbers, and underscores allowed")
    ]

params = analyze_dataclass(AccountForm)

print(params[0].constraints)           # Field(pattern=...)
print(params[0].ui.pattern_message)    # "Only letters, numbers..."
```

**HTML Renderer Demo:**

<iframe src="../demos/str_pattern.html" 
        width="100%" 
        height="180" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try entering special characters like `@` or `#`!

## Integer Constraints

### Range (ge/le)

Constrain integer values with greater-or-equal (`ge`) and less-or-equal (`le`):
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class UserForm:
    age: Annotated[int, Field(ge=18, le=120)]
    rating: Annotated[int, Field(ge=1, le=5)]

params = analyze_dataclass(UserForm)

print(params[0].constraints)  # Field(ge=18, le=120)
print(params[1].constraints)  # Field(ge=1, le=5)
```

**HTML Renderer Demo:**

<iframe src="../demos/int_constraints.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try entering values outside the allowed range!

### Strict Bounds (gt/lt)

Use greater-than (`gt`) and less-than (`lt`) for exclusive bounds:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class ScoreForm:
    percentage: Annotated[int, Field(gt=0, lt=100)]  # 1-99

params = analyze_dataclass(ScoreForm)

print(params[0].constraints)  # Field(gt=0, lt=100)
```

**HTML Renderer Demo:**

<iframe src="../demos/int_strict.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Values 0 and 100 are not allowed!

## Float Constraints

### Range (ge/le)

Constrain decimal values:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class ProductForm:
    price: Annotated[float, Field(ge=0.0, le=9999.99)]
    rating: Annotated[float, Field(ge=0.0, le=5.0)]

params = analyze_dataclass(ProductForm)

print(params[0].constraints)  # Field(ge=0.0, le=9999.99)
print(params[1].constraints)  # Field(ge=0.0, le=5.0)
```

**HTML Renderer Demo:**

<iframe src="../demos/float_constraints.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Strict Bounds (gt/lt)

Exclusive bounds for floats:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class MeasurementForm:
    temperature: Annotated[float, Field(gt=-273.15)]  # Above absolute zero

params = analyze_dataclass(MeasurementForm)

print(params[0].constraints)  # Field(gt=-273.15)
```

**HTML Renderer Demo:**

<iframe src="../demos/float_strict.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## List Constraints

### List Length

Limit the number of items in a list:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class TagsForm:
    tags: Annotated[list[str], Field(min_length=1, max_length=5)]
    categories: Annotated[list[str], Field(min_length=2)]

params = analyze_dataclass(TagsForm)

print(params[0].list.constraints)  # Field(min_length=1, max_length=5)
print(params[1].list.constraints)  # Field(min_length=2)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_constraints.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try adding/removing items - the `+` and `×` buttons are disabled when limits are reached!

### Item Constraints

Apply constraints to individual list items:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class ScoresForm:
    scores: list[Annotated[int, Field(ge=0, le=100)]]
    names: list[Annotated[str, Field(min_length=2, max_length=50)]]

params = analyze_dataclass(ScoresForm)

print(params[0].constraints)  # Field(ge=0, le=100) - for each item
print(params[1].constraints)  # Field(min_length=2, max_length=50) - for each item
```

**HTML Renderer Demo:**

<iframe src="../demos/list_item_constraints.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Each item is validated individually!

### Combined List Constraints

Constrain both list length and item values:
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class TestForm:
    answers: Annotated[
        list[Annotated[int, Field(ge=1, le=5)]],
        Field(min_length=5, max_length=10)
    ]

params = analyze_dataclass(TestForm)

print(params[0].list.constraints)  # Field(min_length=5, max_length=10)
print(params[0].constraints)       # Field(ge=1, le=5)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_combined.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Must have 5-10 items, each between 1-5!

## Combined Constraints

Multiple constraints on a single field:
```python
from dataclasses import dataclass
from pytypeinput import Field, PatternMessage, Annotated, analyze_dataclass

@dataclass
class RegistrationForm:
    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=20,
            pattern=r'^[a-zA-Z0-9_]+$'
        ),
        PatternMessage("Only letters, numbers, and underscores")
    ]
    age: Annotated[int, Field(ge=13, le=120)]

params = analyze_dataclass(RegistrationForm)
```

**HTML Renderer Demo:**

<iframe src="../demos/combined_constraints.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Advanced: Type Composition

You can build reusable constraint combinations:
```python
# Define once
PositiveInt = Annotated[int, Field(ge=0)]
Percentage = Annotated[PositiveInt, Field(le=100)]

# Use everywhere
@dataclass
class Settings:
    volume: Percentage
    brightness: Percentage
    contrast: Percentage
```

See **[Type Composition](composition.md)** for more details.
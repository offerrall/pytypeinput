# Type Composition & Inheritance

pytypeinput supports powerful type composition, allowing you to build complex types from simpler ones while preserving all constraints and metadata.

## Basic Composition

Build reusable type aliases with constraints:
```python
from typing import Annotated, TypeAlias
from pydantic import Field
from pytypeinput import analyze_type

# Base constraint
PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]

# Extend with additional constraint
Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]

# All constraints are preserved
param = analyze_type(Percentage, name="completion")
print(param.constraints.metadata)  # [ge=0, le=100]
```

**HTML Renderer Demo:**
<iframe src="../demos/composition_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Adding UI Metadata

Compose constraints with UI enhancements:
```python
from pytypeinput import Slider, Label

# Add UI to constrained type
PercentageSlider: TypeAlias = Annotated[
    Percentage,
    Slider(),
    Label("Volume")
]

param = analyze_type(PercentageSlider, name="volume")
print(param.constraints.metadata)  # [ge=0, le=100]
print(param.ui.is_slider)          # True
print(param.ui.label)              # "Volume"
```

## String Composition

Build validated string types:
```python
# Base constraints
RequiredString: TypeAlias = Annotated[str, Field(min_length=1)]
ShortString: TypeAlias = Annotated[str, Field(max_length=50)]

# Combine both
ShortRequiredString: TypeAlias = Annotated[RequiredString, Field(max_length=50)]

# Or with pattern
Username: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
]

# Add UI metadata
LabeledUsername: TypeAlias = Annotated[
    Username,
    Label("Username"),
    Description("3-20 chars, alphanumeric + underscore")
]
```

## Special Type Inheritance

Extend special types with additional constraints:
```python
from pytypeinput import Email, Color

# Email with length limit
ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
ShortEmail: TypeAlias = Annotated[Email, Field(max_length=100)]

# Email with domain restriction (double inheritance!)
WorkEmail: TypeAlias = Annotated[
    ValidEmail,
    Field(pattern=r'.*@company\.com$')
]

# Color with exact format
HexColor: TypeAlias = Annotated[
    Color,
    Field(min_length=7, max_length=7)
]
```

**All constraints are merged:**
```python
param = analyze_type(WorkEmail, name="work_email")
print(param.widget_type)  # "Email"
# Has both Email pattern AND max_length=254 AND company domain pattern
```

## Multi-Level Composition

Nest as many levels as needed:
```python
Level1: TypeAlias = Annotated[int, Field(ge=0)]
Level2: TypeAlias = Annotated[Level1, Field(le=100)]
Level3: TypeAlias = Annotated[Level2, Slider()]
Level4: TypeAlias = Annotated[Level3, Label("Brightness")]

# All 4 levels are merged correctly!
param = analyze_type(Level4)
# Has: ge=0, le=100, is_slider=True, label="Brightness"
```

## Real-World Domain Types

Build a type library for your domain:
```python
from pytypeinput import analyze_dataclass

# Domain types
Age: TypeAlias = Annotated[PositiveInt, Field(le=120), Label("Age")]
Bio: TypeAlias = Annotated[
    LongString,
    Label("Biography"),
    Description("Tell us about yourself")
]
ValidatedEmail: TypeAlias = Annotated[
    Email,
    Field(min_length=5, max_length=100),
    Label("Email Address")
]

# Use in forms
@dataclass
class UserProfile:
    username: LabeledUsername
    email: ValidatedEmail
    age: Age
    bio: Bio | None = None

# All constraints and UI metadata work!
params = analyze_dataclass(UserProfile)
```

## Benefits

✅ **DRY:** Define constraints once, reuse everywhere  
✅ **Type-safe:** Full IDE support and type checking  
✅ **Composable:** Build complex types from simple ones  
✅ **Flexible:** Add UI metadata without changing base types  
✅ **Maintainable:** Change base type, all uses update
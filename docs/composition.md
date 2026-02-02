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

---

## How Constraint Merging Works

When combining multiple `Field()` constraints:

### Different Constraint Types → Merged

```python
Base: TypeAlias = Annotated[str, Field(max_length=100)]
Enhanced: TypeAlias = Annotated[Base, Field(min_length=5)]

# Result: min_length=5 AND max_length=100 ✅
```

### Same Constraint Type → Last Wins

```python
Loose: TypeAlias = Annotated[str, Field(max_length=100)]
Strict: TypeAlias = Annotated[Loose, Field(max_length=50)]

# Result: max_length=50 (100 is discarded)
```

**Recognized constraints:** `pattern`, `min_length`, `max_length`, `ge`, `le`, `gt`, `lt`

---

## String Composition

```python
# Base types
RequiredString: TypeAlias = Annotated[str, Field(min_length=1)]
ShortString: TypeAlias = Annotated[str, Field(max_length=50)]

# Combine
ShortRequiredString: TypeAlias = Annotated[RequiredString, Field(max_length=50)]
# Result: min_length=1 AND max_length=50 ✅

# Override
VeryShortString: TypeAlias = Annotated[ShortString, Field(max_length=20)]
# Result: max_length=20 (last wins)

# Pattern + constraints
Username: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
]
```

---

## Adding UI Metadata

```python
from pytypeinput import Slider, Label, Description

# Add UI to constrained type
PercentageSlider: TypeAlias = Annotated[
    Percentage,  # Has ge=0, le=100
    Slider(),
    Label("Volume")
]

# UI metadata is always accumulated
Base: TypeAlias = Annotated[int, Label("Value")]
Enhanced: TypeAlias = Annotated[Base, Description("Enter a value")]
# Has BOTH label and description ✅
```

---

## Special Type Inheritance

Extend special types with additional constraints:

```python
from pytypeinput import Email

# ✅ Email with length constraints
ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
StrictEmail: TypeAlias = Annotated[Email, Field(min_length=5, max_length=100)]

param = analyze_type(ValidEmail, name="email")
print(param.widget_type)  # "Email" ✅
# Has: Email pattern + max_length=254
```

---

## ⚠️ Pattern Override Warning

When you override a `pattern`, the widget type is determined by the **last** pattern:

```python
from pytypeinput import Email

ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
WorkEmail: TypeAlias = Annotated[ValidEmail, Field(pattern=r'.*@company\.com$')]

param = analyze_type(WorkEmail, name="work_email")
print(param.widget_type)  # None ⚠️ (not "Email"!)
# Pattern: '.*@company\.com$' (replaces Email pattern)
# max_length: 254 (preserved)
```

**Why:** The "last wins" rule applies to all constraints. The custom pattern replaces the Email pattern and isn't recognized as a special type.

**Solution:**
```python
# ✅ Create a combined pattern
CompanyEmailPattern = r'^[a-zA-Z0-9._%+-]+@company\.com$'
WorkEmail: TypeAlias = Annotated[
    str,
    Field(pattern=CompanyEmailPattern, max_length=254)
]

# ✅ Or use two-layer validation
email: Email  # UI widget
# Validate domain separately in business logic
```

---

## Multi-Level Composition

```python
Level1: TypeAlias = Annotated[int, Field(ge=0)]
Level2: TypeAlias = Annotated[Level1, Field(le=100)]
Level3: TypeAlias = Annotated[Level2, Slider()]
Level4: TypeAlias = Annotated[Level3, Label("Brightness")]

# Result: ge=0, le=100, is_slider=True, label="Brightness" ✅
```

**With overrides:**
```python
Base: TypeAlias = Annotated[int, Field(ge=0, le=100)]
Strict: TypeAlias = Annotated[Base, Field(ge=10)]  # Override ge

# Result: ge=10 (not 0!), le=100 ✅
```

---

## Real-World Example

```python
from typing import Annotated, TypeAlias
from dataclasses import dataclass
from pydantic import Field
from pytypeinput import Email, analyze_dataclass, Label, Description, Slider

# Build your type library
PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]
PercentageSlider: TypeAlias = Annotated[Percentage, Slider()]

Username: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
    Label("Username")
]

ValidEmail: TypeAlias = Annotated[
    Email,
    Field(max_length=254),
    Description("We'll never share your email")
]

# Use in your application
@dataclass
class RegistrationForm:
    username: Username
    email: ValidEmail
    age: Annotated[PositiveInt, Field(le=120), Label("Age")]
    volume: PercentageSlider = 50

params = analyze_dataclass(RegistrationForm)
```

---

## Best Practices

**DO:**

- Build reusable constraint libraries
- Override constraints for stricter validation
- Layer constraints from general to specific

**WHEN OVERRIDING PATTERNS:**

- You'll lose the original widget type
- Consider combining patterns manually instead
- Or use two-layer validation (UI + business logic)

**DON'T:**

- Expect multiple patterns to coexist (last wins)
- Create contradictory constraints (e.g., `ge=100, le=50`)

---
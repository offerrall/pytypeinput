# UI Metadata

pytypeinput provides UI customization options through metadata classes like `Label`, `Description`, `Placeholder`, `Slider`, and more.

## Label

Override the auto-generated label:
```python
from dataclasses import dataclass
from pytypeinput import Label, Annotated, analyze_dataclass

@dataclass
class UserForm:
    first_name: Annotated[str, Label("Full Name")]
    email_address: Annotated[str, Label("Work Email")]

params = analyze_dataclass(UserForm)

print(params[0].ui.label)  # "Full Name"
print(params[1].ui.label)  # "Work Email"
```

**HTML Renderer Demo:**

<iframe src="../demos/label.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Without `Label`, field names would be "First Name" and "Email Address" (auto-generated from `first_name` and `email_address`).

## Description

Add help text below the input:
```python
from dataclasses import dataclass
from pytypeinput import Description, Annotated, analyze_dataclass

@dataclass
class SettingsForm:
    api_key: Annotated[
        str,
        Description("Your API key from the developer dashboard")
    ]
    timeout: Annotated[
        int,
        Description("Request timeout in seconds (default: 30)")
    ]

params = analyze_dataclass(SettingsForm)

print(params[0].ui.description)  # "Your API key from..."
print(params[1].ui.description)  # "Request timeout in..."
```

**HTML Renderer Demo:**

<iframe src="../demos/description.html" 
        width="100%" 
        height="280" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Placeholder

Add placeholder text for inputs:
```python
from dataclasses import dataclass
from pytypeinput import Placeholder, Annotated, analyze_dataclass

@dataclass
class SearchForm:
    query: Annotated[str, Placeholder("Search products...")]
    max_price: Annotated[int, Placeholder("Max price")]

params = analyze_dataclass(SearchForm)

print(params[0].ui.placeholder)  # "Search products..."
print(params[1].ui.placeholder)  # "Max price"
```

**HTML Renderer Demo:**

<iframe src="../demos/placeholder.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## PatternMessage

Custom error message for pattern validation:
```python
from dataclasses import dataclass
from pytypeinput import Field, PatternMessage, Annotated, analyze_dataclass

@dataclass
class AccountForm:
    username: Annotated[
        str,
        Field(pattern=r'^[a-zA-Z0-9_]+$'),
        PatternMessage("Only letters, numbers, and underscores are allowed")
    ]

params = analyze_dataclass(AccountForm)

print(params[0].ui.pattern_message)  # "Only letters, numbers..."
```

**HTML Renderer Demo:**

<iframe src="../demos/pattern_message.html" 
        width="100%" 
        height="180" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try entering `test@123` to see the custom error message!

## Rows

Multi-line text input (textarea):
```python
from dataclasses import dataclass
from pytypeinput import Rows, Annotated, analyze_dataclass

@dataclass
class FeedbackForm:
    comments: Annotated[str, Rows(5)]
    bio: Annotated[str, Rows(3)]

params = analyze_dataclass(FeedbackForm)

print(params[0].ui.rows)  # 5
print(params[1].ui.rows)  # 3
```

**HTML Renderer Demo:**

<iframe src="../demos/rows.html" 
        width="100%" 
        height="350" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Step

Increment step for number inputs:
```python
from dataclasses import dataclass
from pytypeinput import Step, Annotated, analyze_dataclass

@dataclass
class ProductForm:
    quantity: Annotated[int, Step(5)]
    price: Annotated[float, Step(0.25)]

params = analyze_dataclass(ProductForm)

print(params[0].ui.step)  # 5
print(params[1].ui.step)  # 0.25
```

**HTML Renderer Demo:**

<iframe src="../demos/step.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Use the arrow buttons or keyboard to see the step increment!

## Slider

Render number inputs as sliders:
```python
from dataclasses import dataclass
from pytypeinput import Field, Slider, Annotated, analyze_dataclass

@dataclass
class SettingsForm:
    volume: Annotated[int, Field(ge=0, le=100), Slider()]
    brightness: Annotated[float, Field(ge=0.0, le=1.0), Slider(show_value=True)]

params = analyze_dataclass(SettingsForm)

print(params[0].ui.is_slider)        # True
print(params[1].ui.show_slider_value) # True
```

**HTML Renderer Demo:**

<iframe src="../demos/slider.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

**Note:** Sliders require `Field(ge=..., le=...)` constraints!

## IsPassword

Render string input as password field:
```python
from dataclasses import dataclass
from pytypeinput import IsPassword, Annotated, analyze_dataclass

@dataclass
class LoginForm:
    username: str
    password: Annotated[str, IsPassword]

params = analyze_dataclass(LoginForm)

print(params[1].ui.is_password)  # True
```

**HTML Renderer Demo:**

<iframe src="../demos/password.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Combined UI Metadata

Use multiple metadata classes together:
```python
from dataclasses import dataclass
from pytypeinput import Field, Label, Description, Placeholder, PatternMessage, Annotated, analyze_dataclass

@dataclass
class RegistrationForm:
    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        Label("Username"),
        Description("Choose a unique username for your account"),
        Placeholder("Enter username"),
        PatternMessage("Only letters, numbers, and underscores allowed")
    ]
    bio: Annotated[
        str,
        Label("Biography"),
        Description("Tell us about yourself (optional)"),
        Placeholder("Write a short bio..."),
        Rows(4)
    ] | None = None

params = analyze_dataclass(RegistrationForm)
```

**HTML Renderer Demo:**

<iframe src="../demos/combined_ui.html" 
        width="100%" 
        height="450" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
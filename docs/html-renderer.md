# HTML Renderer

The HTML renderer generates complete, interactive forms from parameter metadata with built-in validation and styling.

## Basic Usage

Render a complete form from a dataclass:
```python
from dataclasses import dataclass
from pytypeinput import Field, Email, Annotated, analyze_dataclass
from pytypeinput.html import HTMLRenderer

@dataclass
class ContactForm:
    name: str
    email: Email
    age: Annotated[int, Field(ge=18, le=120)]

params = analyze_dataclass(ContactForm)
renderer = HTMLRenderer()

# Render individual fields
html_fields = '\n'.join(renderer.render_param(p) for p in params)

# Get complete HTML with styles and validation
complete_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {renderer.get_styles()}
</head>
<body>
    {html_fields}
    {renderer.get_validation_script()}
</body>
</html>
"""
```

**HTML Renderer Demo:**

<iframe src="../demos/renderer_basic.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Render Individual Parameters

Render parameters one at a time:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass
from pytypeinput.html import HTMLRenderer

@dataclass
class UserForm:
    username: str
    age: int

params = analyze_dataclass(UserForm)
renderer = HTMLRenderer()

# Render each parameter separately
for param in params:
    html = renderer.render_param(param)
    print(f"Field '{param.name}':")
    print(html)
```

**HTML Renderer Demo:**

<iframe src="../demos/renderer_individual.html" 
        width="100%" 
        height="220" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Complete Example

Full working example with all features:
```python
from dataclasses import dataclass
from pytypeinput import (
    Field, Email, Annotated, Label, Description, 
    Placeholder, PatternMessage, analyze_dataclass
)
from pytypeinput.html import HTMLRenderer

@dataclass
class RegistrationForm:
    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        Label("Username"),
        Description("Choose a unique username"),
        Placeholder("Enter username"),
        PatternMessage("Only letters, numbers, and underscores")
    ]
    email: Annotated[
        Email,
        Label("Email Address"),
        Placeholder("you@example.com")
    ]
    age: Annotated[
        int,
        Field(ge=18, le=120),
        Label("Age"),
        Description("You must be 18 or older")
    ]
    newsletter: Annotated[
        bool,
        Label("Subscribe to Newsletter"),
        Description("Receive updates and promotions")
    ] = True

params = analyze_dataclass(RegistrationForm)
renderer = HTMLRenderer()

fields_html = '\n'.join(renderer.render_param(p) for p in params)

html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registration Form</title>
    {renderer.get_styles()}
</head>
<body style="padding: 20px; max-width: 600px; margin: 0 auto;">
    <h1>Create Account</h1>
    {fields_html}
    {renderer.get_validation_script()}
</body>
</html>"""

# Save to file
with open('registration.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

**HTML Renderer Demo:**

<iframe src="../demos/renderer_complete.html" 
        width="100%" 
        height="500" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Advanced Options

The renderer supports additional customization options not shown in the demos above:
```python
# Custom CSS styles
renderer = HTMLRenderer(custom_styles="your-custom-css")

# Disable client-side validation
renderer = HTMLRenderer(enable_validation=False)

# List available CSS variables for theming
variables = HTMLRenderer.list_css_variables()
# ['--pytypeinput-border-radius', '--pytypeinput-input-bg', ...]

# Get default styles for modification
default_styles = HTMLRenderer.get_default_styles()
```
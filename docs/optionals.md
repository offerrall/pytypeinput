# Optionals

pytypeinput supports optional fields with toggle switches. Optional fields can be enabled or disabled by default.

## Basic Optional

Optional field with default disabled:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class UserForm:
    username: str
    bio: str | None = None

params = analyze_dataclass(UserForm)

print(params[1].name)      # "bio"
print(params[1].optional)  # OptionalMetadata(enabled=False)
```

**HTML Renderer Demo:**

<iframe src="../demos/optional_basic.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Toggle the switch to enable/disable the field!

## Optional with Default Value

Optional field enabled by default (has a value):
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class SettingsForm:
    theme: str | None = "dark"
    language: str | None = "en"

params = analyze_dataclass(SettingsForm)

print(params[0].optional)  # OptionalMetadata(enabled=True)
print(params[0].default)   # "dark"
print(params[1].optional)  # OptionalMetadata(enabled=True)
print(params[1].default)   # "en"
```

**HTML Renderer Demo:**

<iframe src="../demos/optional_default.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Fields are enabled by default because they have values.

## Explicitly Enabled Optional

Force optional field to be enabled even without a default:
```python
from dataclasses import dataclass
from pytypeinput import Annotated, OptionalEnabled, analyze_dataclass

@dataclass
class ProfileForm:
    name: str
    nickname: str | OptionalEnabled = None

params = analyze_dataclass(ProfileForm)

print(params[1].optional)  # OptionalMetadata(enabled=True)
print(params[1].default)   # None
```

**HTML Renderer Demo:**

<iframe src="../demos/optional_enabled.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Field is enabled by default even though it has no value.

## Explicitly Disabled Optional

Force optional field to be disabled even with a default value:
```python
from dataclasses import dataclass
from pytypeinput import Annotated, OptionalDisabled, analyze_dataclass

@dataclass
class ConfigForm:
    api_key: str
    debug_mode: str | OptionalDisabled = "false"

params = analyze_dataclass(ConfigForm)

print(params[1].optional)  # OptionalMetadata(enabled=False)
print(params[1].default)   # "false"
```

**HTML Renderer Demo:**

<iframe src="../demos/optional_disabled.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Field is disabled by default even though it has a value.

## Optional with All Types

Any type can be optional:
```python
from dataclasses import dataclass
from datetime import date
from pytypeinput import Email, analyze_dataclass

@dataclass
class ContactForm:
    email: Email
    phone: str | None = None
    age: int | None = None
    birthday: date | None = None
    verified: bool | None = None

params = analyze_dataclass(ContactForm)

print(params[1].optional)  # OptionalMetadata(enabled=False)
print(params[2].optional)  # OptionalMetadata(enabled=False)
print(params[3].optional)  # OptionalMetadata(enabled=False)
print(params[4].optional)  # OptionalMetadata(enabled=False)
```

**HTML Renderer Demo:**

<iframe src="../demos/optional_types.html" 
        width="100%" 
        height="400" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
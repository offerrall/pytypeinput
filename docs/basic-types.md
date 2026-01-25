# Basic Types

pytypeinput supports all basic Python types: `str`, `int`, `float`, `bool`, `date`, `time`.

## String

Basic string input:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class UserForm:
    username: str

params = analyze_dataclass(UserForm)

print(params[0].name)        # "username"
print(params[0].param_type)  # <class 'str'>
```

**HTML Renderer Demo:**

<iframe src="../demos/str_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Integer

Basic integer input:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class UserForm:
    age: int

params = analyze_dataclass(UserForm)

print(params[0].name)        # "age"
print(params[0].param_type)  # <class 'int'>
```

**HTML Renderer Demo:**

<iframe src="../demos/int_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Float

Basic float input:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class ProductForm:
    price: float

params = analyze_dataclass(ProductForm)

print(params[0].name)        # "price"
print(params[0].param_type)  # <class 'float'>
```

**HTML Renderer Demo:**

<iframe src="../demos/float_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Boolean

Boolean toggle switch:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class PreferencesForm:
    newsletter: bool

params = analyze_dataclass(PreferencesForm)

print(params[0].name)        # "newsletter"
print(params[0].param_type)  # <class 'bool'>
```

**HTML Renderer Demo:**

<iframe src="../demos/bool_basic.html" 
        width="100%" 
        height="120" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Date

Date picker input:
```python
from dataclasses import dataclass
from datetime import date
from pytypeinput import analyze_dataclass

@dataclass
class UserForm:
    birthday: date

params = analyze_dataclass(UserForm)

print(params[0].name)        # "birthday"
print(params[0].param_type)  # <class 'datetime.date'>
```

**HTML Renderer Demo:**

<iframe src="../demos/date_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Time

Time picker input:
```python
from dataclasses import dataclass
from datetime import time
from pytypeinput import analyze_dataclass

@dataclass
class MeetingForm:
    meeting_time: time

params = analyze_dataclass(MeetingForm)

print(params[0].name)        # "meeting_time"
print(params[0].param_type)  # <class 'datetime.time'>
```

**HTML Renderer Demo:**

<iframe src="../demos/time_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Default Values

All basic types support default values:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class SettingsForm:
    theme: str = "dark"
    volume: int = 50
    notifications: bool = True

params = analyze_dataclass(SettingsForm)

print(params[0].default)  # "dark"
print(params[1].default)  # 50
print(params[2].default)  # True
```

**HTML Renderer Demo:**

<iframe src="../demos/defaults.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
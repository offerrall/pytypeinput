# Lists

pytypeinput supports dynamic lists with add/remove functionality and validation at both list and item levels.

## String List

Basic list of strings:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class TagsForm:
    tags: list[str]

params = analyze_dataclass(TagsForm)

print(params[0].name)        # "tags"
print(params[0].param_type)  # <class 'str'>
print(params[0].list)        # ListMetadata(constraints=None)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_str.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Click `+` to add items, `×` to remove them.

## Integer List

List of integers:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class ScoresForm:
    scores: list[int]

params = analyze_dataclass(ScoresForm)

print(params[0].name)        # "scores"
print(params[0].param_type)  # <class 'int'>
print(params[0].list)        # ListMetadata(constraints=None)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_int.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Float List

List of floats:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class MeasurementsForm:
    measurements: list[float]

params = analyze_dataclass(MeasurementsForm)

print(params[0].name)        # "measurements"
print(params[0].param_type)  # <class 'float'>
```

**HTML Renderer Demo:**

<iframe src="../demos/list_float.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Boolean List

List of booleans:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class PermissionsForm:
    permissions: list[bool]

params = analyze_dataclass(PermissionsForm)

print(params[0].name)        # "permissions"
print(params[0].param_type)  # <class 'bool'>
```

**HTML Renderer Demo:**

<iframe src="../demos/list_bool.html" 
        width="100%" 
        height="250" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Date List

List of dates:
```python
from dataclasses import dataclass
from datetime import date
from pytypeinput import analyze_dataclass

@dataclass
class EventsForm:
    event_dates: list[date]

params = analyze_dataclass(EventsForm)

print(params[0].name)        # "event_dates"
print(params[0].param_type)  # <class 'datetime.date'>
```

**HTML Renderer Demo:**

<iframe src="../demos/list_date.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>


## Time List

List of times:
```python
from dataclasses import dataclass
from datetime import time
from pytypeinput import analyze_dataclass

@dataclass
class ScheduleForm:
    meeting_times: list[time]

params = analyze_dataclass(ScheduleForm)

print(params[0].name)        # "meeting_times"
print(params[0].param_type)  # <class 'datetime.time'>
```

**HTML Renderer Demo:**

<iframe src="../demos/list_time.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Email List

List of emails:
```python
from dataclasses import dataclass
from pytypeinput import Email, analyze_dataclass

@dataclass
class InviteForm:
    recipients: list[Email]

params = analyze_dataclass(InviteForm)

print(params[0].name)         # "recipients"
print(params[0].widget_type)  # "Email"
print(params[0].list)         # ListMetadata(constraints=None)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_email.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## File List

List of file uploads:
```python
from dataclasses import dataclass
from pytypeinput import ImageFile, analyze_dataclass

@dataclass
class GalleryForm:
    photos: list[ImageFile]

params = analyze_dataclass(GalleryForm)

print(params[0].name)         # "photos"
print(params[0].widget_type)  # "ImageFile"
print(params[0].list)         # ListMetadata(constraints=None)
```

**HTML Renderer Demo:**

<iframe src="../demos/list_image.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Select multiple files at once or use `+` to add more.

## Lists of Choices

All choice types work with lists:
```python
from dataclasses import dataclass
from typing import Literal
from enum import Enum
from pytypeinput import Annotated, Dropdown, analyze_dataclass

class Tag(Enum):
    BUG = "Bug"
    FEATURE = "Feature"
    DOCS = "Documentation"

def get_colors():
    return ["Red", "Blue", "Green", "Yellow"]

@dataclass
class ProjectForm:
    categories: list[Literal["Frontend", "Backend", "DevOps"]]
    tags: list[Tag]
    colors: list[Annotated[str, Dropdown(get_colors)]]

params = analyze_dataclass(ProjectForm)

print(params[0].list)  # ListMetadata(constraints=None)
print(params[1].list)  # ListMetadata(constraints=None)
print(params[2].list)  # ListMetadata(constraints=None)
```

**HTML Renderer Demo:**

<iframe src="../demos/choices_lists.html" 
        width="100%" 
        height="400" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Default Values

Lists support default values:
```python
from dataclasses import dataclass
from pytypeinput import analyze_dataclass

@dataclass
class PreferencesForm:
    favorite_colors: list[str] = ["red", "green", "blue"]
    lucky_numbers: list[int] = [7, 11, 42]

params = analyze_dataclass(PreferencesForm)

print(params[0].default)  # ['red', 'green', 'blue']
print(params[1].default)  # [7, 11, 42]
```

**HTML Renderer Demo:**

<iframe src="../demos/list_defaults.html" 
        width="100%" 
        height="300" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
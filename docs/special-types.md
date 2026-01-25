# Special Types

pytypeinput provides specialized input types with built-in validation and custom UI widgets.

## Email

Email input with validation:
```python
from dataclasses import dataclass
from pytypeinput import Email, analyze_dataclass

@dataclass
class ContactForm:
    email: Email

params = analyze_dataclass(ContactForm)

print(params[0].name)         # "email"
print(params[0].widget_type)  # "Email"
```

**HTML Renderer Demo:**

<iframe src="../demos/email_basic.html" 
        width="100%" 
        height="180" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Try entering an invalid email like `test@` or `invalid.com`!

## Color

Color picker input:
```python
from dataclasses import dataclass
from pytypeinput import Color, analyze_dataclass

@dataclass
class ThemeForm:
    primary_color: Color

params = analyze_dataclass(ThemeForm)

print(params[0].name)         # "primary_color"
print(params[0].widget_type)  # "Color"
```

**HTML Renderer Demo:**

<iframe src="../demos/color_basic.html" 
        width="100%" 
        height="150" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## File Upload

Generic file upload:
```python
from dataclasses import dataclass
from pytypeinput import File, analyze_dataclass

@dataclass
class UploadForm:
    document: File

params = analyze_dataclass(UploadForm)

print(params[0].name)         # "document"
print(params[0].widget_type)  # "File"
```

**HTML Renderer Demo:**

<iframe src="../demos/file_basic.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Image File

Image file upload with preview:
```python
from dataclasses import dataclass
from pytypeinput import ImageFile, analyze_dataclass

@dataclass
class ProfileForm:
    avatar: ImageFile

params = analyze_dataclass(ProfileForm)

print(params[0].name)         # "avatar"
print(params[0].widget_type)  # "ImageFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/image_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.svg`, and more.

## Video File

Video file upload:
```python
from dataclasses import dataclass
from pytypeinput import VideoFile, analyze_dataclass

@dataclass
class MediaForm:
    video: VideoFile

params = analyze_dataclass(MediaForm)

print(params[0].name)         # "video"
print(params[0].widget_type)  # "VideoFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/video_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, and more.

## Audio File

Audio file upload:
```python
from dataclasses import dataclass
from pytypeinput import AudioFile, analyze_dataclass

@dataclass
class PodcastForm:
    episode: AudioFile

params = analyze_dataclass(PodcastForm)

print(params[0].name)         # "episode"
print(params[0].widget_type)  # "AudioFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/audio_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`.

## Data File

Data file upload (CSV, Excel, JSON, etc.):
```python
from dataclasses import dataclass
from pytypeinput import DataFile, analyze_dataclass

@dataclass
class ImportForm:
    spreadsheet: DataFile

params = analyze_dataclass(ImportForm)

print(params[0].name)         # "spreadsheet"
print(params[0].widget_type)  # "DataFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/data_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.csv`, `.xlsx`, `.xls`, `.json`, `.xml`, `.yaml`, `.yml`.

## Text File

Text file upload:
```python
from dataclasses import dataclass
from pytypeinput import TextFile, analyze_dataclass

@dataclass
class EditorForm:
    notes: TextFile

params = analyze_dataclass(EditorForm)

print(params[0].name)         # "notes"
print(params[0].widget_type)  # "TextFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/text_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.txt`, `.md`, `.log`, `.rtf`.

## Document File

Document file upload (PDF, Word, Excel, PowerPoint):
```python
from dataclasses import dataclass
from pytypeinput import DocumentFile, analyze_dataclass

@dataclass
class SubmissionForm:
    resume: DocumentFile

params = analyze_dataclass(SubmissionForm)

print(params[0].name)         # "resume"
print(params[0].widget_type)  # "DocumentFile"
```

**HTML Renderer Demo:**

<iframe src="../demos/document_file.html" 
        width="100%" 
        height="200" 
        frameborder="0"
        style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

Accepts: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, and more.
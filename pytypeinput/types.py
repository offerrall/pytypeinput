from typing import Annotated
from pydantic import Field
import re


# ===== PATTERN HELPERS =====

def _file_pattern(*extensions):
    exts = [e.lstrip('.').lower() for e in extensions]
    return r'(?i)^.+\.(' + '|'.join(exts) + r')$'


# ===== PATTERNS =====

COLOR_PATTERN = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

IMAGE_FILE_PATTERN = _file_pattern('png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff', 'svg', 'ico', 'heic', 'avif', 'raw', 'psd')
VIDEO_FILE_PATTERN = _file_pattern('mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg')
AUDIO_FILE_PATTERN = _file_pattern('mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a')
DATA_FILE_PATTERN = _file_pattern('csv', 'xlsx', 'xls', 'json', 'xml', 'yaml', 'yml')
TEXT_FILE_PATTERN = _file_pattern('txt', 'md', 'log', 'rtf')
DOCUMENT_FILE_PATTERN = _file_pattern('pdf', 'doc', 'docx', 'odt', 'ppt', 'pptx', 'odp', 'xls', 'xlsx', 'ods')
ANY_FILE_PATTERN = r'^.+$'


# ===== SPECIAL_TYPES (only Color + File types) =====

SPECIAL_TYPES = {
    COLOR_PATTERN: 'Color',
    IMAGE_FILE_PATTERN: 'File',
    VIDEO_FILE_PATTERN: 'File',
    AUDIO_FILE_PATTERN: 'File',
    DATA_FILE_PATTERN: 'File',
    TEXT_FILE_PATTERN: 'File',
    DOCUMENT_FILE_PATTERN: 'File',
    ANY_FILE_PATTERN: 'File',
}


# ===== UI METADATA =====

class Step:
    def __init__(self, value: int | float = 1):
        self.value = value

class Placeholder:
    def __init__(self, text: str):
        self.text = text

class PatternMessage:
    def __init__(self, message: str):
        self.message = message

class Description:
    def __init__(self, text: str):
        self.text = text

class Label:
    def __init__(self, text: str):
        self.text = text

class Rows:
    def __init__(self, count: int):
        self.count = count

class Slider:
    def __init__(self, show_value: bool = True):
        self.show_value = show_value

class Dropdown:
    def __init__(self, options_function):
        self.options_function = options_function

class IsPassword:
    pass


# ===== OPTIONAL MARKERS =====

class _OptionalEnabledMarker:
    pass

class _OptionalDisabledMarker:
    pass

OptionalEnabled = Annotated[None, _OptionalEnabledMarker()]
OptionalDisabled = Annotated[None, _OptionalDisabledMarker()]


# ===== TYPE ALIASES =====

Color = Annotated[str, Field(pattern=COLOR_PATTERN)]
Email = Annotated[str, Field(pattern=EMAIL_PATTERN), PatternMessage("Must be a valid email address (e.g., name@example.com)"), Placeholder("name@example.com")]
ImageFile = Annotated[str, Field(pattern=IMAGE_FILE_PATTERN)]
VideoFile = Annotated[str, Field(pattern=VIDEO_FILE_PATTERN)]
AudioFile = Annotated[str, Field(pattern=AUDIO_FILE_PATTERN)]
DataFile = Annotated[str, Field(pattern=DATA_FILE_PATTERN)]
TextFile = Annotated[str, Field(pattern=TEXT_FILE_PATTERN)]
DocumentFile = Annotated[str, Field(pattern=DOCUMENT_FILE_PATTERN)]
File = Annotated[str, Field(pattern=ANY_FILE_PATTERN)]
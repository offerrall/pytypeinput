from typing import Annotated
from pydantic import Field
import re


# ===== PATTERN HELPERS =====

def _file_pattern(*extensions):
    exts = [e.lstrip('.').lower() for e in extensions]
    return r'(?i)^.+\.(' + '|'.join(exts) + r')$'


def _pattern_to_accept(pattern: str) -> str:
    match = re.search(r'\\\.\(([^)]+)\)', pattern)
    if not match:
        return '*'
    extensions = match.group(1).split('|')
    return ','.join(f'.{ext}' for ext in extensions)


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


# ===== WIDGET TYPE NAMES =====

WIDGET_TYPE_COLOR = 'Color'
WIDGET_TYPE_EMAIL = 'Email'
WIDGET_TYPE_IMAGE_FILE = 'ImageFile'
WIDGET_TYPE_VIDEO_FILE = 'VideoFile'
WIDGET_TYPE_AUDIO_FILE = 'AudioFile'
WIDGET_TYPE_DATA_FILE = 'DataFile'
WIDGET_TYPE_TEXT_FILE = 'TextFile'
WIDGET_TYPE_DOCUMENT_FILE = 'DocumentFile'
WIDGET_TYPE_FILE = 'File'

FILE_WIDGET_TYPES = {
    WIDGET_TYPE_IMAGE_FILE, WIDGET_TYPE_VIDEO_FILE, WIDGET_TYPE_AUDIO_FILE,
    WIDGET_TYPE_DATA_FILE, WIDGET_TYPE_TEXT_FILE, WIDGET_TYPE_DOCUMENT_FILE,
    WIDGET_TYPE_FILE
}


# ===== MAPPINGS =====

FILE_ACCEPT_EXTENSIONS = {
    WIDGET_TYPE_IMAGE_FILE: _pattern_to_accept(IMAGE_FILE_PATTERN),
    WIDGET_TYPE_VIDEO_FILE: _pattern_to_accept(VIDEO_FILE_PATTERN),
    WIDGET_TYPE_AUDIO_FILE: _pattern_to_accept(AUDIO_FILE_PATTERN),
    WIDGET_TYPE_DATA_FILE: _pattern_to_accept(DATA_FILE_PATTERN),
    WIDGET_TYPE_TEXT_FILE: _pattern_to_accept(TEXT_FILE_PATTERN),
    WIDGET_TYPE_DOCUMENT_FILE: _pattern_to_accept(DOCUMENT_FILE_PATTERN),
    WIDGET_TYPE_FILE: '*'
}

SPECIAL_TYPES = {
    COLOR_PATTERN: WIDGET_TYPE_COLOR,
    EMAIL_PATTERN: WIDGET_TYPE_EMAIL,
    IMAGE_FILE_PATTERN: WIDGET_TYPE_IMAGE_FILE,
    VIDEO_FILE_PATTERN: WIDGET_TYPE_VIDEO_FILE,
    AUDIO_FILE_PATTERN: WIDGET_TYPE_AUDIO_FILE,
    DATA_FILE_PATTERN: WIDGET_TYPE_DATA_FILE,
    TEXT_FILE_PATTERN: WIDGET_TYPE_TEXT_FILE,
    DOCUMENT_FILE_PATTERN: WIDGET_TYPE_DOCUMENT_FILE,
    ANY_FILE_PATTERN: WIDGET_TYPE_FILE,
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
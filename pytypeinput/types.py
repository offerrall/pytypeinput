from typing import Annotated
from pydantic import Field
import re


# ===== PATTERN HELPERS =====

def _file_pattern(*extensions):
    """Generate a case-insensitive regex pattern for file extensions."""
    exts = [e.lstrip('.').lower() for e in extensions]
    return r'(?i)^.+\.(' + '|'.join(exts) + r')$'


def _pattern_to_accept(pattern: str) -> str:
    """Convert regex pattern to HTML accept attribute format.
    
    Extracts extensions from pattern and converts to comma-separated list.
    
    Args:
        pattern: Regex pattern with extensions.
    
    Returns:
        Comma-separated extensions with dots (e.g., '.png,.jpg').
    """
    # Extract the group AFTER \. (the literal dot in the regex)
    match = re.search(r'\\\.\(([^)]+)\)', pattern)
    if not match:
        return '*'
    
    # Split by | and add dots
    extensions = match.group(1).split('|')
    return ','.join(f'.{ext}' for ext in extensions)


# ===== STRING PATTERNS =====

COLOR_PATTERN = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# ===== FILE PATTERNS =====

IMAGE_FILE_PATTERN = _file_pattern(
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff', 'svg', 
    'ico', 'heic', 'avif', 'raw', 'psd',
)

VIDEO_FILE_PATTERN = _file_pattern(
    'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', 'mpg'
)

AUDIO_FILE_PATTERN = _file_pattern(
    'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a'
)

DATA_FILE_PATTERN = _file_pattern(
    'csv', 'xlsx', 'xls', 'json', 'xml', 'yaml', 'yml'
)

TEXT_FILE_PATTERN = _file_pattern(
    'txt', 'md', 'log', 'rtf'
)

DOCUMENT_FILE_PATTERN = _file_pattern(
    'pdf', 'doc', 'docx', 'odt', 'ppt', 'pptx', 'odp', 'xls', 'xlsx', 'ods'
)

ANY_FILE_PATTERN = r'^.+$'

FILE_TYPE_PATTERNS = [
    IMAGE_FILE_PATTERN,
    VIDEO_FILE_PATTERN,
    AUDIO_FILE_PATTERN,
    DATA_FILE_PATTERN,
    TEXT_FILE_PATTERN,
    DOCUMENT_FILE_PATTERN,
    ANY_FILE_PATTERN
]


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
    WIDGET_TYPE_IMAGE_FILE,
    WIDGET_TYPE_VIDEO_FILE,
    WIDGET_TYPE_AUDIO_FILE,
    WIDGET_TYPE_DATA_FILE,
    WIDGET_TYPE_TEXT_FILE,
    WIDGET_TYPE_DOCUMENT_FILE,
    WIDGET_TYPE_FILE
}


# ===== FILE ACCEPT EXTENSIONS =====

FILE_ACCEPT_EXTENSIONS = {
    WIDGET_TYPE_IMAGE_FILE: _pattern_to_accept(IMAGE_FILE_PATTERN),
    WIDGET_TYPE_VIDEO_FILE: _pattern_to_accept(VIDEO_FILE_PATTERN),
    WIDGET_TYPE_AUDIO_FILE: _pattern_to_accept(AUDIO_FILE_PATTERN),
    WIDGET_TYPE_DATA_FILE: _pattern_to_accept(DATA_FILE_PATTERN),
    WIDGET_TYPE_TEXT_FILE: _pattern_to_accept(TEXT_FILE_PATTERN),
    WIDGET_TYPE_DOCUMENT_FILE: _pattern_to_accept(DOCUMENT_FILE_PATTERN),
    WIDGET_TYPE_FILE: '*'
}


# ===== PATTERN TO WIDGET TYPE MAPPING =====

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


# ===== UI METADATA CLASSES =====

class Step:
    """Step increment for number inputs."""
    
    def __init__(self, value: int | float = 1):
        if not isinstance(value, (int, float)):
            raise TypeError(f"Step value must be int or float, got {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"Step must be positive, got {value}")
        self.value = value


class Placeholder:
    """Placeholder text for input fields."""
    
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Placeholder text must be str, got {type(text).__name__}")
        self.text = text


class PatternMessage:
    """Custom error message for pattern validation."""
    
    def __init__(self, message: str):
        if not isinstance(message, str):
            raise TypeError(f"PatternMessage message must be str, got {type(message).__name__}")
        self.message = message


class Description:
    """Help text displayed below the input field."""
    
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Description text must be str, got {type(text).__name__}")
        self.text = text


class Label:
    """Custom label text (overrides auto-generated label from parameter name)."""
    
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise TypeError(f"Label text must be str, got {type(text).__name__}")
        self.text = text


class Rows:
    """Number of visible text rows for textarea (multi-line text input)."""
    
    def __init__(self, count: int):
        if not isinstance(count, int):
            raise TypeError(f"Rows count must be int, got {type(count).__name__}")
        if count <= 0:
            raise ValueError(f"Rows count must be positive, got {count}")
        self.count = count


class Slider:
    """Render number input as slider widget.
    
    Requires the parameter to have min/max constraints via Field(ge=..., le=...).
    Only compatible with int and float types.
    """
    
    def __init__(self, show_value: bool = True):
        """Initialize slider widget.
        
        Args:
            show_value: Whether to display the current value next to the slider.
        """
        if not isinstance(show_value, bool):
            raise TypeError(f"show_value must be bool, got {type(show_value).__name__}")
        self.show_value = show_value


class Dropdown:
    """Dropdown selector with dynamic options from a function."""
    
    def __init__(self, options_function):
        if not callable(options_function):
            raise TypeError("options_function must be callable")
        self.options_function = options_function


class IsPassword:
    """Marker to render string input as password field."""
    pass


# ===== OPTIONAL MARKERS =====

class _OptionalEnabledMarker:
    """Internal marker for explicitly enabled optional fields."""
    pass


class _OptionalDisabledMarker:
    """Internal marker for explicitly disabled optional fields."""
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
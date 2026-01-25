from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Literal
from pytypeinput import (
    Field, Annotated, Label, Description, PatternMessage,
    Email, Color, File, ImageFile, VideoFile, AudioFile, 
    DataFile, TextFile, DocumentFile,
    OptionalEnabled, OptionalDisabled,
    Dropdown,
    Step, Rows, Slider, IsPassword, Placeholder
)
from demo_generator import create_dataclass_demo, DEMOS_DIR


# ===== ENUMS =====

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Rating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class Status(Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"

class Tag(Enum):
    BUG = "Bug"
    FEATURE = "Feature"
    DOCS = "Documentation"


# ===== DROPDOWN FUNCTIONS =====

def get_countries():
    return ["USA", "Canada", "Mexico", "UK", "Germany", "France"]

def get_years():
    return [2020, 2021, 2022, 2023, 2024, 2025]

def get_colors():
    return ["Red", "Blue", "Green", "Yellow"]

def get_themes():
    return ["Light", "Dark", "Auto"]


# ===== INDEX DEMO =====

@dataclass
class User:
    name: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        Label("Username"),
        Description("Choose a unique username (letters, numbers, underscore only)"),
        PatternMessage("Username can only contain letters, numbers, and underscores.")
    ]
    age: Annotated[int, Field(ge=18, le=120)]
    bio: str | None = None


# ===== BASIC TYPES DEMOS =====

@dataclass
class StrBasic:
    username: str

@dataclass
class IntBasic:
    age: int

@dataclass
class FloatBasic:
    price: float

@dataclass
class BoolBasic:
    newsletter: bool

@dataclass
class DateBasic:
    birthday: date

@dataclass
class TimeBasic:
    meeting_time: time

@dataclass
class Defaults:
    theme: str = "dark"
    volume: int = 50
    notifications: bool = True


# ===== SPECIAL TYPES DEMOS =====

@dataclass
class EmailBasic:
    email: Email

@dataclass
class ColorBasic:
    primary_color: Color

@dataclass
class FileBasic:
    document: File

@dataclass
class ImageFileDemo:
    avatar: ImageFile

@dataclass
class VideoFileDemo:
    video: VideoFile

@dataclass
class AudioFileDemo:
    episode: AudioFile

@dataclass
class DataFileDemo:
    spreadsheet: DataFile

@dataclass
class TextFileDemo:
    notes: TextFile

@dataclass
class DocumentFileDemo:
    resume: DocumentFile


# ===== LISTS DEMOS =====

@dataclass
class ListStr:
    tags: list[str]

@dataclass
class ListInt:
    scores: list[int]

@dataclass
class ListFloat:
    measurements: list[float]

@dataclass
class ListBool:
    permissions: list[bool]

@dataclass
class ListDate:
    event_dates: list[date]

@dataclass
class ListTime:
    meeting_times: list[time]

@dataclass
class ListEmail:
    recipients: list[Email]

@dataclass
class ListImage:
    photos: list[ImageFile]

@dataclass
class ListDefaults:
    favorite_colors: list[str] = field(default_factory=lambda: ["red", "green", "blue"])
    lucky_numbers: list[int] = field(default_factory=lambda: [7, 11, 42])


# ===== OPTIONALS DEMOS =====

@dataclass
class OptionalBasic:
    username: str
    bio: str | None = None

@dataclass
class OptionalDefault:
    theme: str | None = "dark"
    language: str | None = "en"

@dataclass
class OptionalEnabledDemo:
    name: str
    nickname: str | OptionalEnabled = None

@dataclass
class OptionalDisabledDemo:
    api_key: str
    debug_mode: str | OptionalDisabled = "false"

@dataclass
class OptionalTypes:
    email: Email
    phone: str | None = None
    age: int | None = None
    birthday: date | None = None
    verified: bool | None = None


# ===== CHOICES DEMOS =====

@dataclass
class LiteralBasic:
    size: Literal["Small", "Medium", "Large"]

@dataclass
class LiteralNumbers:
    stars: Literal[1, 2, 3, 4, 5]
    score: Literal[0.0, 2.5, 5.0, 7.5, 10.0] # type: ignore

@dataclass
class EnumBasic:
    priority: Priority

@dataclass
class EnumInt:
    rating: Rating

@dataclass
class DropdownBasic:
    country: Annotated[str, Dropdown(get_countries)]

@dataclass
class DropdownInt:
    year: Annotated[int, Dropdown(get_years)]

@dataclass
class ChoicesLists:
    categories: list[Literal["Frontend", "Backend", "DevOps"]]
    tags: list[Tag]
    colors: list[Annotated[str, Dropdown(get_colors)]]

@dataclass
class ChoicesDefaults:
    visibility: Literal["Public", "Private"] = "Public"
    status: Status = Status.DRAFT
    theme: Annotated[str, Dropdown(get_themes)] = "Auto"


# ===== CONSTRAINTS DEMOS =====

@dataclass
class StrConstraints:
    username: Annotated[str, Field(min_length=3, max_length=20)]
    bio: Annotated[str, Field(max_length=500)]

@dataclass
class StrPattern:
    username: Annotated[
        str,
        Field(pattern=r'^[a-zA-Z0-9_]+$'),
        PatternMessage("Only letters, numbers, and underscores allowed")
    ]

@dataclass
class IntConstraints:
    age: Annotated[int, Field(ge=18, le=120)]
    rating: Annotated[int, Field(ge=1, le=5)]

@dataclass
class IntStrict:
    percentage: Annotated[int, Field(gt=0, lt=100)]

@dataclass
class FloatConstraints:
    price: Annotated[float, Field(ge=0.0, le=9999.99)]
    rating: Annotated[float, Field(ge=0.0, le=5.0)]

@dataclass
class FloatStrict:
    temperature: Annotated[float, Field(gt=-273.15)]

@dataclass
class ListConstraints:
    tags: Annotated[list[str], Field(min_length=1, max_length=5)]
    categories: Annotated[list[str], Field(min_length=2)]

@dataclass
class ListItemConstraints:
    scores: list[Annotated[int, Field(ge=0, le=100)]]
    names: list[Annotated[str, Field(min_length=2, max_length=50)]]

@dataclass
class ListCombined:
    answers: Annotated[
        list[Annotated[int, Field(ge=1, le=5)]],
        Field(min_length=5, max_length=10)
    ]

@dataclass
class CombinedConstraints:
    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        PatternMessage("Only letters, numbers, and underscores")
    ]
    age: Annotated[int, Field(ge=13, le=120)]

# ===== UI METADATA DEMOS =====

@dataclass
class LabelDemo:
    first_name: Annotated[str, Label("Full Name")]
    email_address: Annotated[str, Label("Work Email")]

@dataclass
class DescriptionDemo:
    api_key: Annotated[str, Description("Your API key from the developer dashboard")]
    timeout: Annotated[int, Description("Request timeout in seconds (default: 30)")]

@dataclass
class PlaceholderDemo:
    query: Annotated[str, Placeholder("Search products...")]
    max_price: Annotated[int, Placeholder("Max price")]

@dataclass
class PatternMessageDemo:
    username: Annotated[
        str,
        Field(pattern=r'^[a-zA-Z0-9_]+$'),
        PatternMessage("Only letters, numbers, and underscores are allowed")
    ]

@dataclass
class RowsDemo:
    comments: Annotated[str, Rows(5)]
    bio: Annotated[str, Rows(3)]

@dataclass
class StepDemo:
    quantity: Annotated[int, Step(5)]
    price: Annotated[float, Step(0.25)]

@dataclass
class SliderDemo:
    volume: Annotated[int, Field(ge=0, le=100), Slider()]
    brightness: Annotated[float, Field(ge=0.0, le=1.0), Slider(show_value=True)]

@dataclass
class PasswordDemo:
    username: str
    password: Annotated[str, IsPassword]

@dataclass
class CombinedUI:
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

# ===== HTML RENDERER DEMOS =====

@dataclass
class RendererBasic:
    name: str
    email: Email
    age: Annotated[int, Field(ge=18, le=120)]

@dataclass
class RendererIndividual:
    username: str
    age: int

@dataclass
class RendererComplete:
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

if __name__ == "__main__":
    print("Generating demos...")

    create_dataclass_demo(User, "user_form.html")

    create_dataclass_demo(StrBasic, "str_basic.html")
    create_dataclass_demo(IntBasic, "int_basic.html")
    create_dataclass_demo(FloatBasic, "float_basic.html")
    create_dataclass_demo(BoolBasic, "bool_basic.html")
    create_dataclass_demo(DateBasic, "date_basic.html")
    create_dataclass_demo(TimeBasic, "time_basic.html")
    create_dataclass_demo(Defaults, "defaults.html")

    create_dataclass_demo(EmailBasic, "email_basic.html")
    create_dataclass_demo(ColorBasic, "color_basic.html")
    create_dataclass_demo(FileBasic, "file_basic.html")
    create_dataclass_demo(ImageFileDemo, "image_file.html")
    create_dataclass_demo(VideoFileDemo, "video_file.html")
    create_dataclass_demo(AudioFileDemo, "audio_file.html")
    create_dataclass_demo(DataFileDemo, "data_file.html")
    create_dataclass_demo(TextFileDemo, "text_file.html")
    create_dataclass_demo(DocumentFileDemo, "document_file.html")

    create_dataclass_demo(ListStr, "list_str.html")
    create_dataclass_demo(ListInt, "list_int.html")
    create_dataclass_demo(ListFloat, "list_float.html")
    create_dataclass_demo(ListBool, "list_bool.html")
    create_dataclass_demo(ListDate, "list_date.html")
    create_dataclass_demo(ListTime, "list_time.html")
    create_dataclass_demo(ListEmail, "list_email.html")
    create_dataclass_demo(ListImage, "list_image.html")
    create_dataclass_demo(ListDefaults, "list_defaults.html")

    create_dataclass_demo(OptionalBasic, "optional_basic.html")
    create_dataclass_demo(OptionalDefault, "optional_default.html")
    create_dataclass_demo(OptionalEnabledDemo, "optional_enabled.html")
    create_dataclass_demo(OptionalDisabledDemo, "optional_disabled.html")
    create_dataclass_demo(OptionalTypes, "optional_types.html")

    create_dataclass_demo(LiteralBasic, "literal_basic.html")
    create_dataclass_demo(LiteralNumbers, "literal_numbers.html")
    create_dataclass_demo(EnumBasic, "enum_basic.html")
    create_dataclass_demo(EnumInt, "enum_int.html")
    create_dataclass_demo(DropdownBasic, "dropdown_basic.html")
    create_dataclass_demo(DropdownInt, "dropdown_int.html")
    create_dataclass_demo(ChoicesLists, "choices_lists.html")
    create_dataclass_demo(ChoicesDefaults, "choices_defaults.html")

    create_dataclass_demo(StrConstraints, "str_constraints.html")
    create_dataclass_demo(StrPattern, "str_pattern.html")
    create_dataclass_demo(IntConstraints, "int_constraints.html")
    create_dataclass_demo(IntStrict, "int_strict.html")
    create_dataclass_demo(FloatConstraints, "float_constraints.html")
    create_dataclass_demo(FloatStrict, "float_strict.html")
    create_dataclass_demo(ListConstraints, "list_constraints.html")
    create_dataclass_demo(ListItemConstraints, "list_item_constraints.html")
    create_dataclass_demo(ListCombined, "list_combined.html")
    create_dataclass_demo(CombinedConstraints, "combined_constraints.html")

    create_dataclass_demo(LabelDemo, "label.html")
    create_dataclass_demo(DescriptionDemo, "description.html")
    create_dataclass_demo(PlaceholderDemo, "placeholder.html")
    create_dataclass_demo(PatternMessageDemo, "pattern_message.html")
    create_dataclass_demo(RowsDemo, "rows.html")
    create_dataclass_demo(StepDemo, "step.html")
    create_dataclass_demo(SliderDemo, "slider.html")
    create_dataclass_demo(PasswordDemo, "password.html")
    create_dataclass_demo(CombinedUI, "combined_ui.html")

    create_dataclass_demo(RendererBasic, "renderer_basic.html")
    create_dataclass_demo(RendererIndividual, "renderer_individual.html")
    create_dataclass_demo(RendererComplete, "renderer_complete.html")

    print(f"✅ Done! Demos saved to {DEMOS_DIR}")
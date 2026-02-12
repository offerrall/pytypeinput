import inspect
import pytest
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time
from pydantic import Field

from pytypeinput.analyzer import analyze_type
from pytypeinput.param import (
    ParamMetadata, OptionalMetadata, ParamUIMetadata,
    ListMetadata, ItemUIMetadata, ChoiceMetadata,
)
from pytypeinput.types import (
    Label, Description, Step, Placeholder, PatternMessage, Rows,
    Slider, IsPassword, Dropdown, OptionalEnabled, OptionalDisabled,
    Color, Email, ImageFile, VideoFile, AudioFile, DataFile, TextFile, DocumentFile, File,
    _file_pattern, _pattern_to_accept,
    COLOR_PATTERN, EMAIL_PATTERN,
    IMAGE_FILE_PATTERN, VIDEO_FILE_PATTERN, AUDIO_FILE_PATTERN,
    DATA_FILE_PATTERN, TEXT_FILE_PATTERN, DOCUMENT_FILE_PATTERN, ANY_FILE_PATTERN,
    SPECIAL_TYPES, FILE_ACCEPT_EXTENSIONS, FILE_WIDGET_TYPES,
    WIDGET_TYPE_COLOR, WIDGET_TYPE_EMAIL,
    WIDGET_TYPE_IMAGE_FILE, WIDGET_TYPE_VIDEO_FILE, WIDGET_TYPE_AUDIO_FILE,
    WIDGET_TYPE_DATA_FILE, WIDGET_TYPE_TEXT_FILE, WIDGET_TYPE_DOCUMENT_FILE,
    WIDGET_TYPE_FILE,
    _OptionalEnabledMarker, _OptionalDisabledMarker,
)

EMPTY = inspect.Parameter.empty


class ColEnum(Enum):
    R = "red"; G = "green"


class EmptyEnum(Enum):
    pass


class MixEnum(Enum):
    A = 1; B = "x"


def _opts():
    return ["a", "b"]


def _bad():
    raise RuntimeError("boom")


VALID = [
    (int, "f", EMPTY),
    (str, "f", EMPTY),
    (float, "f", EMPTY),
    (bool, "f", EMPTY),
    (date, "f", EMPTY),
    (time, "f", EMPTY),

    (str | None, "f", EMPTY),
    (str | None, "f", None),
    (str | None, "f", ""),
    (str | None, "f", "hi"),
    (int | None, "f", 0),
    (bool | None, "f", False),
    (float | None, "f", 3.14),
    (date | None, "f", EMPTY),
    (time | None, "f", EMPTY),
    (str | OptionalEnabled, "f", EMPTY),
    (str | OptionalEnabled, "f", None),
    (str | OptionalDisabled, "f", "hi"),

    (Annotated[int, Label("L")], "f", EMPTY),
    (Annotated[str, Description("D")], "f", EMPTY),
    (Annotated[float, Label("L"), Description("D")], "f", EMPTY),
    (list[Annotated[int, Label("L")]], "f", EMPTY),
    (Annotated[list[Annotated[int, Label("In")]], Label("Out")], "f", EMPTY),

    (list[int], "f", EMPTY),
    (list[str], "f", EMPTY),
    (list[float], "f", EMPTY),
    (list[bool], "f", EMPTY),
    (list[date], "f", EMPTY),
    (list[time], "f", EMPTY),
    (Annotated[list[int], Field(min_length=1)], "f", EMPTY),
    (Annotated[list[str], Field(max_length=10)], "f", EMPTY),
    (Annotated[list[float], Field(min_length=2, max_length=5)], "f", EMPTY),

    (Annotated[int, Step(5)], "f", EMPTY),
    (Annotated[float, Step(0.1)], "f", EMPTY),
    (Annotated[str, Placeholder("...")], "f", EMPTY),
    (Annotated[str, Field(pattern=r"^\d+$"), PatternMessage("N")], "f", EMPTY),
    (Annotated[str, Rows(5)], "f", EMPTY),
    (Annotated[int, Slider(), Field(ge=0, le=100)], "f", EMPTY),
    (Annotated[int, Slider(show_value=False), Field(ge=0, le=100)], "f", EMPTY),
    (Annotated[str, IsPassword()], "f", EMPTY),
    (Annotated[float, Step(0.5), Slider(), Placeholder("0"), Field(ge=0.0, le=1.0)], "f", EMPTY),
    (list[Annotated[int, Step(2), Slider(), Field(ge=0, le=10)]], "f", EMPTY),

    (ColEnum, "f", EMPTY),
    (ColEnum, "f", ColEnum.R),
    (ColEnum | None, "f", EMPTY),
    (ColEnum | None, "f", ColEnum.G),
    (Annotated[ColEnum, Label("C")], "f", EMPTY),

    (Literal["a", "b"], "f", EMPTY),
    (Literal[1, 2, 3], "f", EMPTY),
    (Literal["x", "y"], "f", "x"),
    (Literal["a", "b"] | None, "f", EMPTY),
    (Annotated[Literal["x", "y"], Label("L")], "f", EMPTY),

    (Annotated[str, Dropdown(_opts)], "f", EMPTY),

    (Annotated[int, Field(ge=0, le=100)], "f", EMPTY),
    (Annotated[float, Field(gt=0, lt=1)], "f", EMPTY),
    (Annotated[str, Field(min_length=1, max_length=50)], "f", EMPTY),
    (Annotated[str, Field(pattern=r"^\d{3}$")], "f", EMPTY),
    (Annotated[int, Field(ge=0), Field(le=100)], "f", EMPTY),
    (Annotated[int, Field(ge=0, le=100)], "f", 50),
    (Annotated[str, Field(min_length=1)], "f", "ok"),

    (int, "f", 42),
    (str, "f", "hi"),
    (float, "f", 3.14),
    (bool, "f", True),
    (date, "f", date(2024, 1, 1)),
    (time, "f", time(12, 0)),
    (int, "f", None),

    (Color, "f", EMPTY),
    (Email, "f", EMPTY),
    (ImageFile, "f", EMPTY),
    (VideoFile, "f", EMPTY),
    (AudioFile, "f", EMPTY),
    (DataFile, "f", EMPTY),
    (TextFile, "f", EMPTY),
    (DocumentFile, "f", EMPTY),
    (File, "f", EMPTY),
    (Color | None, "f", EMPTY),
    (list[Color], "f", EMPTY),
    (Annotated[Color, Label("C")], "f", EMPTY),
    (Annotated[Email, Label("E"), Description("D")], "f", EMPTY),

    (Annotated[str, Label("N"), Description("D")] | None, "f", "J"),
    (Annotated[int, Field(ge=0, le=100)] | None, "f", 50),
    (Annotated[list[Annotated[int, Step(5), Slider(), Field(ge=0, le=100)]], Field(min_length=1, max_length=10)], "f", EMPTY),
    (Annotated[str, Label("C"), Placeholder("..."), Dropdown(_opts)], "f", EMPTY),
    (Annotated[int, Label("V"), Description("D"), Field(ge=0, le=100), Step(5), Slider()] | None, "v", 50),
    (Annotated[str, IsPassword(), Placeholder("pw")], "f", EMPTY),
    (Annotated[str, Rows(10), Placeholder("bio")], "f", EMPTY),
]


ERRORS = [
    (dict, "f", EMPTY),
    (tuple, "f", EMPTY),
    (set, "f", EMPTY),
    (bytes, "f", EMPTY),
    (complex, "f", EMPTY),
    (None, "f", EMPTY),
    (type(None), "f", EMPTY),

    (int, 123, EMPTY),

    (str | int, "f", EMPTY),
    (int | str | None, "f", EMPTY),

    (list, "f", EMPTY),
    (list[dict], "f", EMPTY),
    (list[list[int]], "f", EMPTY),
    (list[str | int], "f", EMPTY),
    (list[str | None], "f", EMPTY),
    (Annotated[list[int], Field(ge=0)], "f", EMPTY),

    (EmptyEnum, "f", EMPTY),
    (MixEnum, "f", EMPTY),
    (ColEnum, "f", "yellow"),

    (Literal[1, "x"], "f", EMPTY),
    (Literal["x", "y"], "f", "z"),

    (Annotated[str, Dropdown("bad")], "f", EMPTY),
    (Annotated[str, Dropdown(lambda: [])], "f", EMPTY),
    (Annotated[str, Dropdown(lambda: [1, "x"])], "f", EMPTY),
    (Annotated[str, Dropdown(_bad)], "f", EMPTY),
    (Annotated[str, Dropdown(lambda: "nope")], "f", EMPTY),

    (Annotated[int, Field(ge=10)], "f", 5),
    (Annotated[int, Field(le=10)], "f", 20),
    (Annotated[str, Field(min_length=5)], "f", "hi"),

    (int, "f", "no"),
    (str, "f", 123),
    (float, "f", "3"),
    (bool, "f", 1),
    (int, "f", True),

    (Annotated[int, "a"], "f", EMPTY),
    (Annotated[int | None, "a"], "f", EMPTY),

    # Slider without any bounds
    (Annotated[int, Slider()], "f", EMPTY),
    # Slider with only lower bound
    (Annotated[int, Slider(), Field(ge=0)], "f", EMPTY),
    # Slider with only upper bound
    (Annotated[int, Slider(), Field(le=100)], "f", EMPTY),
    # Slider with show_value but no bounds
    (Annotated[int, Slider(show_value=False)], "f", EMPTY),
    # Slider in list without bounds
    (list[Annotated[int, Slider()]], "f", EMPTY),
]


@pytest.mark.parametrize("annotation, name, default", VALID)
def test_valid(annotation, name, default):
    result = analyze_type(annotation, name, default)
    assert isinstance(result, ParamMetadata)


@pytest.mark.parametrize("annotation, name, default", ERRORS)
def test_error(annotation, name, default):
    with pytest.raises((TypeError, ValueError)):
        analyze_type(annotation, name, default)


def test_error_wraps_name_in_brackets():
    with pytest.raises(TypeError, match=r"\[my_field\]"):
        analyze_type(dict, "my_field")


def test_error_wraps_name_on_bad_default():
    with pytest.raises(TypeError, match=r"\[age\]"):
        analyze_type(int, "age", "not_int")


def test_error_wraps_name_on_bad_choices():
    with pytest.raises(ValueError, match=r"\[color\]"):
        analyze_type(Literal["x", "y"], "color", "z")


def test_param_metadata_defaults():
    p = ParamMetadata(name="x", param_type=int)
    assert p.name == "x"
    assert p.param_type is int
    assert p.default is None
    assert p.constraints is None
    assert p.widget_type is None
    assert p.optional is None
    assert p.list is None
    assert p.choices is None
    assert p.item_ui is None
    assert p.param_ui is None


def test_param_metadata_frozen():
    p = ParamMetadata(name="x", param_type=int)
    with pytest.raises(AttributeError):
        p.name = "y"


def test_optional_metadata_defaults():
    assert OptionalMetadata().enabled is False


def test_optional_metadata_frozen():
    o = OptionalMetadata(enabled=True)
    with pytest.raises(AttributeError):
        o.enabled = False


def test_list_metadata_defaults():
    meta = ListMetadata()
    assert meta.min_length is None
    assert meta.max_length is None


def test_list_metadata_frozen():
    with pytest.raises(AttributeError):
        ListMetadata().constraints = "x"


def test_choice_metadata_defaults():
    c = ChoiceMetadata(options=("a", "b"))
    assert c.enum_class is None
    assert c.options_function is None
    assert c.options == ("a", "b")


def test_choice_metadata_frozen():
    with pytest.raises(AttributeError):
        ChoiceMetadata(options=("a",)).options = ("b",)


def test_item_ui_metadata_defaults():
    i = ItemUIMetadata()
    assert i.step == None
    assert i.is_password is False
    assert i.is_slider is False
    assert i.show_slider_value is True
    assert i.placeholder is None
    assert i.pattern_message is None
    assert i.rows is None


def test_item_ui_metadata_frozen():
    with pytest.raises(AttributeError):
        ItemUIMetadata().step = 5


def test_param_ui_metadata_defaults():
    p = ParamUIMetadata()
    assert p.label is None
    assert p.description is None


def test_param_ui_metadata_frozen():
    with pytest.raises(AttributeError):
        ParamUIMetadata().label = "x"


def test_file_pattern_basic():
    p = _file_pattern("png", "jpg")
    assert "png" in p and "jpg" in p


def test_file_pattern_strips_dots():
    p = _file_pattern(".png", ".JPG")
    assert "png" in p and "jpg" in p


def test_file_pattern_case_insensitive():
    assert _file_pattern("png").startswith("(?i)")


def test_file_pattern_single_ext():
    p = _file_pattern("txt")
    assert "txt" in p


def test_pattern_to_accept_image():
    r = _pattern_to_accept(IMAGE_FILE_PATTERN)
    assert ".png" in r and ".jpg" in r


def test_pattern_to_accept_video():
    r = _pattern_to_accept(VIDEO_FILE_PATTERN)
    assert ".mp4" in r


def test_pattern_to_accept_audio():
    r = _pattern_to_accept(AUDIO_FILE_PATTERN)
    assert ".mp3" in r


def test_pattern_to_accept_data():
    r = _pattern_to_accept(DATA_FILE_PATTERN)
    assert ".csv" in r


def test_pattern_to_accept_text():
    r = _pattern_to_accept(TEXT_FILE_PATTERN)
    assert ".txt" in r


def test_pattern_to_accept_document():
    r = _pattern_to_accept(DOCUMENT_FILE_PATTERN)
    assert ".pdf" in r


def test_pattern_to_accept_any():
    assert _pattern_to_accept(ANY_FILE_PATTERN) == "*"


def test_pattern_to_accept_no_match():
    assert _pattern_to_accept("no_ext_here") == "*"


def test_pattern_to_accept_color():
    assert _pattern_to_accept(COLOR_PATTERN) == "*"


EXPECTED_SPECIAL = [
    (COLOR_PATTERN, WIDGET_TYPE_COLOR),
    (EMAIL_PATTERN, WIDGET_TYPE_EMAIL),
    (IMAGE_FILE_PATTERN, WIDGET_TYPE_IMAGE_FILE),
    (VIDEO_FILE_PATTERN, WIDGET_TYPE_VIDEO_FILE),
    (AUDIO_FILE_PATTERN, WIDGET_TYPE_AUDIO_FILE),
    (DATA_FILE_PATTERN, WIDGET_TYPE_DATA_FILE),
    (TEXT_FILE_PATTERN, WIDGET_TYPE_TEXT_FILE),
    (DOCUMENT_FILE_PATTERN, WIDGET_TYPE_DOCUMENT_FILE),
    (ANY_FILE_PATTERN, WIDGET_TYPE_FILE),
]


@pytest.mark.parametrize("pattern, widget", EXPECTED_SPECIAL)
def test_special_types_mapping(pattern, widget):
    assert SPECIAL_TYPES[pattern] == widget


def test_special_types_count():
    assert len(SPECIAL_TYPES) == 9


def test_file_widget_types_contains_all_files():
    expected = {
        WIDGET_TYPE_IMAGE_FILE, WIDGET_TYPE_VIDEO_FILE, WIDGET_TYPE_AUDIO_FILE,
        WIDGET_TYPE_DATA_FILE, WIDGET_TYPE_TEXT_FILE, WIDGET_TYPE_DOCUMENT_FILE,
        WIDGET_TYPE_FILE,
    }
    assert FILE_WIDGET_TYPES == expected


def test_file_widget_types_excludes_non_files():
    assert WIDGET_TYPE_COLOR not in FILE_WIDGET_TYPES
    assert WIDGET_TYPE_EMAIL not in FILE_WIDGET_TYPES


def test_file_accept_extensions_keys():
    assert set(FILE_ACCEPT_EXTENSIONS.keys()) == FILE_WIDGET_TYPES


def test_file_accept_any():
    assert FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_FILE] == "*"


def test_file_accept_image_has_png():
    assert ".png" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_IMAGE_FILE]


def test_file_accept_video_has_mp4():
    assert ".mp4" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_VIDEO_FILE]


def test_file_accept_audio_has_mp3():
    assert ".mp3" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_AUDIO_FILE]


def test_file_accept_data_has_csv():
    assert ".csv" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_DATA_FILE]


def test_file_accept_text_has_txt():
    assert ".txt" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_TEXT_FILE]


def test_file_accept_document_has_pdf():
    assert ".pdf" in FILE_ACCEPT_EXTENSIONS[WIDGET_TYPE_DOCUMENT_FILE]


def test_widget_type_values():
    assert WIDGET_TYPE_COLOR == "Color"
    assert WIDGET_TYPE_EMAIL == "Email"
    assert WIDGET_TYPE_IMAGE_FILE == "ImageFile"
    assert WIDGET_TYPE_VIDEO_FILE == "VideoFile"
    assert WIDGET_TYPE_AUDIO_FILE == "AudioFile"
    assert WIDGET_TYPE_DATA_FILE == "DataFile"
    assert WIDGET_TYPE_TEXT_FILE == "TextFile"
    assert WIDGET_TYPE_DOCUMENT_FILE == "DocumentFile"
    assert WIDGET_TYPE_FILE == "File"


def test_step():
    assert Step(5).value == 5
    assert Step(0.1).value == 0.1
    assert Step().value == 1


def test_placeholder():
    assert Placeholder("hi").text == "hi"


def test_pattern_message():
    assert PatternMessage("err").message == "err"


def test_description_class():
    assert Description("d").text == "d"


def test_label_class():
    assert Label("l").text == "l"


def test_rows():
    assert Rows(3).count == 3


def test_slider():
    assert Slider().show_value is True
    assert Slider(show_value=False).show_value is False


def test_dropdown_stores_function():
    assert Dropdown(_opts).options_function is _opts


def test_is_password():
    assert isinstance(IsPassword(), IsPassword)


def test_optional_enabled_marker_instantiates():
    assert isinstance(_OptionalEnabledMarker(), _OptionalEnabledMarker)


def test_optional_disabled_marker_instantiates():
    assert isinstance(_OptionalDisabledMarker(), _OptionalDisabledMarker)


def test_optional_enabled_is_annotated_none():
    from typing import get_origin, get_args
    assert get_origin(OptionalEnabled) is Annotated
    base, *meta = get_args(OptionalEnabled)
    assert base is type(None)
    assert any(isinstance(m, _OptionalEnabledMarker) for m in meta)


def test_optional_disabled_is_annotated_none():
    from typing import get_origin, get_args
    assert get_origin(OptionalDisabled) is Annotated
    base, *meta = get_args(OptionalDisabled)
    assert base is type(None)
    assert any(isinstance(m, _OptionalDisabledMarker) for m in meta)


TYPE_ALIASES = [Color, Email, ImageFile, VideoFile, AudioFile, DataFile, TextFile, DocumentFile, File]


@pytest.mark.parametrize("alias", TYPE_ALIASES)
def test_type_alias_base_is_str(alias):
    from typing import get_origin, get_args
    assert get_origin(alias) is Annotated
    assert get_args(alias)[0] is str


def test_bare_list_error_message():
    with pytest.raises(TypeError, match="Empty list type"):
        analyze_type(list, "f")


def test_bare_list_error_not_unsupported():
    with pytest.raises(TypeError) as exc_info:
        analyze_type(list, "f")
    assert "Unsupported type" not in str(exc_info.value)


import re


def test_color_pattern_valid():
    assert re.match(COLOR_PATTERN, "#fff")
    assert re.match(COLOR_PATTERN, "#FF00AA")


def test_color_pattern_invalid():
    assert not re.match(COLOR_PATTERN, "red")
    assert not re.match(COLOR_PATTERN, "#gggggg")


def test_email_pattern_valid():
    assert re.match(EMAIL_PATTERN, "a@b.co")
    assert re.match(EMAIL_PATTERN, "user.name+tag@example.com")


def test_email_pattern_invalid():
    assert not re.match(EMAIL_PATTERN, "notanemail")
    assert not re.match(EMAIL_PATTERN, "@no.com")


def test_image_pattern_valid():
    assert re.match(IMAGE_FILE_PATTERN, "photo.png")
    assert re.match(IMAGE_FILE_PATTERN, "IMG.JPG")


def test_image_pattern_invalid():
    assert not re.match(IMAGE_FILE_PATTERN, "file.mp4")


def test_any_file_pattern():
    assert re.match(ANY_FILE_PATTERN, "anything.xyz")
    assert re.match(ANY_FILE_PATTERN, "no_extension")
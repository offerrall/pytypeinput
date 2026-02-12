import inspect
import pytest
from typing import Annotated, Literal, get_origin, get_args
from datetime import date, time
from enum import Enum
from pydantic import Field

from pytypeinput.extractors.validate_type_01 import validate_type
from pytypeinput.extractors.validate_optional_02 import extract_optional
from pytypeinput.extractors.extract_param_ui_03 import extract_param_ui
from pytypeinput.param import ParamUIMetadata
from pytypeinput.types import (
    Label, Description, Slider, Step, Placeholder, PatternMessage,
    IsPassword, Rows, Dropdown,
    Color, Email, ImageFile, File,
)

EMPTY = inspect.Parameter.empty


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


def get_colors():
    return ["red", "blue", "green"]


RETURNS_NONE = [
    str, int, float, bool, date, time,
    list[str], list[int],
    Color, Email, ImageFile, File,
    Priority, Literal["a", "b"],
    str | None, list[str] | None,
    Annotated[str, Field(min_length=3)],
    Annotated[int, Field(ge=0), Slider()],
    Annotated[str, Placeholder("...")],
    Annotated[str, IsPassword()],
    Annotated[str, Rows(5)],
    Annotated[float, Step(0.5)],
    Annotated[str, Dropdown(get_colors)],
    Annotated[str, Field(pattern=r'^\d+$'), PatternMessage("err")],
    list[Annotated[int, Slider()]],
]


LABEL_ONLY = [
    (Annotated[str, Label("Name")],                                         "Name"),
    (Annotated[str, Field(min_length=3), Label("Name")],                    "Name"),
    (Annotated[int, Field(ge=0), Slider(), Label("Age")],                   "Age"),
    (Annotated[str, Placeholder("..."), Label("Name")],                     "Name"),
    (Annotated[list[str], Label("Tags")],                                   "Tags"),
    (Annotated[list[str], Field(min_length=1), Label("Tags")],              "Tags"),
]


DESCRIPTION_ONLY = [
    (Annotated[str, Description("Help")],                                   "Help"),
    (Annotated[str, Field(min_length=3), Description("Help")],              "Help"),
    (Annotated[list[int], Description("Add numbers")],                      "Add numbers"),
]


LABEL_AND_DESCRIPTION = [
    (Annotated[str, Label("Name"), Description("Enter name")],                                 "Name",   "Enter name"),
    (Annotated[str, Field(min_length=3), Label("Name"), Description("Help")],                  "Name",   "Help"),
    (Annotated[int, Field(ge=0), Slider(), Label("Vol"), Description("Volume")],               "Vol",    "Volume"),
    (Annotated[list[int], Field(min_length=1), Label("Scores"), Description("Add")],           "Scores", "Add"),
]


LAST_WINS = [
    (Annotated[str, Label("A"), Label("B")],                                            "B",    None),
    (Annotated[str, Description("A"), Description("B")],                                None,   "B"),
    (Annotated[str, Label("A"), Description("A"), Label("B"), Description("B")],        "B",    "B"),
]


_Base_label = Annotated[int, Label("Base")]
_Base_desc = Annotated[str, Description("Old")]
_Base_both = Annotated[int, Label("Old"), Description("Old")]
_Base_label_desc = Annotated[int, Label("Old"), Description("Keep")]
_Base_keep_label = Annotated[int, Label("Keep"), Description("Old")]
_Base_field_label = Annotated[int, Field(ge=0), Label("Base")]
_Base_desc_only = Annotated[str, Description("Base")]
_L1 = Annotated[int, Label("L1")]
_L2 = Annotated[_L1, Label("L2")]
_L3 = Annotated[_L2, Label("L3")]
_D1 = Annotated[str, Description("D1")]
_D2 = Annotated[_D1, Description("D2")]
_D3 = Annotated[_D2, Description("D3")]
_M1 = Annotated[int, Label("L1"), Description("D1")]
_M2 = Annotated[_M1, Label("L2")]
_M3 = Annotated[_M2, Description("D3")]
_Slider_base = Annotated[int, Field(ge=0)]
_Slider_with = Annotated[_Slider_base, Slider()]
_Slider_labeled = Annotated[_Slider_with, Label("Value")]

COMPOSITION = [
    (_Base_label,                                                           "Base",     None),
    (Annotated[_Base_label, Label("Override")],                             "Override", None),
    (Annotated[_Base_desc, Description("New")],                             None,       "New"),
    (Annotated[_Base_both, Label("New"), Description("New")],               "New",      "New"),
    (Annotated[_Base_label_desc, Label("New")],                             "New",      "Keep"),
    (Annotated[_Base_keep_label, Description("New")],                       "Keep",     "New"),
    (Annotated[_Base_field_label, Description("Added")],                    "Base",     "Added"),
    (Annotated[_Base_desc_only, Label("Added")],                            "Added",    "Base"),
    (_L3,                                                                   "L3",       None),
    (_D3,                                                                   None,       "D3"),
    (_M3,                                                                   "L2",       "D3"),
    (Annotated[Email, Label("Contact")],                                    "Contact",  None),
    (Annotated[Color, Label("Primary"), Description("Pick")],               "Primary",  "Pick"),
    (_Slider_labeled,                                                       "Value",    None),
]


_Rating = Annotated[int, Label("Rating")]
_Item_desc = Annotated[str, Description("Help")]
_Item_both = Annotated[int, Label("Score"), Description("Rate")]
_Item_field_label = Annotated[int, Field(ge=0), Label("Base")]

LIST_FALLBACK = [
    (list[_Rating],                     "Rating",   None),
    (list[_Item_desc],                  None,       "Help"),
    (list[_Item_both],                  "Score",    "Rate"),
    (list[_Item_field_label],           "Base",     None),
]


LIST_OUTER_WINS = [
    (Annotated[list[_Rating], Label("All Ratings")],                                "All Ratings",  None),
    (Annotated[list[_Item_desc], Description("List help")],                         None,           "List help"),
    (Annotated[list[_Item_both], Label("All"), Description("All items")],           "All",          "All items"),
    (Annotated[list[Annotated[int, Description("Item help")]], Label("Scores")],    "Scores",       None),
    (Annotated[list[_Rating], Description("Add scores")],                           None,           "Add scores"),
]


CLEANED_NO_LABEL_DESC = [
    Annotated[str, Field(min_length=3), Label("X")],
    Annotated[str, Field(min_length=3), Description("X")],
    Annotated[str, Field(min_length=3), Label("X"), Description("Y")],
]

CLEANED_RETURNS_BASE = [
    Annotated[str, Label("X")],
    Annotated[str, Description("X")],
    Annotated[str, Label("X"), Description("Y")],
]


def analyze_param_ui(annotation):
    validate_type(annotation)
    annotation, _ = extract_optional(annotation, EMPTY)
    return extract_param_ui(annotation)


def ui(ann):
    return analyze_param_ui(ann)[1]


@pytest.mark.parametrize("annotation", RETURNS_NONE)
def test_returns_none(annotation):
    assert ui(annotation) is None


@pytest.mark.parametrize("annotation, label", LABEL_ONLY)
def test_label_only(annotation, label):
    assert ui(annotation) == ParamUIMetadata(label=label)


@pytest.mark.parametrize("annotation, description", DESCRIPTION_ONLY)
def test_description_only(annotation, description):
    assert ui(annotation) == ParamUIMetadata(description=description)


@pytest.mark.parametrize("annotation, label, description", LABEL_AND_DESCRIPTION)
def test_label_and_description(annotation, label, description):
    assert ui(annotation) == ParamUIMetadata(label=label, description=description)


@pytest.mark.parametrize("annotation, label, description", LAST_WINS)
def test_last_wins(annotation, label, description):
    assert ui(annotation) == ParamUIMetadata(label=label, description=description)


@pytest.mark.parametrize("annotation, label, description", COMPOSITION)
def test_composition(annotation, label, description):
    assert ui(annotation) == ParamUIMetadata(label=label, description=description)


@pytest.mark.parametrize("annotation, label, description", LIST_FALLBACK)
def test_list_fallback(annotation, label, description):
    assert ui(annotation) == ParamUIMetadata(label=label, description=description)


@pytest.mark.parametrize("annotation, label, description", LIST_OUTER_WINS)
def test_list_outer_wins(annotation, label, description):
    assert ui(annotation) == ParamUIMetadata(label=label, description=description)


@pytest.mark.parametrize("annotation", CLEANED_NO_LABEL_DESC)
def test_label_description_removed(annotation):
    ann, _ = analyze_param_ui(annotation)
    assert not any(isinstance(m, (Label, Description)) for m in get_args(ann)[1:])


@pytest.mark.parametrize("annotation", CLEANED_RETURNS_BASE)
def test_only_label_description_returns_base(annotation):
    ann, _ = analyze_param_ui(annotation)
    assert ann is str


def test_other_metadata_kept():
    ann, _ = analyze_param_ui(Annotated[str, Field(min_length=3), Placeholder("..."), Label("X")])
    types = [type(m) for m in get_args(ann)[1:]]
    assert Placeholder in types

def test_list_outer_wins_cleans_inner():
    _Inner = Annotated[int, Label("Inner"), Description("Inner desc")]
    ann, meta = analyze_param_ui(Annotated[list[_Inner], Label("Outer")])
    assert meta == ParamUIMetadata(label="Outer", description=None)
    assert get_origin(ann) is list
    assert get_args(ann)[0] is int
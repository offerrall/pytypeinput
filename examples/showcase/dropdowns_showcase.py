from enum import Enum

from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, Dropdown, Literal

from visual_test_base import run_visual_test


class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Status(Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class Size(Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"

class Rating(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class Department(Enum):
    ENGINEERING = "Engineering"
    SALES = "Sales"
    MARKETING = "Marketing"
    HR = "HR"


def get_countries():
    return ["USA", "Canada", "Mexico", "UK", "Germany", "France", "Japan"]

def get_colors():
    return ["Red", "Blue", "Green", "Yellow", "Purple", "Orange"]

def get_years():
    return [2020, 2021, 2022, 2023, 2024, 2025]

def get_skills():
    return ["Python", "JavaScript", "TypeScript", "Rust", "Go", "Java"]


def dropdown_test(
    literal_basic: Literal["Small", "Medium", "Large"],
    
    literal_with_label: Annotated[
        Literal["Active", "Inactive", "Pending"],
        Label("Account Status")
    ],
    
    literal_with_description: Annotated[
        Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        Description("Select your preferred day")
    ],
    
    literal_with_placeholder: Annotated[
        Literal["USD", "EUR", "GBP", "JPY"],
        Placeholder("Choose currency")
    ],
    
    literal_full: Annotated[
        Literal["Beginner", "Intermediate", "Advanced", "Expert"],
        Label("Skill Level"),
        Placeholder("Select level"),
        Description("Choose your current skill level")
    ],
    
    literal_int: Literal[1, 2, 3, 4, 5],
    
    literal_float: Literal[1.0, 2.5, 5.0, 7.5, 10.0],
    
    literal_list: list[Literal["Option A", "Option B", "Option C"]],
    
    literal_list_constrained: Annotated[
        list[Literal["Red", "Green", "Blue", "Yellow"]],
        Field(min_length=2, max_length=4),
        Label("Color Palette"),
        Description("Select 2-4 colors")
    ],
    
    enum_basic: Priority,
    
    enum_with_label: Annotated[Status, Label("Document Status")],
    
    enum_with_description: Annotated[
        Size,
        Description("Select your shirt size")
    ],
    
    enum_with_placeholder: Annotated[
        Department,
        Placeholder("Choose department")
    ],
    
    enum_full: Annotated[
        Priority,
        Label("Task Priority"),
        Placeholder("Set priority"),
        Description("Choose priority level for this task")
    ],
    
    enum_int: Rating,
    
    enum_list: list[Priority],
    
    enum_list_constrained: Annotated[
        list[Status],
        Field(min_length=1, max_length=3),
        Label("Workflow Statuses"),
        Description("Select 1-3 allowed statuses")
    ],
    
    dropdown_basic: Annotated[str, Dropdown(get_countries)],
    
    dropdown_with_label: Annotated[
        str,
        Dropdown(get_colors),
        Label("Theme Color")
    ],
    
    dropdown_with_description: Annotated[
        str,
        Dropdown(get_countries),
        Description("Select your country of residence")
    ],
    
    dropdown_with_placeholder: Annotated[
        str,
        Dropdown(get_skills),
        Placeholder("Pick a skill")
    ],
    
    dropdown_full: Annotated[
        str,
        Dropdown(get_countries),
        Label("Shipping Country"),
        Placeholder("Select country"),
        Description("Where should we ship your order?")
    ],
    
    dropdown_int: Annotated[int, Dropdown(get_years)],
    
    dropdown_list: list[Annotated[str, Dropdown(get_skills)]],
    
    dropdown_list_constrained: Annotated[
        list[Annotated[str, Dropdown(get_colors)]],
        Field(min_length=2, max_length=5),
        Label("Favorite Colors"),
        Description("Select 2-5 favorite colors")
    ],
    
    optional_literal: Literal["Yes", "No", "Maybe"] | None,
    
    optional_enum: Priority | None,
    
    optional_dropdown: Annotated[str, Dropdown(get_countries)] | None,
    
    optional_literal_full: Annotated[
        Literal["Low", "Medium", "High"],
        Label("Urgency Level"),
        Description("Optional: How urgent is this?")
    ] | None,
    
    optional_enum_full: Annotated[
        Status,
        Label("Initial Status"),
        Description("Optional: Set an initial status")
    ] | None,
    
    optional_dropdown_full: Annotated[
        str,
        Dropdown(get_colors),
        Label("Accent Color"),
        Description("Optional: Choose an accent color")
    ] | None,
    
    optional_literal_list: list[Literal["A", "B", "C"]] | None,
    
    optional_enum_list: list[Size] | None,
    
    optional_dropdown_list: list[Annotated[str, Dropdown(get_skills)]] | None,
    
    default_literal: Literal["Draft", "Published", "Archived"] = "Draft",
    
    default_enum: Priority = Priority.MEDIUM,
    
    default_dropdown: Annotated[str, Dropdown(get_countries)] = "USA",
    
    default_literal_full: Annotated[
        Literal["Public", "Private", "Unlisted"],
        Label("Visibility")
    ] = "Public",
    
    default_enum_full: Annotated[
        Status,
        Label("Default Status")
    ] = Status.DRAFT,
    
    default_dropdown_full: Annotated[
        str,
        Dropdown(get_colors),
        Label("Default Color")
    ] = "Blue",
    
    default_literal_list: list[Literal["Tag1", "Tag2", "Tag3"]] = ["Tag2"],
    
    default_enum_list: list[Priority] = [Priority.LOW, Priority.MEDIUM],
    
    default_dropdown_list: list[Annotated[str, Dropdown(get_skills)]] = ["Python", "JavaScript"],
    
    optional_literal_enabled: Annotated[
        Literal["Yes", "No"],
        Label("Email Notifications")
    ] | None = "Yes",
    
    optional_enum_enabled: Annotated[
        Size,
        Label("T-Shirt Size")
    ] | None = Size.M,
    
    optional_dropdown_enabled: Annotated[
        int,
        Dropdown(get_years),
        Label("Birth Year")
    ] | None = 2024,
    
    optional_literal_explicit: Literal["On", "Off"] | OptionalEnabled = None,
    
    optional_enum_explicit: Priority | OptionalDisabled = Priority.LOW,
    
    optional_dropdown_explicit: Annotated[str, Dropdown(get_countries)] | OptionalEnabled = None,
    
    optional_literal_list_enabled: Annotated[
        list[Literal["Mon", "Tue", "Wed", "Thu", "Fri"]],
        Label("Work Days")
    ] | None = ["Mon", "Wed", "Fri"],
    
    optional_enum_list_enabled: Annotated[
        list[Status],
        Label("Allowed Statuses")
    ] | None = [Status.DRAFT, Status.PENDING],
    
    optional_dropdown_list_enabled: Annotated[
        list[Annotated[str, Dropdown(get_colors)]],
        Label("Theme Colors")
    ] | None = ["Red", "Blue"],
):
    pass


if __name__ == "__main__":
    run_visual_test(dropdown_test, "Dropdown Types Test - Literal, Enum & Dropdown Complete")
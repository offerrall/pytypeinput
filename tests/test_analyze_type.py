import pytest
from typing import Annotated
from datetime import date, time

from pytypeinput import analyze_type, Field, Label, Description, Placeholder, Rows, IsPassword, OptionalEnabled


def test_analyze_type_basic_str():
    metadata = analyze_type(str, name="username")
    
    assert metadata.name == "username"
    assert metadata.param_type == str
    assert metadata.default is None
    assert metadata.constraints is None


def test_analyze_type_basic_int():
    metadata = analyze_type(int, name="age")
    
    assert metadata.name == "age"
    assert metadata.param_type == int
    assert metadata.default is None


def test_analyze_type_with_constraints():
    Username = Annotated[str, Field(min_length=3, max_length=20)]
    metadata = analyze_type(Username, name="username")
    
    assert metadata.name == "username"
    assert metadata.param_type == str
    assert metadata.constraints is not None


def test_analyze_type_with_label():
    FullName = Annotated[str, Label("Full Name")]
    metadata = analyze_type(FullName, name="full_name")
    
    assert metadata.name == "full_name"
    assert metadata.ui is not None
    assert metadata.ui.label == "Full Name"


def test_analyze_type_with_all_ui_metadata():
    Bio = Annotated[
        str,
        Field(min_length=10, max_length=500),
        Rows(5),
        Label("Biography"),
        Placeholder("Tell us about yourself..."),
        Description("This will appear on your profile")
    ]
    metadata = analyze_type(Bio, name="bio")
    
    assert metadata.name == "bio"
    assert metadata.param_type == str
    assert metadata.ui is not None
    assert metadata.ui.label == "Biography"
    assert metadata.ui.rows == 5
    assert metadata.ui.placeholder == "Tell us about yourself..."
    assert metadata.ui.description == "This will appear on your profile"


def test_analyze_type_with_password():
    Password = Annotated[str, Field(min_length=8), IsPassword()]
    metadata = analyze_type(Password, name="password")
    
    assert metadata.name == "password"
    assert metadata.ui is not None
    assert metadata.ui.is_password is True


def test_analyze_type_list():
    Tags = list[str]
    metadata = analyze_type(Tags, name="tags")
    
    assert metadata.name == "tags"
    assert metadata.param_type == str
    assert metadata.list is not None


def test_analyze_type_list_with_constraints():
    Skills = Annotated[list[str], Field(min_length=2, max_length=5)]
    metadata = analyze_type(Skills, name="skills")
    
    assert metadata.name == "skills"
    assert metadata.param_type == str
    assert metadata.list is not None
    assert metadata.list.constraints is not None


def test_analyze_type_list_with_item_metadata():
    Emails = list[Annotated[
        str,
        Field(pattern=r'^[^@]+@[^@]+\.[^@]+$'),
        Placeholder("user@example.com")
    ]]
    metadata = analyze_type(Emails, name="emails")
    
    assert metadata.name == "emails"
    assert metadata.param_type == str
    assert metadata.list is not None
    assert metadata.ui is not None
    assert metadata.ui.placeholder == "user@example.com"


def test_analyze_type_date():
    metadata = analyze_type(date, name="birth_date")
    
    assert metadata.name == "birth_date"
    assert metadata.param_type == date


def test_analyze_type_time():
    metadata = analyze_type(time, name="meeting_time")
    
    assert metadata.name == "meeting_time"
    assert metadata.param_type == time


def test_analyze_type_bool():
    metadata = analyze_type(bool, name="newsletter")
    
    assert metadata.name == "newsletter"
    assert metadata.param_type == bool


def test_analyze_type_float():
    Price = Annotated[float, Field(ge=0.0)]
    metadata = analyze_type(Price, name="price")
    
    assert metadata.name == "price"
    assert metadata.param_type == float


def test_analyze_type_custom_name():
    Email = Annotated[str, Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')]
    
    metadata1 = analyze_type(Email, name="primary_email")
    metadata2 = analyze_type(Email, name="secondary_email")
    
    assert metadata1.name == "primary_email"
    assert metadata2.name == "secondary_email"


def test_analyze_type_reusable():
    # Define once
    Username = Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
        Label("Username"),
        Placeholder("Enter username")
    ]
    
    # Reuse multiple times
    metadata1 = analyze_type(Username, name="username")
    metadata2 = analyze_type(Username, name="admin_username")
    metadata3 = analyze_type(Username, name="moderator_username")
    
    # All have same constraints but different names
    assert metadata1.name == "username"
    assert metadata2.name == "admin_username"
    assert metadata3.name == "moderator_username"
    
    assert metadata1.ui.label == metadata2.ui.label == metadata3.ui.label == "Username"
    assert metadata1.ui.placeholder == metadata2.ui.placeholder == metadata3.ui.placeholder


def test_analyze_type_complex_combination():
    ComplexField = Annotated[
        list[Annotated[
            str,
            Field(min_length=10, max_length=200),
            Rows(3),
            Placeholder("Enter item...")
        ]],
        Field(min_length=1, max_length=5),
        Label("Items"),
        Description("Add 1-5 items")
    ]
    metadata = analyze_type(ComplexField, name="items")
    
    assert metadata.name == "items"
    assert metadata.param_type == str
    assert metadata.list is not None
    assert metadata.ui is not None
    assert metadata.ui.label == "Items"
    assert metadata.ui.description == "Add 1-5 items"
    assert metadata.ui.rows == 3
    assert metadata.ui.placeholder == "Enter item..."


def test_analyze_type_no_type_hint_raises():
    # Can't pass None or inspect.Parameter.empty as annotation
    with pytest.raises((TypeError, AttributeError)):
        analyze_type(None, name="field")


def test_analyze_type_default_name():
    metadata = analyze_type(str)
    assert metadata.name == "field"  # Default name
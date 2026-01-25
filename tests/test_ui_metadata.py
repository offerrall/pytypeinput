# tests/test_ui_metadata_extended.py
import pytest
from typing import Annotated
from pydantic import Field

from pytypeinput import analyze_function
from pytypeinput.types import Step, IsPassword, Placeholder, PatternMessage, Description, Label, Rows


# ===== LABEL TESTS =====

def test_label_metadata():
    def func(user_name: Annotated[str, Label("Full Name")]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Full Name"


def test_label_with_field():
    def func(user_email: Annotated[str, Field(min_length=5), Label("Email Address")]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Email Address"
    assert params[0].constraints is not None


def test_label_default_value():
    def func(name: str):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is None


def test_label_with_optional():
    def func(middle_name: Annotated[str, Label("Middle Name")] | None = None):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Middle Name"
    assert params[0].optional is not None


def test_label_with_list():
    def func(tags: Annotated[list[str], Label("Your Tags")]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Your Tags"
    assert params[0].list is not None


def test_label_not_allowed_on_list_items():
    with pytest.raises(TypeError, match="Label not allowed on list items"):
        def func(items: list[Annotated[str, Label("Item")]]):
            pass
        analyze_function(func)


# ===== DESCRIPTION TESTS =====

def test_description_metadata():
    def func(bio: Annotated[str, Description("Tell us about yourself")]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.description == "Tell us about yourself"


def test_description_with_field():
    def func(
        comment: Annotated[
            str, 
            Field(min_length=10, max_length=500), 
            Description("Share your thoughts (10-500 chars)")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.description == "Share your thoughts (10-500 chars)"
    assert params[0].constraints is not None


def test_description_default_value():
    def func(name: str):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is None


def test_description_with_optional():
    def func(
        notes: Annotated[str, Description("Optional notes")] | None = None
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.description == "Optional notes"
    assert params[0].optional is not None


def test_description_with_list():
    def func(
        skills: Annotated[
            list[str], 
            Description("List your top 5 professional skills")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.description == "List your top 5 professional skills"
    assert params[0].list is not None


def test_description_not_allowed_on_list_items():
    with pytest.raises(TypeError, match="Description not allowed on list items"):
        def func(items: list[Annotated[str, Description("Item desc")]]):
            pass
        analyze_function(func)


# ===== ROWS TESTS =====

def test_rows_metadata():
    def func(bio: Annotated[str, Rows(5)]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 5


def test_rows_with_field():
    def func(
        comment: Annotated[str, Field(min_length=10, max_length=1000), Rows(8)]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 8
    assert params[0].constraints is not None


def test_rows_default_value():
    def func(name: str):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is None


def test_rows_with_optional():
    def func(notes: Annotated[str, Rows(4)] | None = None):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 4
    assert params[0].optional is not None


def test_rows_with_list():
    def func(descriptions: list[Annotated[str, Rows(3)]]):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 3
    assert params[0].list is not None


def test_rows_with_placeholder():
    def func(
        bio: Annotated[str, Rows(5), Placeholder("Tell us about yourself...")]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 5
    assert params[0].ui.placeholder == "Tell us about yourself..."


def test_rows_multiple_values():
    def func(
        short: Annotated[str, Rows(2)],
        medium: Annotated[str, Rows(5)],
        long: Annotated[str, Rows(10)]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 3
    assert params[0].ui.rows == 2
    assert params[1].ui.rows == 5
    assert params[2].ui.rows == 10


# ===== COMBINED UI METADATA TESTS =====

def test_label_description_together():
    def func(
        bio: Annotated[
            str,
            Label("Biography"),
            Description("Share your life story")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Biography"
    assert params[0].ui.description == "Share your life story"


def test_label_description_rows_together():
    def func(
        bio: Annotated[
            str,
            Rows(10),
            Label("Your Story"),
            Description("Tell us about your journey")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.rows == 10
    assert params[0].ui.label == "Your Story"
    assert params[0].ui.description == "Tell us about your journey"


def test_all_ui_metadata_combined():
    def func(
        username: Annotated[
            str,
            Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
            Label("Username"),
            Placeholder("Enter username"),
            PatternMessage("Only letters, numbers, underscore"),
            Description("This will be your public identifier")
        ],
        password: Annotated[
            str,
            Field(min_length=8, pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'),
            IsPassword(),
            Label("Password"),
            Placeholder("Secure password"),
            PatternMessage("8+ chars with upper, lower, number"),
            Description("Choose a strong password")
        ],
        bio: Annotated[
            str,
            Field(max_length=500),
            Rows(5),
            Label("Biography"),
            Placeholder("Tell us about yourself..."),
            Description("This will appear on your profile (max 500 chars)")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 3
    
    # Username
    assert params[0].ui.label == "Username"
    assert params[0].ui.placeholder == "Enter username"
    assert params[0].ui.pattern_message == "Only letters, numbers, underscore"
    assert params[0].ui.description == "This will be your public identifier"
    assert params[0].ui.is_password is False
    assert params[0].ui.rows is None
    
    # Password
    assert params[1].ui.label == "Password"
    assert params[1].ui.is_password is True
    assert params[1].ui.placeholder == "Secure password"
    assert params[1].ui.pattern_message == "8+ chars with upper, lower, number"
    assert params[1].ui.description == "Choose a strong password"
    assert params[1].ui.rows is None
    
    # Bio
    assert params[2].ui.label == "Biography"
    assert params[2].ui.rows == 5
    assert params[2].ui.placeholder == "Tell us about yourself..."
    assert params[2].ui.description == "This will appear on your profile (max 500 chars)"
    assert params[2].ui.is_password is False


def test_list_with_label_description():
    def func(
        skills: Annotated[
            list[Annotated[
                str,
                Field(min_length=2, max_length=50),
                Placeholder("e.g., Python programming")
            ]],
            Field(min_length=2, max_length=5),
            Label("Your Skills"),
            Description("List 2-5 of your professional skills")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Your Skills"
    assert params[0].ui.description == "List 2-5 of your professional skills"
    assert params[0].ui.placeholder == "e.g., Python programming"
    assert params[0].list is not None


def test_list_items_inherit_placeholder_rows():
    def func(
        notes: Annotated[
            list[Annotated[
                str,
                Rows(3),
                Placeholder("Enter note...")
            ]],
            Label("Notes"),
            Description("Add multiple notes")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Notes"
    assert params[0].ui.description == "Add multiple notes"
    assert params[0].ui.rows == 3
    assert params[0].ui.placeholder == "Enter note..."


def test_optional_with_all_metadata():
    def func(
        middle_name: Annotated[
            str,
            Label("Middle Name"),
            Placeholder("Optional"),
            Description("Your middle name (if you have one)")
        ] | None = None
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Middle Name"
    assert params[0].ui.placeholder == "Optional"
    assert params[0].ui.description == "Your middle name (if you have one)"
    assert params[0].optional is not None


# ===== ORDER INDEPENDENCE TESTS =====

def test_ui_metadata_order_independence_full():
    def func1(
        field1: Annotated[
            str,
            Label("Test"),
            Description("Desc"),
            Rows(5),
            Placeholder("PH"),
            Field(min_length=3)
        ]
    ):
        pass
    
    def func2(
        field2: Annotated[
            str,
            Field(min_length=3),
            Rows(5),
            Description("Desc"),
            Placeholder("PH"),
            Label("Test")
        ]
    ):
        pass
    
    params1 = analyze_function(func1)
    params2 = analyze_function(func2)
    
    assert params1[0].ui.label == params2[0].ui.label == "Test"
    assert params1[0].ui.description == params2[0].ui.description == "Desc"
    assert params1[0].ui.rows == params2[0].ui.rows == 5
    assert params1[0].ui.placeholder == params2[0].ui.placeholder == "PH"


# ===== DEFAULTS TESTS =====

def test_ui_defaults_when_label_present():
    def func(name: Annotated[str, Label("Name")]):
        pass
    
    params = analyze_function(func)
    assert params[0].ui is not None
    assert params[0].ui.label == "Name"
    assert params[0].ui.description is None
    assert params[0].ui.rows is None
    assert params[0].ui.placeholder is None
    assert params[0].ui.is_password is False
    assert params[0].ui.step == 1


def test_ui_defaults_when_description_present():
    def func(bio: Annotated[str, Description("Bio text")]):
        pass
    
    params = analyze_function(func)
    assert params[0].ui is not None
    assert params[0].ui.description == "Bio text"
    assert params[0].ui.label is None
    assert params[0].ui.rows is None
    assert params[0].ui.placeholder is None


def test_ui_defaults_when_rows_present():
    def func(text: Annotated[str, Rows(8)]):
        pass
    
    params = analyze_function(func)
    assert params[0].ui is not None
    assert params[0].ui.rows == 8
    assert params[0].ui.label is None
    assert params[0].ui.description is None


# ===== EDGE CASES =====

def test_multiple_fields_different_metadata():
    def func(
        field1: Annotated[str, Label("One")],
        field2: Annotated[str, Description("Two")],
        field3: Annotated[str, Rows(3)],
        field4: str
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 4
    assert params[0].ui is not None and params[0].ui.label == "One"
    assert params[1].ui is not None and params[1].ui.description == "Two"
    assert params[2].ui is not None and params[2].ui.rows == 3
    assert params[3].ui is None


def test_label_description_on_integers():
    def func(
        age: Annotated[
            int,
            Field(ge=0, le=120),
            Step(1),
            Label("Your Age"),
            Description("How old are you?")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Your Age"
    assert params[0].ui.description == "How old are you?"
    assert params[0].ui.step == 1


def test_label_description_on_floats():
    def func(
        price: Annotated[
            float,
            Field(ge=0.0),
            Step(0.01),
            Label("Price (USD)"),
            Description("Enter the product price")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    assert params[0].ui is not None
    assert params[0].ui.label == "Price (USD)"
    assert params[0].ui.description == "Enter the product price"
    assert params[0].ui.step == 0.01


def test_empty_strings_not_allowed():
    # Label, Description, Placeholder no deberían aceptar strings vacíos
    # pero eso se valida en types.py al inicializar las clases
    pass


def test_list_level_vs_item_level_metadata():
    def func(
        emails: Annotated[
            list[Annotated[
                str,
                Field(pattern=r'^[^@]+@[^@]+$'),
                Placeholder("user@example.com"),
                PatternMessage("Invalid email")
            ]],
            Field(min_length=1, max_length=3),
            Label("Email Addresses"),
            Description("Add 1-3 email addresses")
        ]
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 1
    
    # List level metadata
    assert params[0].ui.label == "Email Addresses"
    assert params[0].ui.description == "Add 1-3 email addresses"
    
    # Item level metadata
    assert params[0].ui.placeholder == "user@example.com"
    assert params[0].ui.pattern_message == "Invalid email"
    
    # Constraints
    assert params[0].list.constraints is not None
    assert params[0].constraints is not None


def test_complex_real_world_form():
    def func(
        full_name: Annotated[
            str,
            Field(min_length=2, max_length=100),
            Label("Full Name"),
            Placeholder("John Doe"),
            Description("Your legal name")
        ],
        email: Annotated[
            str,
            Field(pattern=r'^[^@]+@[^@]+\.[^@]+$'),
            Label("Email Address"),
            Placeholder("john@example.com"),
            PatternMessage("Please enter a valid email"),
            Description("We'll send confirmation here")
        ],
        password: Annotated[
            str,
            Field(min_length=8, pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'),
            IsPassword(),
            Label("Password"),
            Placeholder("Strong password"),
            PatternMessage("8+ chars: upper, lower, number required"),
            Description("Choose a secure password")
        ],
        age: Annotated[
            int,
            Field(ge=18, le=120),
            Step(1),
            Label("Age"),
            Description("Must be 18 or older")
        ],
        bio: Annotated[
            str,
            Field(max_length=500),
            Rows(5),
            Label("About You"),
            Placeholder("Tell us your story..."),
            Description("Brief introduction (max 500 characters)")
        ],
        skills: Annotated[
            list[Annotated[
                str,
                Field(min_length=2, max_length=50),
                Rows(2),
                Placeholder("e.g., Python, JavaScript")
            ]],
            Field(min_length=3, max_length=10),
            Label("Skills"),
            Description("List 3-10 professional skills")
        ],
        newsletter: bool = True
    ):
        pass
    
    params = analyze_function(func)
    assert len(params) == 7
    
    # Verify all metadata is correctly extracted
    assert all(p.ui is not None for p in params[:6])
    assert params[6].ui is None  # newsletter has no UI metadata
    
    # Spot check a few
    assert params[0].ui.label == "Full Name"
    assert params[2].ui.is_password is True
    assert params[4].ui.rows == 5
    assert params[5].ui.description == "List 3-10 professional skills"
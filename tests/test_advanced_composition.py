import pytest
from typing import Annotated, TypeAlias
from pydantic import Field
from pytypeinput import (
    analyze_function,
    analyze_type,
    analyze_dataclass,
    Email,
    Color,
    ImageFile,
    Slider,
    Label,
    Description,
    Placeholder,
    PatternMessage,
    Step,
    Rows,
    IsPassword
)
from dataclasses import dataclass


# ==================== DOMAIN TYPE LIBRARY ====================

# Numeric base types
PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
NegativeInt: TypeAlias = Annotated[int, Field(lt=0)]
PositiveFloat: TypeAlias = Annotated[float, Field(ge=0.0)]

# Percentage (0-100)
Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]

# Score (0-10)
Score: TypeAlias = Annotated[PositiveInt, Field(le=10)]

# Age
Age: TypeAlias = Annotated[PositiveInt, Field(le=120)]

# Temperature (above absolute zero)
Temperature: TypeAlias = Annotated[float, Field(gt=-273.15)]

# String base types
NonEmptyString: TypeAlias = Annotated[str, Field(min_length=1)]
ShortString: TypeAlias = Annotated[str, Field(max_length=50)]
MediumString: TypeAlias = Annotated[str, Field(max_length=200)]
LongString: TypeAlias = Annotated[str, Field(max_length=1000)]

# Combined string types
ShortRequired: TypeAlias = Annotated[NonEmptyString, Field(max_length=50)]
MediumRequired: TypeAlias = Annotated[NonEmptyString, Field(max_length=200)]

# Username with validation
Username: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
]

# Slug (URL-safe)
Slug: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=50, pattern=r'^[a-z0-9-]+$')
]

# Email variants
ValidatedEmail: TypeAlias = Annotated[Email, Field(min_length=5, max_length=254)]
ShortEmail: TypeAlias = Annotated[Email, Field(max_length=100)]

# UI-enhanced types
VolumeSlider: TypeAlias = Annotated[
    Percentage,
    Slider(),
    Label("Volume"),
    Description("Audio volume (0-100%)")
]

BrightnessSlider: TypeAlias = Annotated[
    Percentage,
    Slider(show_value=True),
    Label("Brightness"),
    Description("Screen brightness level")
]

OpacitySlider: TypeAlias = Annotated[
    Annotated[float, Field(ge=0.0, le=1.0)],
    Slider(),
    Label("Opacity"),
    Step(0.1)
]

LabeledUsername: TypeAlias = Annotated[
    Username,
    Label("Username"),
    Description("Choose a unique username (3-20 characters)"),
    Placeholder("Enter username"),
    PatternMessage("Only letters, numbers, and underscores allowed")
]

LabeledEmail: TypeAlias = Annotated[
    ValidatedEmail,
    Label("Email Address"),
    Placeholder("you@example.com"),
    Description("We'll never share your email")
]

LabeledAge: TypeAlias = Annotated[
    Age,
    Label("Age"),
    Description("You must be 18 or older to register")
]

SecurePassword: TypeAlias = Annotated[
    str,
    Field(min_length=8, max_length=128),
    IsPassword,
    Label("Password"),
    Description("Minimum 8 characters"),
    Placeholder("Enter secure password")
]

LongBio: TypeAlias = Annotated[
    LongString,
    Rows(5),
    Label("Biography"),
    Description("Tell us about yourself"),
    Placeholder("Write a short bio...")
]

ThemeColor: TypeAlias = Annotated[
    Color,
    Field(min_length=7, max_length=7),
    Label("Theme Color"),
    Description("Choose your primary theme color")
]


# ==================== ADVANCED COMPOSITION TESTS ====================

class TestAdvancedTypeComposition:
    """Test advanced type composition scenarios."""
    
    def test_triple_nested_numeric_composition(self):
        """Three levels: base → percentage → slider with UI."""
        param = analyze_type(VolumeSlider, name="volume")
        
        # Check all constraints merged
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in param.constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in param.constraints.metadata)
        
        assert has_ge, "Should inherit ge=0 from PositiveInt"
        assert has_le, "Should inherit le=100 from Percentage"
        
        # Check UI metadata
        assert param.ui is not None
        assert param.ui.is_slider is True
        assert param.ui.label == "Volume"
        assert param.ui.description == "Audio volume (0-100%)"
    
    def test_opacity_slider_with_step(self):
        """Float slider with custom step."""
        param = analyze_type(OpacitySlider, name="opacity")
        
        has_ge = any(hasattr(c, 'ge') and c.ge == 0.0 for c in param.constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 1.0 for c in param.constraints.metadata)
        
        assert has_ge
        assert has_le
        assert param.ui.is_slider is True
        assert param.ui.step == 0.1
        assert param.ui.label == "Opacity"
    
    def test_quadruple_nested_string_composition(self):
        """Four levels: str → NonEmpty → Short → Username → UI."""
        param = analyze_type(LabeledUsername, name="user")
        
        # Check constraints
        has_min = any(hasattr(c, 'min_length') and c.min_length == 3 for c in param.constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 20 for c in param.constraints.metadata)
        has_pattern = any(hasattr(c, 'pattern') for c in param.constraints.metadata)
        
        assert has_min
        assert has_max
        assert has_pattern
        
        # Check all UI metadata
        assert param.ui.label == "Username"
        assert param.ui.description is not None
        assert param.ui.placeholder == "Enter username"
        assert param.ui.pattern_message is not None
    
    def test_email_double_inheritance_with_ui(self):
        """Email → ValidatedEmail → LabeledEmail."""
        param = analyze_type(LabeledEmail, name="contact")
        
        # Should have Email widget
        assert param.widget_type == "Email"
        
        # Should have length constraints
        has_min = any(hasattr(c, 'min_length') and c.min_length == 5 for c in param.constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 254 for c in param.constraints.metadata)
        has_pattern = any(hasattr(c, 'pattern') for c in param.constraints.metadata)
        
        assert has_min, "Should have min_length=5"
        assert has_max, "Should have max_length=254"
        assert has_pattern, "Should preserve Email pattern"
        
        # Check UI
        assert param.ui.label == "Email Address"
        assert param.ui.placeholder == "you@example.com"
        assert param.ui.description is not None
    
    def test_password_with_multiple_constraints_and_ui(self):
        """Password with length + IsPassword + UI metadata."""
        param = analyze_type(SecurePassword, name="pwd")
        
        has_min = any(hasattr(c, 'min_length') and c.min_length == 8 for c in param.constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 128 for c in param.constraints.metadata)
        
        assert has_min
        assert has_max
        assert param.ui.is_password is True
        assert param.ui.label == "Password"
        assert param.ui.description == "Minimum 8 characters"
        assert param.ui.placeholder is not None
    
    def test_long_bio_with_rows_and_ui(self):
        """LongString → Rows + Label + Description."""
        param = analyze_type(LongBio, name="bio")
        
        has_max = any(hasattr(c, 'max_length') and c.max_length == 1000 for c in param.constraints.metadata)
        
        assert has_max
        assert param.ui.rows == 5
        assert param.ui.label == "Biography"
        assert param.ui.description is not None
        assert param.ui.placeholder is not None
    
    def test_theme_color_with_exact_length(self):
        """Color with exact hex format (#RRGGBB)."""
        param = analyze_type(ThemeColor, name="theme")
        
        assert param.widget_type == "Color"
        
        has_min = any(hasattr(c, 'min_length') and c.min_length == 7 for c in param.constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 7 for c in param.constraints.metadata)
        has_pattern = any(hasattr(c, 'pattern') for c in param.constraints.metadata)
        
        assert has_min
        assert has_max
        assert has_pattern
        assert param.ui.label == "Theme Color"
        assert param.ui.description is not None


class TestRealWorldDomainForms:
    """Real-world forms using composed domain types."""
    
    def test_user_registration_form(self):
        """Complete registration form with composed types."""
        @dataclass
        class RegistrationForm:
            username: LabeledUsername
            email: LabeledEmail
            password: SecurePassword
            age: LabeledAge
            bio: LongBio | None = None
        
        params = analyze_dataclass(RegistrationForm)
        
        # Username
        assert params[0].ui.label == "Username"
        assert params[0].constraints is not None
        
        # Email
        assert params[1].widget_type == "Email"
        assert params[1].ui.label == "Email Address"
        
        # Password
        assert params[2].ui.is_password is True
        assert params[2].ui.label == "Password"
        
        # Age
        assert params[3].ui.label == "Age"
        has_ge = any(hasattr(c, 'ge') for c in params[3].constraints.metadata)
        has_le = any(hasattr(c, 'le') for c in params[3].constraints.metadata)
        assert has_ge and has_le
        
        # Bio (optional)
        assert params[4].optional is not None
        assert params[4].ui.rows == 5
    
    def test_media_settings_form(self):
        """Settings form with multiple sliders."""
        @dataclass
        class MediaSettings:
            volume: VolumeSlider = 50
            brightness: BrightnessSlider = 75
            opacity: OpacitySlider = 1.0
            theme: ThemeColor = "#3B82F6"
        
        params = analyze_dataclass(MediaSettings)
        
        # All should be sliders
        assert params[0].ui.is_slider is True
        assert params[1].ui.is_slider is True
        assert params[2].ui.is_slider is True
        
        # All should have labels
        assert params[0].ui.label == "Volume"
        assert params[1].ui.label == "Brightness"
        assert params[2].ui.label == "Opacity"
        
        # Theme should be color picker
        assert params[3].widget_type == "Color"
        
        # All should have defaults
        assert params[0].default == 50
        assert params[1].default == 75
        assert params[2].default == 1.0
        assert params[3].default == "#3B82F6"
    
    def test_content_creation_form(self):
        """Blog post form with string compositions."""
        @dataclass
        class BlogPostForm:
            title: Annotated[ShortRequired, Label("Post Title"), Placeholder("Enter title")]
            slug: Annotated[Slug, Label("URL Slug"), Placeholder("my-post-title")]
            excerpt: Annotated[MediumRequired, Rows(3), Label("Excerpt")]
            content: Annotated[LongString, Rows(10), Label("Content")]
            author_email: ShortEmail
        
        params = analyze_dataclass(BlogPostForm)
        
        # Title - short required with UI
        title_has_min = any(hasattr(c, 'min_length') and c.min_length == 1 for c in params[0].constraints.metadata)
        title_has_max = any(hasattr(c, 'max_length') and c.max_length == 50 for c in params[0].constraints.metadata)
        assert title_has_min and title_has_max
        assert params[0].ui.label == "Post Title"
        
        # Slug - with pattern
        slug_has_pattern = any(hasattr(c, 'pattern') for c in params[1].constraints.metadata)
        assert slug_has_pattern
        assert params[1].ui.label == "URL Slug"
        
        # Excerpt - medium with rows
        assert params[2].ui.rows == 3
        
        # Content - long with many rows
        assert params[3].ui.rows == 10
        
        # Email - short variant
        assert params[4].widget_type == "Email"
        email_has_max = any(hasattr(c, 'max_length') and c.max_length == 100 for c in params[4].constraints.metadata)
        assert email_has_max


class TestComplexNesting:
    """Test very deep nesting scenarios."""
    
    def test_five_level_composition(self):
        """Five levels of composition."""
        Level1: TypeAlias = Annotated[int, Field(ge=0)]
        Level2: TypeAlias = Annotated[Level1, Field(le=100)]
        Level3: TypeAlias = Annotated[Level2, Slider()]
        Level4: TypeAlias = Annotated[Level3, Label("Value")]
        Level5: TypeAlias = Annotated[Level4, Description("Adjust the value")]
        
        param = analyze_type(Level5, name="val")
        
        # All constraints merged
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in param.constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in param.constraints.metadata)
        
        assert has_ge
        assert has_le
        
        # All UI merged
        assert param.ui.is_slider is True
        assert param.ui.label == "Value"
        assert param.ui.description == "Adjust the value"
    
    def test_branching_composition(self):
        """Same base type, different UI branches."""
        Base: TypeAlias = Annotated[int, Field(ge=0, le=100)]
        
        SliderVersion: TypeAlias = Annotated[Base, Slider(), Label("Slider")]
        SteppedVersion: TypeAlias = Annotated[Base, Step(10), Label("Stepped")]
        PlainVersion: TypeAlias = Annotated[Base, Label("Plain")]
        
        slider_param = analyze_type(SliderVersion, name="s")
        stepped_param = analyze_type(SteppedVersion, name="st")
        plain_param = analyze_type(PlainVersion, name="p")
        
        # All have same constraints
        for p in [slider_param, stepped_param, plain_param]:
            has_ge = any(hasattr(c, 'ge') for c in p.constraints.metadata)
            has_le = any(hasattr(c, 'le') for c in p.constraints.metadata)
            assert has_ge and has_le
        
        # Different UI
        assert slider_param.ui.is_slider is True
        assert stepped_param.ui.step == 10
        assert plain_param.ui.is_slider is False
    
    def test_mixed_special_types_and_composition(self):
        """Special types with deep composition."""
        # Image with size limit hint
        SmallImage: TypeAlias = Annotated[
            ImageFile,
            Label("Profile Picture"),
            Description("Max 2MB, square format recommended")
        ]
        
        # Email with work domain
        WorkEmail: TypeAlias = Annotated[
            ValidatedEmail,
            Field(pattern=r'.*@company\.com$'),
            Label("Work Email"),
            Description("Must be a company email address")
        ]
        
        @dataclass
        class EmployeeForm:
            photo: SmallImage
            email: WorkEmail
        
        params = analyze_dataclass(EmployeeForm)
        
        # Image
        assert params[0].widget_type == "ImageFile"
        assert params[0].ui.label == "Profile Picture"
        assert params[0].ui.description is not None
        
        # Email with multiple patterns
        assert params[1].widget_type == "Email"
        pattern_count = sum(1 for c in params[1].constraints.metadata if hasattr(c, 'pattern'))
        assert pattern_count >= 2, "Should have Email pattern + company domain pattern"


class TestTypeLibraryReuse:
    """Test that type library enables DRY principle."""
    
    def test_percentage_reused_multiple_times(self):
        """Same Percentage type used in multiple contexts."""
        @dataclass
        class Form:
            cpu_usage: Annotated[Percentage, Label("CPU Usage")]
            memory_usage: Annotated[Percentage, Label("Memory Usage")]
            disk_usage: Annotated[Percentage, Label("Disk Usage")]
        
        params = analyze_dataclass(Form)
        
        # All three have same constraints
        for param in params:
            has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in param.constraints.metadata)
            has_le = any(hasattr(c, 'le') and c.le == 100 for c in param.constraints.metadata)
            assert has_ge and has_le
        
        # But different labels
        assert params[0].ui.label == "CPU Usage"
        assert params[1].ui.label == "Memory Usage"
        assert params[2].ui.label == "Disk Usage"
    
    def test_age_type_consistency(self):
        """Age type used across multiple forms maintains consistency."""
        @dataclass
        class UserForm:
            age: Age
        
        @dataclass
        class EmployeeForm:
            employee_age: Age
        
        @dataclass
        class StudentForm:
            student_age: Age
        
        user_params = analyze_dataclass(UserForm)
        employee_params = analyze_dataclass(EmployeeForm)
        student_params = analyze_dataclass(StudentForm)
        
        # All should have exact same constraints
        for params in [user_params, employee_params, student_params]:
            has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
            has_le = any(hasattr(c, 'le') and c.le == 120 for c in params[0].constraints.metadata)
            assert has_ge and has_le


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
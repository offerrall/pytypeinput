import pytest
from typing import Annotated, TypeAlias
from pydantic import Field
from pytypeinput import (
    analyze_function,
    analyze_type,
    Email,
    Color,
    Slider,
    Label,
    Description,
    Placeholder
)


# ==================== REUSABLE TYPE ALIASES ====================

# Basic building blocks
PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
NegativeInt: TypeAlias = Annotated[int, Field(lt=0)]
NonNegativeFloat: TypeAlias = Annotated[float, Field(ge=0.0)]

# Composed constraints
Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]
Score0to10: TypeAlias = Annotated[PositiveInt, Field(le=10)]
Temperature: TypeAlias = Annotated[int, Field(ge=-273, le=1000)]

# With UI
PercentageSlider: TypeAlias = Annotated[Percentage, Slider(), Label("Percentage")]
VolumeControl: TypeAlias = Annotated[Percentage, Slider(), Label("Volume"), Description("0-100")]

# String constraints
ShortString: TypeAlias = Annotated[str, Field(max_length=50)]
LongString: TypeAlias = Annotated[str, Field(max_length=500)]
RequiredString: TypeAlias = Annotated[str, Field(min_length=1)]
ShortRequiredString: TypeAlias = Annotated[RequiredString, Field(max_length=50)]

# Username patterns
Username: TypeAlias = Annotated[str, Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')]
LabeledUsername: TypeAlias = Annotated[Username, Label("Username"), Description("3-20 chars, alphanumeric + underscore")]

# Email variants
ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
ShortEmail: TypeAlias = Annotated[Email, Field(max_length=100)]
WorkEmail: TypeAlias = Annotated[ValidEmail, Field(pattern=r'.*@company\.com$')]

# Color variants
HexColor: TypeAlias = Annotated[Color, Field(min_length=7, max_length=7)]
LabeledColor: TypeAlias = Annotated[Color, Label("Theme Color")]


# ==================== TYPE COMPOSITION TESTS ====================

class TestTypeComposition:
    """Test composition of type aliases with Field constraints."""
    
    def test_positive_int_base(self):
        """PositiveInt has ge=0 constraint."""
        def func(value: PositiveInt): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
        assert has_ge
    
    def test_percentage_inherits_positive_and_adds_max(self):
        """Percentage inherits ge=0 from PositiveInt and adds le=100."""
        def func(value: Percentage): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in params[0].constraints.metadata)
        
        assert has_ge, "Should inherit ge=0 from PositiveInt"
        assert has_le, "Should add le=100"
    
    def test_percentage_slider_inherits_all_constraints(self):
        """PercentageSlider inherits constraints and adds UI."""
        def func(volume: PercentageSlider): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le
        assert params[0].ui is not None
        assert params[0].ui.is_slider is True
        assert params[0].ui.label == "Percentage"
    
    def test_volume_control_inherits_all_with_description(self):
        """VolumeControl has all constraints plus UI metadata."""
        def func(vol: VolumeControl): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le
        assert params[0].ui.is_slider is True
        assert params[0].ui.label == "Volume"
        assert params[0].ui.description == "0-100"
    
    def test_score_0_to_10_composition(self):
        """Score0to10 composes PositiveInt with le=10."""
        def func(rating: Score0to10): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 10 for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le
    
    def test_temperature_with_negative_range(self):
        """Temperature has both negative min and positive max."""
        def func(temp: Temperature): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == -273 for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 1000 for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le


class TestStringComposition:
    """Test composition of string type aliases."""
    
    def test_short_string(self):
        """ShortString has max_length=50."""
        def func(text: ShortString): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_max = any(hasattr(c, 'max_length') and c.max_length == 50 for c in params[0].constraints.metadata)
        assert has_max
    
    def test_required_string(self):
        """RequiredString has min_length=1."""
        def func(text: RequiredString): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_min = any(hasattr(c, 'min_length') and c.min_length == 1 for c in params[0].constraints.metadata)
        assert has_min
    
    def test_short_required_string_composition(self):
        """ShortRequiredString composes both min and max."""
        def func(text: ShortRequiredString): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_min = any(hasattr(c, 'min_length') and c.min_length == 1 for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 50 for c in params[0].constraints.metadata)
        
        assert has_min
        assert has_max
    
    def test_username_has_all_constraints(self):
        """Username has min, max, and pattern."""
        def func(user: Username): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_min = any(hasattr(c, 'min_length') and c.min_length == 3 for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 20 for c in params[0].constraints.metadata)
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        
        assert has_min
        assert has_max
        assert has_pattern
    
    def test_labeled_username_inherits_and_adds_ui(self):
        """LabeledUsername inherits all constraints and adds UI."""
        def func(user: LabeledUsername): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_min = any(hasattr(c, 'min_length') for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') for c in params[0].constraints.metadata)
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        
        assert has_min
        assert has_max
        assert has_pattern
        assert params[0].ui is not None
        assert params[0].ui.label == "Username"
        assert params[0].ui.description is not None


class TestEmailInheritance:
    """Test Email type inheritance and composition."""
    
    def test_valid_email_inherits_pattern_adds_max(self):
        """ValidEmail inherits Email pattern and adds max_length."""
        def func(email: ValidEmail): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 254 for c in params[0].constraints.metadata)
        
        assert has_pattern
        assert has_max
    
    def test_short_email_inherits_pattern_adds_shorter_max(self):
        """ShortEmail inherits Email pattern and adds max_length=100."""
        def func(email: ShortEmail): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 100 for c in params[0].constraints.metadata)
        
        assert has_pattern
        assert has_max
    
    def test_work_email_replaces_pattern_loses_widget(self):
        """WorkEmail replaces Email pattern, loses Email widget type.
        
        When you override the pattern, the widget type detection uses the new pattern.
        Since '.*@company\.com$' is not a recognized special type, widget_type becomes None.
        
        To preserve Email widget while adding domain validation, combine patterns manually.
        """
        def func(email: WorkEmail): pass
        params = analyze_function(func)
        
        # widget_type is None (pattern override not recognized)
        assert params[0].widget_type is None
        
        # But still has all constraints
        max_lens = [c.max_length for c in params[0].constraints.metadata if hasattr(c, 'max_length')]
        patterns = [c.pattern for c in params[0].constraints.metadata if hasattr(c, 'pattern')]
        
        assert len(max_lens) == 1
        assert max_lens[0] == 254
        
        assert len(patterns) == 1
        assert patterns[0] == r'.*@company\.com$'


class TestColorInheritance:
    """Test Color type inheritance."""
    
    def test_hex_color_inherits_pattern_adds_length(self):
        """HexColor inherits Color pattern and adds exact length."""
        def func(color: HexColor): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Color"
        assert params[0].constraints is not None
        
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        has_min = any(hasattr(c, 'min_length') and c.min_length == 7 for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') and c.max_length == 7 for c in params[0].constraints.metadata)
        
        assert has_pattern
        assert has_min
        assert has_max
    
    def test_labeled_color_inherits_pattern_adds_ui(self):
        """LabeledColor inherits Color pattern and adds Label."""
        def func(theme: LabeledColor): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Color"
        assert params[0].constraints is not None
        
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        
        assert has_pattern
        assert params[0].ui is not None
        assert params[0].ui.label == "Theme Color"


class TestComplexComposition:
    """Test complex multi-level compositions."""
    
    def test_triple_composition_int(self):
        """Three levels of composition all merge correctly."""
        Base: TypeAlias = Annotated[int, Field(ge=0)]
        Middle: TypeAlias = Annotated[Base, Field(le=100)]
        Top: TypeAlias = Annotated[Middle, Slider(), Label("Value")]
        
        def func(val: Top): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le
        assert params[0].ui.is_slider is True
        assert params[0].ui.label == "Value"
    
    def test_quadruple_composition_string(self):
        """Four levels of composition - last pattern wins."""
        Level1: TypeAlias = Annotated[str, Field(min_length=1)]
        Level2: TypeAlias = Annotated[Level1, Field(max_length=100)]
        Level3: TypeAlias = Annotated[Level2, Field(pattern=r'^[A-Z]')]
        Level4: TypeAlias = Annotated[Level3, Label("Name"), Description("Must start with capital")]
        
        def func(name: Level4): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        has_min = any(hasattr(c, 'min_length') for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') for c in params[0].constraints.metadata)
        
        # Only last pattern
        patterns = [c.pattern for c in params[0].constraints.metadata if hasattr(c, 'pattern')]
        
        assert has_min
        assert has_max
        assert len(patterns) == 1
        assert patterns[0] == r'^[A-Z]'
        assert params[0].ui.label == "Name"
        assert params[0].ui.description is not None
    
    def test_mixing_special_types_with_composition(self):
        """Special types work with multi-level composition."""
        ValidatedEmail: TypeAlias = Annotated[Email, Field(min_length=5, max_length=100)]
        LabeledEmail: TypeAlias = Annotated[ValidatedEmail, Label("Email"), Placeholder("you@example.com")]
        
        def func(contact: LabeledEmail): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(hasattr(c, 'pattern') for c in params[0].constraints.metadata)
        has_min = any(hasattr(c, 'min_length') for c in params[0].constraints.metadata)
        has_max = any(hasattr(c, 'max_length') for c in params[0].constraints.metadata)
        
        assert has_pattern
        assert has_min
        assert has_max
        assert params[0].ui.label == "Email"
        assert params[0].ui.placeholder == "you@example.com"


class TestConstraintOverride:
    """Test constraint override behavior (last wins)."""
    
    def test_max_length_override(self):
        """Later max_length overrides earlier one."""
        Base: TypeAlias = Annotated[str, Field(max_length=100)]
        Strict: TypeAlias = Annotated[Base, Field(max_length=50)]
        
        def func(text: Strict): pass
        params = analyze_function(func)
        
        max_lens = [c.max_length for c in params[0].constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(max_lens) == 1
        assert max_lens[0] == 50, "Should use last max_length"
    
    def test_ge_override(self):
        """Later ge overrides earlier one."""
        Base: TypeAlias = Annotated[int, Field(ge=0)]
        Strict: TypeAlias = Annotated[Base, Field(ge=10)]
        
        def func(value: Strict): pass
        params = analyze_function(func)
        
        ge_vals = [c.ge for c in params[0].constraints.metadata if hasattr(c, 'ge')]
        
        assert len(ge_vals) == 1
        assert ge_vals[0] == 10, "Should use last ge"
    
    def test_pattern_override(self):
        """Later pattern overrides earlier one."""
        Base: TypeAlias = Annotated[str, Field(pattern=r'^[a-z]+$')]
        Override: TypeAlias = Annotated[Base, Field(pattern=r'^[a-z]{3,}$')]
        
        def func(value: Override): pass
        params = analyze_function(func)
        
        patterns = [c.pattern for c in params[0].constraints.metadata if hasattr(c, 'pattern')]
        
        assert len(patterns) == 1
        assert patterns[0] == r'^[a-z]{3,}$', "Should use last pattern"


class TestRealWorldDomainTypes:
    """Real-world examples of domain-driven type design."""
    
    def test_user_profile_with_domain_types(self):
        """User profile using composed domain types."""
        Age: TypeAlias = Annotated[PositiveInt, Field(le=120), Label("Age")]
        Bio: TypeAlias = Annotated[LongString, Label("Biography"), Description("Tell us about yourself")]
        
        def create_profile(
            username: LabeledUsername,
            email: ValidEmail,
            age: Age,
            bio: Bio | None = None
        ): pass
        
        params = analyze_function(create_profile)
        
        # Username
        assert params[0].constraints is not None
        assert params[0].ui.label == "Username"
        
        # Email
        assert params[1].widget_type == "Email"
        assert params[1].constraints is not None
        
        # Age
        assert params[2].constraints is not None
        assert params[2].ui.label == "Age"
        
        # Bio
        assert params[3].constraints is not None
        assert params[3].optional is not None
        assert params[3].ui.label == "Biography"
    
    def test_settings_form_with_sliders(self):
        """Settings form using slider compositions."""
        Brightness: TypeAlias = Annotated[Percentage, Slider(), Label("Brightness")]
        Contrast: TypeAlias = Annotated[Percentage, Slider(), Label("Contrast")]
        
        def update_display_settings(
            brightness: Brightness = 50,
            contrast: Contrast = 50,
            theme: LabeledColor = "#FFFFFF"
        ): pass
        
        params = analyze_function(update_display_settings)
        
        # Brightness
        assert params[0].ui.is_slider is True
        assert params[0].ui.label == "Brightness"
        has_ge = any(hasattr(c, 'ge') for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') for c in params[0].constraints.metadata)
        assert has_ge and has_le
        
        # Contrast
        assert params[1].ui.is_slider is True
        assert params[1].ui.label == "Contrast"
        
        # Theme
        assert params[2].widget_type == "Color"
        assert params[2].ui.label == "Theme Color"


class TestAnalyzeTypeWithComposition:
    """Test analyze_type() with composed types."""
    
    def test_analyze_type_with_percentage(self):
        """analyze_type works with composed Percentage type."""
        metadata = analyze_type(Percentage, name="completion")
        
        assert metadata.constraints is not None
        has_ge = any(hasattr(c, 'ge') and c.ge == 0 for c in metadata.constraints.metadata)
        has_le = any(hasattr(c, 'le') and c.le == 100 for c in metadata.constraints.metadata)
        
        assert has_ge
        assert has_le
    
    def test_analyze_type_with_labeled_username(self):
        """analyze_type works with UI-enhanced types."""
        metadata = analyze_type(LabeledUsername, name="user")
        
        assert metadata.constraints is not None
        assert metadata.ui is not None
        assert metadata.ui.label == "Username"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
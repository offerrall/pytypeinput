import pytest
from typing import Annotated, TypeAlias
from pydantic import Field
from pytypeinput import (
    analyze_type,
    analyze_function,
    Email,
    Label,
    Description,
    Placeholder,
    Slider,
    Step,
    PatternMessage
)


class TestConstraintMerging:
    """Test constraint merging rules: different types merge, same type last wins."""
    
    def test_different_constraints_merge(self):
        """Different constraint types are accumulated."""
        Base: TypeAlias = Annotated[str, Field(max_length=100)]
        Enhanced: TypeAlias = Annotated[Base, Field(min_length=5)]
        
        param = analyze_type(Enhanced, name="text")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 5
        assert len(max_lens) == 1
        assert max_lens[0] == 100
    
    def test_same_constraint_last_wins_max_length(self):
        """Same constraint type - last one wins (max_length)."""
        Loose: TypeAlias = Annotated[str, Field(max_length=100)]
        Strict: TypeAlias = Annotated[Loose, Field(max_length=50)]
        
        param = analyze_type(Strict, name="text")
        
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(max_lens) == 1
        assert max_lens[0] == 50, "Last max_length should win"
    
    def test_same_constraint_last_wins_min_length(self):
        """Same constraint type - last one wins (min_length)."""
        Base: TypeAlias = Annotated[str, Field(min_length=1)]
        Strict: TypeAlias = Annotated[Base, Field(min_length=10)]
        
        param = analyze_type(Strict, name="text")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 10, "Last min_length should win"
    
    def test_same_constraint_last_wins_ge(self):
        """Same constraint type - last one wins (ge)."""
        Base: TypeAlias = Annotated[int, Field(ge=0)]
        Strict: TypeAlias = Annotated[Base, Field(ge=10)]
        
        param = analyze_type(Strict, name="value")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        
        assert len(ge_vals) == 1
        assert ge_vals[0] == 10, "Last ge should win"
    
    def test_same_constraint_last_wins_le(self):
        """Same constraint type - last one wins (le)."""
        Base: TypeAlias = Annotated[int, Field(le=100)]
        Strict: TypeAlias = Annotated[Base, Field(le=50)]
        
        param = analyze_type(Strict, name="value")
        
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert len(le_vals) == 1
        assert le_vals[0] == 50, "Last le should win"
    
    def test_same_constraint_last_wins_pattern(self):
        """Same constraint type - last one wins (pattern)."""
        Base: TypeAlias = Annotated[str, Field(pattern=r'^[a-z]+$')]
        Enhanced: TypeAlias = Annotated[Base, Field(pattern=r'^[a-z]{3,}$')]
        
        param = analyze_type(Enhanced, name="text")
        
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        
        assert len(patterns) == 1
        assert patterns[0] == r'^[a-z]{3,}$', "Last pattern should win"
    
    def test_both_ge_and_le_override(self):
        """Can override both ge and le simultaneously."""
        Base: TypeAlias = Annotated[int, Field(ge=0, le=100)]
        Stricter: TypeAlias = Annotated[Base, Field(ge=10, le=90)]
        
        param = analyze_type(Stricter, name="value")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert len(ge_vals) == 1
        assert ge_vals[0] == 10
        assert len(le_vals) == 1
        assert le_vals[0] == 90


class TestStringComposition:
    """Test string type composition scenarios."""
    
    def test_required_string_composition(self):
        """RequiredString has min_length=1."""
        RequiredString: TypeAlias = Annotated[str, Field(min_length=1)]
        
        param = analyze_type(RequiredString, name="text")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 1
    
    def test_short_required_string_composition(self):
        """ShortRequiredString combines min and max."""
        RequiredString: TypeAlias = Annotated[str, Field(min_length=1)]
        ShortRequiredString: TypeAlias = Annotated[RequiredString, Field(max_length=50)]
        
        param = analyze_type(ShortRequiredString, name="text")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 1
        assert len(max_lens) == 1
        assert max_lens[0] == 50
    
    def test_very_short_string_override(self):
        """VeryShortString overrides max_length."""
        ShortString: TypeAlias = Annotated[str, Field(max_length=50)]
        VeryShortString: TypeAlias = Annotated[ShortString, Field(max_length=20)]
        
        param = analyze_type(VeryShortString, name="text")
        
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(max_lens) == 1
        assert max_lens[0] == 20
    
    def test_username_pattern_with_lengths(self):
        """Username has min, max, and pattern."""
        Username: TypeAlias = Annotated[
            str,
            Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
        ]
        
        param = analyze_type(Username, name="username")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 3
        assert len(max_lens) == 1
        assert max_lens[0] == 20
        assert len(patterns) == 1
        assert patterns[0] == r'^[a-zA-Z0-9_]+$'


class TestUIMetadataComposition:
    """Test UI metadata composition - always accumulated, never replaced."""
    
    def test_label_preserved(self):
        """Label is preserved through composition."""
        Base: TypeAlias = Annotated[str, Label("Base Label")]
        
        param = analyze_type(Base, name="field")
        
        assert param.ui is not None
        assert param.ui.label == "Base Label"
    
    def test_multiple_ui_metadata_accumulated(self):
        """Multiple UI metadata types are accumulated."""
        Base: TypeAlias = Annotated[int, Label("Value")]
        Enhanced: TypeAlias = Annotated[Base, Description("Enter a value")]
        
        param = analyze_type(Enhanced, name="field")
        
        assert param.ui is not None
        assert param.ui.label == "Value"
        assert param.ui.description == "Enter a value"
    
    def test_slider_with_label_and_description(self):
        """Slider + Label + Description all work together."""
        PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
        Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]
        PercentageSlider: TypeAlias = Annotated[
            Percentage,
            Slider(),
            Label("Volume"),
            Description("Adjust volume level")
        ]
        
        param = analyze_type(PercentageSlider, name="volume")
        
        assert param.ui is not None
        assert param.ui.is_slider is True
        assert param.ui.label == "Volume"
        assert param.ui.description == "Adjust volume level"
        
        # Check constraints preserved
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        assert ge_vals == [0]
        assert le_vals == [100]
    
    def test_all_ui_metadata_types(self):
        """All UI metadata types can be composed together."""
        Complex: TypeAlias = Annotated[
            str,
            Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z]+$'),
            Label("Full Name"),
            Description("Enter your full name"),
            Placeholder("John Doe"),
            PatternMessage("Only letters allowed"),
            Step(1)
        ]
        
        param = analyze_type(Complex, name="name")
        
        assert param.ui is not None
        assert param.ui.label == "Full Name"
        assert param.ui.description == "Enter your full name"
        assert param.ui.placeholder == "John Doe"
        assert param.ui.pattern_message == "Only letters allowed"
        assert param.ui.step == 1


class TestSpecialTypeInheritance:
    """Test Email and other special types with constraint inheritance."""
    
    def test_email_with_max_length(self):
        """Email with max_length preserves Email pattern and widget type."""
        ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
        
        param = analyze_type(ValidEmail, name="email")
        
        assert param.widget_type == "Email"
        
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(patterns) == 1  # Email pattern
        assert len(max_lens) == 1
        assert max_lens[0] == 254
    
    def test_email_with_min_and_max_length(self):
        """Email with both min and max length."""
        StrictEmail: TypeAlias = Annotated[Email, Field(min_length=5, max_length=100)]
        
        param = analyze_type(StrictEmail, name="email")
        
        assert param.widget_type == "Email"
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(min_lens) == 1
        assert min_lens[0] == 5
        assert len(max_lens) == 1
        assert max_lens[0] == 100
    
    def test_pattern_override_loses_widget_type(self):
        """Overriding pattern loses Email widget type."""
        ValidEmail: TypeAlias = Annotated[Email, Field(max_length=254)]
        WorkEmail: TypeAlias = Annotated[ValidEmail, Field(pattern=r'.*@company\.com$')]
        
        param = analyze_type(WorkEmail, name="work_email")
        
        # Widget type is lost because pattern was overridden
        assert param.widget_type is None
        
        # But constraints are preserved correctly
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        
        assert len(patterns) == 1
        assert patterns[0] == r'.*@company\.com$'  # New pattern, not Email pattern
        assert len(max_lens) == 1
        assert max_lens[0] == 254  # max_length preserved


class TestMultiLevelComposition:
    """Test deeply nested type compositions."""
    
    def test_four_level_composition(self):
        """Four levels of composition work correctly."""
        Level1: TypeAlias = Annotated[int, Field(ge=0)]
        Level2: TypeAlias = Annotated[Level1, Field(le=100)]
        Level3: TypeAlias = Annotated[Level2, Slider()]
        Level4: TypeAlias = Annotated[Level3, Label("Brightness")]
        
        param = analyze_type(Level4, name="brightness")
        
        # All constraints merged
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert ge_vals == [0]
        assert le_vals == [100]
        
        # All UI metadata merged
        assert param.ui is not None
        assert param.ui.is_slider is True
        assert param.ui.label == "Brightness"
    
    def test_multi_level_with_override(self):
        """Multi-level with constraint override."""
        Level1: TypeAlias = Annotated[int, Field(ge=0, le=100)]
        Level2: TypeAlias = Annotated[Level1, Field(ge=10)]  # Override ge
        Level3: TypeAlias = Annotated[Level2, Label("Value")]
        
        param = analyze_type(Level3, name="value")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert ge_vals == [10]  # Overridden
        assert le_vals == [100]  # Preserved
        assert param.ui.label == "Value"
    
    def test_five_level_string_composition(self):
        """Five levels of string composition."""
        Level1: TypeAlias = Annotated[str, Field(min_length=1)]
        Level2: TypeAlias = Annotated[Level1, Field(max_length=100)]
        Level3: TypeAlias = Annotated[Level2, Field(pattern=r'^[A-Z]')]
        Level4: TypeAlias = Annotated[Level3, Label("Name")]
        Level5: TypeAlias = Annotated[Level4, Description("Must start with capital")]
        
        param = analyze_type(Level5, name="name")
        
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        
        assert min_lens == [1]
        assert max_lens == [100]
        assert patterns == [r'^[A-Z]']
        assert param.ui.label == "Name"
        assert param.ui.description == "Must start with capital"


class TestRealWorldScenarios:
    """Test real-world composition patterns."""
    
    def test_percentage_type_library(self):
        """Build Percentage type from PositiveInt."""
        PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
        Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]
        PercentageSlider: TypeAlias = Annotated[Percentage, Slider()]
        
        param = analyze_type(PercentageSlider, name="volume")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert ge_vals == [0]
        assert le_vals == [100]
        assert param.ui.is_slider is True
    
    def test_username_type_with_ui(self):
        """Username with pattern, lengths, and UI."""
        Username: TypeAlias = Annotated[
            str,
            Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
        ]
        LabeledUsername: TypeAlias = Annotated[
            Username,
            Label("Username"),
            Description("3-20 chars, alphanumeric + underscore"),
            Placeholder("Enter username")
        ]
        
        param = analyze_type(LabeledUsername, name="username")
        
        # Constraints
        min_lens = [c.min_length for c in param.constraints.metadata if hasattr(c, 'min_length')]
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        patterns = [c.pattern for c in param.constraints.metadata if hasattr(c, 'pattern')]
        
        assert min_lens == [3]
        assert max_lens == [20]
        assert patterns == [r'^[a-zA-Z0-9_]+$']
        
        # UI
        assert param.ui.label == "Username"
        assert param.ui.description == "3-20 chars, alphanumeric + underscore"
        assert param.ui.placeholder == "Enter username"
    
    def test_validated_email_with_description(self):
        """ValidEmail with constraints and UI."""
        ValidEmail: TypeAlias = Annotated[
            Email,
            Field(max_length=254),
            Description("We'll never share your email")
        ]
        
        param = analyze_type(ValidEmail, name="email")
        
        assert param.widget_type == "Email"
        
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        assert max_lens == [254]
        
        assert param.ui is not None
        assert param.ui.description == "We'll never share your email"
    
    def test_complete_registration_form_types(self):
        """Complete type library for registration form."""
        PositiveInt: TypeAlias = Annotated[int, Field(ge=0)]
        Percentage: TypeAlias = Annotated[PositiveInt, Field(le=100)]
        PercentageSlider: TypeAlias = Annotated[Percentage, Slider()]
        
        Username: TypeAlias = Annotated[
            str,
            Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
            Label("Username"),
            Placeholder("Enter username")
        ]
        
        ValidEmail: TypeAlias = Annotated[
            Email,
            Field(max_length=254),
            Description("We'll never share your email")
        ]
        
        Age: TypeAlias = Annotated[PositiveInt, Field(le=120), Label("Age")]
        
        # Test each type
        username_param = analyze_type(Username, name="username")
        email_param = analyze_type(ValidEmail, name="email")
        age_param = analyze_type(Age, name="age")
        volume_param = analyze_type(PercentageSlider, name="volume")
        
        # Username
        assert username_param.ui.label == "Username"
        assert username_param.ui.placeholder == "Enter username"
        
        # Email
        assert email_param.widget_type == "Email"
        assert email_param.ui.description == "We'll never share your email"
        
        # Age
        age_le = [c.le for c in age_param.constraints.metadata if hasattr(c, 'le')]
        assert age_le == [120]
        assert age_param.ui.label == "Age"
        
        # Volume
        assert volume_param.ui.is_slider is True
        volume_ge = [c.ge for c in volume_param.constraints.metadata if hasattr(c, 'ge')]
        volume_le = [c.le for c in volume_param.constraints.metadata if hasattr(c, 'le')]
        assert volume_ge == [0]
        assert volume_le == [100]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_base_type(self):
        """Base type with no constraints."""
        Base: TypeAlias = str
        Enhanced: TypeAlias = Annotated[Base, Field(max_length=50)]
        
        param = analyze_type(Enhanced, name="text")
        
        max_lens = [c.max_length for c in param.constraints.metadata if hasattr(c, 'max_length')]
        assert max_lens == [50]
    
    def test_multiple_overrides_in_chain(self):
        """Multiple overrides of same constraint."""
        Level1: TypeAlias = Annotated[int, Field(ge=0)]
        Level2: TypeAlias = Annotated[Level1, Field(ge=10)]
        Level3: TypeAlias = Annotated[Level2, Field(ge=20)]
        
        param = analyze_type(Level3, name="value")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        assert ge_vals == [20], "Should have only the last ge value"
    
    def test_constraint_and_ui_together(self):
        """Constraint and UI in same Annotated level."""
        Type: TypeAlias = Annotated[
            int,
            Field(ge=0, le=100),
            Slider(),
            Label("Value")
        ]
        
        param = analyze_type(Type, name="value")
        
        ge_vals = [c.ge for c in param.constraints.metadata if hasattr(c, 'ge')]
        le_vals = [c.le for c in param.constraints.metadata if hasattr(c, 'le')]
        
        assert ge_vals == [0]
        assert le_vals == [100]
        assert param.ui.is_slider is True
        assert param.ui.label == "Value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
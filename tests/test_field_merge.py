import pytest
from typing import Annotated, TypeAlias
from pydantic import Field
from pytypeinput import (
    analyze_function,
    Email,
    Color,
    ImageFile,
    VideoFile,
    AudioFile,
    DataFile,
    TextFile,
    DocumentFile,
    File,
    Slider,
    Label,
    Description,
    Placeholder
)


StrBase: TypeAlias = Annotated[str, Field(min_length=3)]
StrMiddle: TypeAlias = Annotated[StrBase, Field(max_length=20)]
StrTop: TypeAlias = Annotated[StrMiddle, Field(pattern=r'^[a-z]+$')]

IntBase: TypeAlias = Annotated[int, Field(ge=0)]
IntExtended: TypeAlias = Annotated[IntBase, Field(le=100)]

EmailWithLength: TypeAlias = Annotated[Email, Field(max_length=50)]
ValidatedEmail: TypeAlias = Annotated[EmailWithLength, Field(min_length=5)]

SliderBase: TypeAlias = Annotated[int, Field(ge=0)]
SliderExtended: TypeAlias = Annotated[SliderBase, Field(le=100), Slider()]


# ==================== NESTED ANNOTATED FIELD MERGE TESTS ====================

class TestNestedAnnotatedFieldMerge:
    """Tests for merging FieldInfo from nested Annotated types."""
    
    def test_email_preserves_pattern(self):
        """Email special type preserves pattern constraint."""
        def func(email: Email): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        assert len(params[0].constraints.metadata) > 0
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        assert has_pattern
    
    def test_email_with_additional_constraint_merges(self):
        """Email + Field(max_length) merges both constraints."""
        def func(email: Annotated[Email, Field(max_length=50)]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        has_max_length = any(
            hasattr(c, 'max_length') for c in params[0].constraints.metadata
        )
        
        assert has_pattern, "Pattern from Email should be preserved"
        assert has_max_length, "max_length should be added"
    
    def test_email_with_min_max_length_merges(self):
        """Email + min/max length merges all constraints."""
        def func(email: Annotated[Email, Field(min_length=5, max_length=100)]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        has_min = any(
            hasattr(c, 'min_length') for c in params[0].constraints.metadata
        )
        has_max = any(
            hasattr(c, 'max_length') for c in params[0].constraints.metadata
        )
        
        assert has_pattern
        assert has_min
        assert has_max
    
    def test_color_preserves_pattern(self):
        """Color special type preserves pattern constraint."""
        def func(bg_color: Color): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Color"
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        assert has_pattern
    
    def test_color_with_additional_constraint_merges(self):
        """Color + Field constraint merges both."""
        def func(theme: Annotated[Color, Field(min_length=4)]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Color"
        assert params[0].constraints is not None
        
        metadata_count = len(params[0].constraints.metadata)
        assert metadata_count >= 2, "Should have pattern + min_length"
    
    def test_image_file_preserves_pattern(self):
        """ImageFile preserves file pattern constraint."""
        def func(photo: ImageFile): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "ImageFile"
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        assert has_pattern
    
    def test_triple_nested_annotated_merges(self):
        """Triple nested Annotated merges all FieldInfo."""
        def func(value: StrTop): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        
        has_min = any(
            hasattr(c, 'min_length') for c in params[0].constraints.metadata
        )
        has_max = any(
            hasattr(c, 'max_length') for c in params[0].constraints.metadata
        )
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        
        assert has_min
        assert has_max
        assert has_pattern
    
    def test_int_with_multiple_constraints_merges(self):
        """Int with nested Field constraints merges all."""
        def func(age: IntExtended): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        
        has_ge = any(
            hasattr(c, 'ge') for c in params[0].constraints.metadata
        )
        has_le = any(
            hasattr(c, 'le') for c in params[0].constraints.metadata
        )
        
        assert has_ge
        assert has_le
    
    def test_email_list_preserves_widget_type(self):
        """List of Email preserves widget_type."""
        def func(emails: list[Email]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].list is not None
    
    def test_email_list_with_list_constraint_merges(self):
        """List of Email with list-level constraint."""
        def func(emails: Annotated[list[Email], Field(min_length=2)]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].list is not None
        assert params[0].list.constraints is not None
    
    def test_email_list_with_item_constraint_merges(self):
        """List of Email with additional item constraint."""
        def func(emails: list[Annotated[Email, Field(max_length=50)]]): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        has_max = any(
            hasattr(c, 'max_length') for c in params[0].constraints.metadata
        )
        
        assert has_pattern
        assert has_max
    
    def test_email_optional_preserves_widget_type(self):
        """Optional Email preserves widget_type."""
        def func(contact: Email | None = None): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].optional is not None
    
    def test_email_optional_with_constraint_merges(self):
        """Optional Email with additional constraint."""
        def func(email: Annotated[Email, Field(max_length=100)] | None = None): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].optional is not None
        assert params[0].constraints is not None
        
        metadata_count = len(params[0].constraints.metadata)
        assert metadata_count >= 2
    
    def test_complex_combination_all_features(self):
        """Complex: Optional list of Email with all constraints."""
        def func(
            recipients: Annotated[
                list[Annotated[Email, Field(max_length=50)]],
                Field(min_length=1, max_length=10)
            ] | None = None
        ): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].optional is not None
        assert params[0].list is not None
        assert params[0].list.constraints is not None
        assert params[0].constraints is not None
        
        has_pattern = any(
            hasattr(c, 'pattern') for c in params[0].constraints.metadata
        )
        has_item_max = any(
            hasattr(c, 'max_length') for c in params[0].constraints.metadata
        )
        
        assert has_pattern
        assert has_item_max


class TestSpecialTypesIntegration:
    """Integration tests for special types with merged constraints."""
    
    def test_all_special_types_preserve_widget_type(self):
        """All special types preserve their widget_type."""
        def func(
            email: Email,
            color: Color,
            image: ImageFile,
            video: VideoFile,
            audio: AudioFile,
            data: DataFile,
            text: TextFile,
            doc: DocumentFile,
            file: File
        ): pass
        
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[1].widget_type == "Color"
        assert params[2].widget_type == "ImageFile"
        assert params[3].widget_type == "VideoFile"
        assert params[4].widget_type == "AudioFile"
        assert params[5].widget_type == "DataFile"
        assert params[6].widget_type == "TextFile"
        assert params[7].widget_type == "DocumentFile"
        assert params[8].widget_type == "File"
    
    def test_special_types_with_various_constraints(self):
        """Special types work with various Field constraints."""
        def func(
            email: Annotated[Email, Field(max_length=100)],
            short_color: Annotated[Color, Field(min_length=4, max_length=7)]
        ): pass
        
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[1].widget_type == "Color"
        
        assert params[0].constraints is not None
        assert params[1].constraints is not None
    
    def test_deeply_nested_special_type(self):
        """Deeply nested special type annotations work."""
        def func(email: ValidatedEmail): pass
        params = analyze_function(func)
        
        assert params[0].widget_type == "Email"
        assert params[0].constraints is not None
        
        metadata_count = len(params[0].constraints.metadata)
        assert metadata_count >= 3


class TestConstraintMergeEdgeCases:
    """Edge cases for constraint merging."""
    
    def test_no_constraints_returns_none(self):
        """Type without constraints returns None for constraints."""
        def func(name: str): pass
        params = analyze_function(func)
        
        assert params[0].constraints is None
    
    def test_single_constraint_no_merge_needed(self):
        """Single constraint doesn't need merging."""
        def func(age: Annotated[int, Field(ge=0)]): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
    
    def test_empty_field_info_ignored(self):
        """FieldInfo without metadata is handled correctly."""
        def func(value: Annotated[str, Field()]): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
    
    def test_conflicting_constraints_both_preserved(self):
        """Conflicting constraints both preserved (validation will fail later)."""
        def func(
            value: Annotated[
                Annotated[int, Field(ge=10)],
                Field(le=5)
            ]
        ): pass
        params = analyze_function(func)
        
        assert params[0].constraints is not None
        
        has_ge = any(hasattr(c, 'ge') for c in params[0].constraints.metadata)
        has_le = any(hasattr(c, 'le') for c in params[0].constraints.metadata)
        
        assert has_ge
        assert has_le


class TestSliderWithMergedConstraints:
    """Test Slider validation with merged constraints."""
    
    def test_slider_with_merged_constraints_valid(self):
        """Slider works with merged ge/le constraints."""
        def func(volume: SliderExtended): pass
        params = analyze_function(func)
        
        assert params[0].ui.is_slider is True
        assert params[0].constraints is not None
    
    def test_slider_requires_both_min_max_after_merge(self):
        """Slider validation checks merged constraints."""
        def func(volume: Annotated[int, Field(ge=0, le=100), Slider()]): pass
        params = analyze_function(func)
        
        assert params[0].ui.is_slider is True
    
    def test_slider_missing_constraint_fails(self):
        """Slider without min/max fails validation."""
        with pytest.raises(TypeError, match="Slider requires"):
            def func(volume: Annotated[int, Slider()]): pass
            analyze_function(func)


class TestRealWorldScenarios:
    """Real-world scenarios combining all features."""
    
    def test_registration_form_complete(self):
        """Complete registration form with all features."""
        def register_user(
            email: Annotated[
                Email,
                Field(max_length=100),
                Label("Email Address"),
                Placeholder("you@example.com")
            ],
            username: Annotated[
                str,
                Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
                Label("Username"),
                Description("3-20 characters, letters/numbers/underscore only")
            ],
            age: Annotated[
                int,
                Field(ge=18, le=120),
                Label("Age"),
                Description("Must be 18 or older")
            ]
        ): pass
        
        params = analyze_function(register_user)
        
        assert params[0].widget_type == "Email"
        assert params[0].ui.label == "Email Address"
        assert params[0].ui.placeholder == "you@example.com"
        
        assert params[1].ui.label == "Username"
        assert params[1].ui.description is not None
        
        assert params[2].ui.label == "Age"
    
    def test_file_upload_with_constraints(self):
        """File upload with list constraints."""
        def upload_images(
            photos: Annotated[
                list[ImageFile],
                Field(min_length=1, max_length=10)
            ]
        ): pass
        
        params = analyze_function(upload_images)
        
        assert params[0].widget_type == "ImageFile"
        assert params[0].list is not None
        assert params[0].list.constraints is not None
    
    def test_settings_form_with_optionals(self):
        """Settings form with optional fields."""
        def update_settings(
            theme: Annotated[Color, Label("Theme Color")] | None = "#FFFFFF",
            volume: Annotated[
                int,
                Field(ge=0, le=100),
                Slider(),
                Label("Volume")
            ] | None = 50,
            notifications: Annotated[
                list[Email],
                Field(max_length=5),
                Label("Notification Emails")
            ] | None = None
        ): pass
        
        params = analyze_function(update_settings)
        
        assert params[0].widget_type == "Color"
        assert params[0].optional is not None
        
        assert params[1].ui.is_slider is True
        assert params[1].optional is not None
        
        assert params[2].widget_type == "Email"
        assert params[2].optional is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
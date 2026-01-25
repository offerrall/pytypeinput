import pytest
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzer import analyze_function
from pytypeinput.types import (
    Color, Email, ImageFile, VideoFile, AudioFile,
    DataFile, TextFile, DocumentFile, File
)
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestColorType:
    def test_color_basic(self):
        def func(color: Color): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        assert color.param_type == str
        assert color.widget_type == 'Color'
        assert color.constraints is not None
    
    def test_color_with_default(self):
        def func(color: Color = "#FF0000"): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        assert color.widget_type == 'Color'
        assert color.default == "#FF0000"
    
    def test_color_optional(self):
        def func(color: Color | None): pass
        result = analyze_function(func)
        
        color = get_param(result, 'color')
        assert color.widget_type == 'Color'
        assert color.optional is not None
    
    def test_color_list(self):
        def func(colors: list[Color]): pass
        result = analyze_function(func)
        
        colors = get_param(result, 'colors')
        assert colors.widget_type == 'Color'
        assert colors.list is not None


class TestEmailType:
    def test_email_basic(self):
        def func(email: Email): pass
        result = analyze_function(func)
        
        email = get_param(result, 'email')
        assert email.param_type == str
        assert email.widget_type == 'Email'
        assert email.constraints is not None
    
    def test_email_with_default(self):
        def func(email: Email = "test@example.com"): pass
        result = analyze_function(func)
        
        email = get_param(result, 'email')
        assert email.widget_type == 'Email'
        assert email.default == "test@example.com"
    
    def test_email_optional(self):
        def func(email: Email | None = None): pass
        result = analyze_function(func)
        
        email = get_param(result, 'email')
        assert email.widget_type == 'Email'
        assert email.optional.enabled is False
    
    def test_email_list(self):
        def func(emails: list[Email]): pass
        result = analyze_function(func)
        
        emails = get_param(result, 'emails')
        assert emails.widget_type == 'Email'
        assert emails.list is not None


class TestImageFileType:
    def test_image_file_basic(self):
        def func(image: ImageFile): pass
        result = analyze_function(func)
        
        image = get_param(result, 'image')
        assert image.param_type == str
        assert image.widget_type == 'ImageFile'
        assert image.constraints is not None
    
    def test_image_file_optional(self):
        def func(image: ImageFile | None): pass
        result = analyze_function(func)
        
        image = get_param(result, 'image')
        assert image.widget_type == 'ImageFile'
        assert image.optional is not None
    
    def test_image_file_list(self):
        def func(images: list[ImageFile]): pass
        result = analyze_function(func)
        
        images = get_param(result, 'images')
        assert images.widget_type == 'ImageFile'
        assert images.list is not None


class TestVideoFileType:
    def test_video_file_basic(self):
        def func(video: VideoFile): pass
        result = analyze_function(func)
        
        video = get_param(result, 'video')
        assert video.param_type == str
        assert video.widget_type == 'VideoFile'
        assert video.constraints is not None
    
    def test_video_file_optional(self):
        def func(video: VideoFile | None): pass
        result = analyze_function(func)
        
        video = get_param(result, 'video')
        assert video.widget_type == 'VideoFile'
        assert video.optional is not None


class TestAudioFileType:
    def test_audio_file_basic(self):
        def func(audio: AudioFile): pass
        result = analyze_function(func)
        
        audio = get_param(result, 'audio')
        assert audio.param_type == str
        assert audio.widget_type == 'AudioFile'
        assert audio.constraints is not None
    
    def test_audio_file_optional(self):
        def func(audio: AudioFile | None): pass
        result = analyze_function(func)
        
        audio = get_param(result, 'audio')
        assert audio.widget_type == 'AudioFile'
        assert audio.optional is not None


class TestDataFileType:
    def test_data_file_basic(self):
        def func(data: DataFile): pass
        result = analyze_function(func)
        
        data = get_param(result, 'data')
        assert data.param_type == str
        assert data.widget_type == 'DataFile'
        assert data.constraints is not None
    
    def test_data_file_list(self):
        def func(files: list[DataFile]): pass
        result = analyze_function(func)
        
        files = get_param(result, 'files')
        assert files.widget_type == 'DataFile'
        assert files.list is not None


class TestTextFileType:
    def test_text_file_basic(self):
        def func(text: TextFile): pass
        result = analyze_function(func)
        
        text = get_param(result, 'text')
        assert text.param_type == str
        assert text.widget_type == 'TextFile'
        assert text.constraints is not None
    
    def test_text_file_optional(self):
        def func(text: TextFile | None): pass
        result = analyze_function(func)
        
        text = get_param(result, 'text')
        assert text.widget_type == 'TextFile'
        assert text.optional is not None


class TestDocumentFileType:
    def test_document_file_basic(self):
        def func(doc: DocumentFile): pass
        result = analyze_function(func)
        
        doc = get_param(result, 'doc')
        assert doc.param_type == str
        assert doc.widget_type == 'DocumentFile'
        assert doc.constraints is not None
    
    def test_document_file_list(self):
        def func(docs: list[DocumentFile]): pass
        result = analyze_function(func)
        
        docs = get_param(result, 'docs')
        assert docs.widget_type == 'DocumentFile'
        assert docs.list is not None


class TestGenericFileType:
    def test_file_basic(self):
        def func(file: File): pass
        result = analyze_function(func)
        
        file = get_param(result, 'file')
        assert file.param_type == str
        assert file.widget_type == 'File'
        assert file.constraints is not None
    
    def test_file_list(self):
        def func(files: list[File]): pass
        result = analyze_function(func)
        
        files = get_param(result, 'files')
        assert files.widget_type == 'File'
        assert files.list is not None
    
    def test_file_optional(self):
        def func(file: File | None): pass
        result = analyze_function(func)
        
        file = get_param(result, 'file')
        assert file.widget_type == 'File'
        assert file.optional is not None


class TestNonSpecialTypes:
    def test_regular_str_no_special_type(self):
        def func(name: str): pass
        result = analyze_function(func)
        
        name = get_param(result, 'name')
        assert name.param_type == str
        assert name.widget_type is None
        assert name.constraints is None
    
    def test_custom_pattern_no_special_type(self):
        def func(code: Annotated[str, Field(pattern=r'^[A-Z]{3}-\d{3}$')]): pass
        result = analyze_function(func)
        
        code = get_param(result, 'code')
        assert code.param_type == str
        assert code.widget_type is None
        assert code.constraints is not None
    
    def test_str_with_length_no_special_type(self):
        def func(username: Annotated[str, Field(min_length=3, max_length=20)]): pass
        result = analyze_function(func)
        
        username = get_param(result, 'username')
        assert username.widget_type is None
        assert username.constraints is not None
    
    def test_int_no_special_type(self):
        def func(age: int): pass
        result = analyze_function(func)
        
        age = get_param(result, 'age')
        assert age.param_type == int
        assert age.widget_type is None
    
    def test_bool_no_special_type(self):
        def func(active: bool): pass
        result = analyze_function(func)
        
        active = get_param(result, 'active')
        assert active.param_type == bool
        assert active.widget_type is None


class TestMultipleSpecialTypes:
    def test_all_special_types_together(self):
        def func(
            color: Color,
            email: Email,
            image: ImageFile,
            video: VideoFile,
            audio: AudioFile,
            data: DataFile,
            text: TextFile,
            doc: DocumentFile,
            file: File
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'color').widget_type == 'Color'
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'image').widget_type == 'ImageFile'
        assert get_param(result, 'video').widget_type == 'VideoFile'
        assert get_param(result, 'audio').widget_type == 'AudioFile'
        assert get_param(result, 'data').widget_type == 'DataFile'
        assert get_param(result, 'text').widget_type == 'TextFile'
        assert get_param(result, 'doc').widget_type == 'DocumentFile'
        assert get_param(result, 'file').widget_type == 'File'
    
    def test_mixed_special_and_regular(self):
        def func(
            name: str,
            email: Email,
            age: int,
            photo: ImageFile,
            active: bool
        ): pass
        result = analyze_function(func)
        
        assert get_param(result, 'name').widget_type is None
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'age').widget_type is None
        assert get_param(result, 'photo').widget_type == 'ImageFile'
        assert get_param(result, 'active').widget_type is None


class TestSpecialTypesWithConstraints:
    def test_color_with_default(self):
        def func(bg_color: Color = "#FFFFFF"): pass
        result = analyze_function(func)
        
        bg_color = get_param(result, 'bg_color')
        assert bg_color.widget_type == 'Color'
        assert bg_color.default == "#FFFFFF"
    
    def test_email_optional_with_default(self):
        def func(contact: Email | None = "default@example.com"): pass
        result = analyze_function(func)
        
        contact = get_param(result, 'contact')
        assert contact.widget_type == 'Email'
        assert contact.optional.enabled is True
        assert contact.default == "default@example.com"
    
    def test_image_list_optional(self):
        def func(gallery: list[ImageFile] | None): pass
        result = analyze_function(func)
        
        gallery = get_param(result, 'gallery')
        assert gallery.widget_type == 'ImageFile'
        assert gallery.list is not None
        assert gallery.optional is not None


class TestSpecialTypesEdgeCases:
    def test_file_list_with_default(self):
        def func(attachments: list[File] = []): pass
        result = analyze_function(func)
        
        attachments = get_param(result, 'attachments')
        assert attachments.widget_type == 'File'
        assert attachments.list is not None
        assert attachments.default is None
    
    def test_color_list_with_values(self):
        def func(palette: list[Color] = ["#FF0000", "#00FF00"]): pass
        result = analyze_function(func)
        
        palette = get_param(result, 'palette')
        assert palette.widget_type == 'Color'
        assert palette.list is not None
        assert palette.default == ["#FF0000", "#00FF00"]
    
    def test_multiple_emails_list(self):
        def func(recipients: list[Email]): pass
        result = analyze_function(func)
        
        recipients = get_param(result, 'recipients')
        assert recipients.widget_type == 'Email'
        assert recipients.list is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
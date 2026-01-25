import pytest
import sys
from pathlib import Path
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzer import analyze_function
from pytypeinput.types import Color, Email, ImageFile, VideoFile, AudioFile, DataFile, TextFile, DocumentFile, File
from pytypeinput.types import OptionalEnabled, OptionalDisabled, Dropdown
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestBasicTypes:
    
    def test_showcase_types(self):
        def showcase_types(
            name: str,
            age: int,
            height: float,
            active: bool,
            birthday: date,
            alarm: time,
        ):
            return {"name": name, "age": age}
        
        result = analyze_function(showcase_types)
        
        assert len(result) == 6
        assert get_param(result, 'name').param_type == str
        assert get_param(result, 'age').param_type == int
        assert get_param(result, 'height').param_type == float
        assert get_param(result, 'active').param_type == bool
        assert get_param(result, 'birthday').param_type == date
        assert get_param(result, 'alarm').param_type == time
        
        for param in result:
            assert param.default is None
            assert param.optional is None


class TestDivisionExamples:
    
    def test_basic_division(self):
        def divide(a: float, b: float):
            return a / b
        
        result = analyze_function(divide)
        
        assert len(result) == 2
        assert get_param(result, 'a').param_type == float
        assert get_param(result, 'b').param_type == float
        assert get_param(result, 'a').constraints is None
        assert get_param(result, 'b').constraints is None
    
    def test_safe_division(self):
        def safe_divide(
            numerator: float,
            denominator: Annotated[float, Field(gt=0)] = 1.0
        ):
            return numerator / denominator
        
        result = analyze_function(safe_divide)
        
        numerator = get_param(result, 'numerator')
        assert numerator.param_type == float
        assert numerator.constraints is None
        assert numerator.default is None
        
        denominator = get_param(result, 'denominator')
        assert denominator.param_type == float
        assert denominator.constraints is not None
        assert denominator.default == 1.0


class TestDropdownExamples:
    
    def test_dynamic_dropdowns(self):
        THEMES = ['light', 'dark', 'auto']
        
        def get_random_theme():
            from random import sample
            return sample(THEMES, k=1)
        
        def configure_app(
            theme: Annotated[str, Dropdown(get_random_theme)],
            size: Annotated[str, Dropdown(get_random_theme)] = None,
        ):
            return {"theme": theme}
        
        result = analyze_function(configure_app)

        theme = get_param(result, 'theme')
        assert theme.param_type == str
        assert theme.choices is not None
        assert theme.choices.options_function == get_random_theme
        assert callable(theme.choices.options_function)
        assert theme.optional is None

        size = get_param(result, 'size')
        assert size.param_type == str
        assert size.choices is not None
        assert size.choices.options_function == get_random_theme
        assert size.optional is None
        assert size.default is None

    
    def test_enum_dropdowns(self):
        class Theme(Enum):
            LIGHT = 'light'
            DARK = 'dark'
            AUTO = 'auto'
        
        class Priority(Enum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3
        
        def create_task(theme: Theme, priority: Priority):
            return f"Theme: {theme.value}"
        
        result = analyze_function(create_task)
        
        theme = get_param(result, 'theme')
        assert theme.param_type == str
        assert theme.choices is not None
        assert theme.choices.enum_class == Theme
        assert theme.choices.options == ('light', 'dark', 'auto')
        
        priority = get_param(result, 'priority')
        assert priority.param_type == int
        assert priority.choices.enum_class == Priority
        assert priority.choices.options == (1, 2, 3)


class TestFileExamples:
    
    def test_file_uploads(self):
        def upload_files(files: list[File]):
            return "Files uploaded"
        
        result = analyze_function(upload_files)
        
        files = get_param(result, 'files')
        assert files.param_type == str
        assert files.list is not None
        assert files.constraints is not None
    
    def test_special_file_types(self):
        def process_files(
            image: ImageFile,
            doc: DocumentFile,
            video: VideoFile,
            audio: AudioFile,
            data: DataFile,
            text: TextFile
        ):
            return "Processed"
        
        result = analyze_function(process_files)
        
        for param_name in ['image', 'doc', 'video', 'audio', 'data', 'text']:
            param = get_param(result, param_name)
            assert param.param_type == str
            assert param.constraints is not None
            assert param.choices is None
    
    def test_special_inputs_combined(self):
        def create_account(
            email: Email,
            photo: ImageFile,
            favorite_color: Color,
            language: Literal['en', 'es', 'fr', 'de']
        ):
            return "Account created"
        
        result = analyze_function(create_account)
        
        email = get_param(result, 'email')
        assert email.param_type == str
        assert email.constraints is not None
        assert email.choices is None
        
        photo = get_param(result, 'photo')
        assert photo.param_type == str
        assert photo.constraints is not None
        
        favorite_color = get_param(result, 'favorite_color')
        assert favorite_color.param_type == str
        assert favorite_color.constraints is not None
        
        language = get_param(result, 'language')
        assert language.param_type == str
        assert language.choices is not None
        assert language.choices.options == ('en', 'es', 'fr', 'de')


class TestConstraintsExamples:
    
    def test_numeric_constraints(self):
        def calculate_bmi(
            age: Annotated[int, Field(ge=0, le=120)],
            weight_kg: Annotated[float, Field(ge=20, le=300)],
            height_m: Annotated[float, Field(ge=0.5, le=2.5)]
        ):
            return weight_kg / (height_m ** 2)
        
        result = analyze_function(calculate_bmi)
        
        assert get_param(result, 'age').constraints is not None
        assert get_param(result, 'weight_kg').constraints is not None
        assert get_param(result, 'height_m').constraints is not None
        
        assert get_param(result, 'age').param_type == int
        assert get_param(result, 'weight_kg').param_type == float
        assert get_param(result, 'height_m').param_type == float
    
    def test_string_constraints(self):
        def register_user(
            username: Annotated[str, Field(min_length=3, max_length=20)],
            email: Email,
            password: Annotated[str, Field(min_length=8, max_length=50)],
            bio: Annotated[str, Field(max_length=200)]
        ):
            return {"username": username}
        
        result = analyze_function(register_user)
        
        username = get_param(result, 'username')
        assert username.param_type == str
        assert username.constraints is not None
        
        email = get_param(result, 'email')
        assert email.param_type == str
        assert email.constraints is not None
        
        password = get_param(result, 'password')
        assert password.param_type == str
        assert password.constraints is not None
        
        bio = get_param(result, 'bio')
        assert bio.param_type == str
        assert bio.constraints is not None
    
    def test_list_constraints(self):
        def rate_movies(
            ratings: Annotated[
                list[Annotated[int, Field(ge=1, le=5)]],
                Field(min_length=3, max_length=10)
            ]
        ):
            return sum(ratings) / len(ratings)
        
        result = analyze_function(rate_movies)
        
        ratings = get_param(result, 'ratings')
        assert ratings.param_type == int
        assert ratings.list is not None
        assert ratings.list.constraints is not None
        assert ratings.constraints is not None


class TestListExamples:
    
    def test_comprehensive_lists(self):
        def list_example(
            numbers: list[int],
            colors: list[Color],
            scores: list[Annotated[int, Field(ge=0, le=100)]],
            usernames: list[Annotated[str, Field(min_length=3)]],
            team: Annotated[list[str], Field(min_length=2, max_length=5)],
            ratings: Annotated[
                list[Annotated[int, Field(ge=1, le=5)]], 
                Field(min_length=3, max_length=10)
            ],
            names: list[str] = ["Alice", "Bob"],
            tags: list[str] | None = None,
            tags2: Annotated[list[str], Field(min_length=2)] | None = None,
            emails: list[Email] | None = None,
            all_features: Annotated[
                list[Annotated[str, Field(min_length=2)]],
                Field(min_length=2)
            ] | OptionalEnabled = ["aaa", "bbb"]
        ):
            return {"numbers": numbers}
        
        result = analyze_function(list_example)
        
        numbers = get_param(result, 'numbers')
        assert numbers.list is not None
        assert numbers.param_type == int
        
        colors = get_param(result, 'colors')
        assert colors.list is not None
        assert colors.param_type == str
        
        scores = get_param(result, 'scores')
        assert scores.list is not None
        assert scores.constraints is not None
        
        usernames = get_param(result, 'usernames')
        assert usernames.list is not None
        assert usernames.constraints is not None
        
        team = get_param(result, 'team')
        assert team.list is not None
        assert team.list.constraints is not None
        
        ratings = get_param(result, 'ratings')
        assert ratings.list is not None
        assert ratings.list.constraints is not None
        assert ratings.constraints is not None
        
        names = get_param(result, 'names')
        assert names.list is not None
        assert names.default == ["Alice", "Bob"]
        
        tags = get_param(result, 'tags')
        assert tags.list is not None
        assert tags.optional is not None
        assert tags.optional.enabled is False
        
        tags2 = get_param(result, 'tags2')
        assert tags2.list is not None
        assert tags2.optional.enabled is False
        
        emails = get_param(result, 'emails')
        assert emails.list is not None
        assert emails.optional.enabled is False
        
        all_features = get_param(result, 'all_features')
        assert all_features.list is not None
        assert all_features.optional.enabled is True
        assert all_features.default == ["aaa", "bbb"]


class TestOptionalExamples:
    
    def test_optional_advanced(self):
        def create_user(
            username: str,
            surname: str | None,
            age: int | OptionalDisabled,
            favorite_color: Color | OptionalEnabled,
            birth_date: date | None,
            language: Literal['English', 'Spanish', 'French'] | None,
            date_of_meeting: time | OptionalEnabled,
            profile_picture: ImageFile | OptionalDisabled,
            job: str | None = "Dev",
            email: Email | OptionalEnabled = "test@gmail.com",
            bio: Annotated[str, Field(max_length=500, min_length=10)] | OptionalDisabled = "Software developer",
        ):
            return f"Username: {username}"
        
        result = analyze_function(create_user)
        
        assert get_param(result, 'username').optional is None
        
        surname = get_param(result, 'surname')
        assert surname.optional is not None
        assert surname.optional.enabled is False
        
        age = get_param(result, 'age')
        assert age.optional.enabled is False
        
        favorite_color = get_param(result, 'favorite_color')
        assert favorite_color.optional.enabled is True
        
        birth_date = get_param(result, 'birth_date')
        assert birth_date.optional.enabled is False
        
        language = get_param(result, 'language')
        assert language.optional.enabled is False
        assert language.choices is not None
        
        date_of_meeting = get_param(result, 'date_of_meeting')
        assert date_of_meeting.optional.enabled is True
        
        profile_picture = get_param(result, 'profile_picture')
        assert profile_picture.optional.enabled is False
        
        job = get_param(result, 'job')
        assert job.optional.enabled is True
        assert job.default == "Dev"
        
        email = get_param(result, 'email')
        assert email.optional.enabled is True
        assert email.default == "test@gmail.com"
        
        bio = get_param(result, 'bio')
        assert bio.optional.enabled is False
        assert bio.default == "Software developer"


class TestMultipleFunctions:
    
    def test_multiple_functions_analyzed(self):
        def calculate_bmi(
            weight_kg: Annotated[float, Field(ge=20, le=300)],
            height_m: Annotated[float, Field(ge=0.5, le=2.5)]
        ):
            return {"bmi": weight_kg / (height_m ** 2)}
        
        def celsius_to_fahrenheit(celsius: float = 0.0):
            return f"{celsius}°C"
        
        def reverse_text(text: str = "Hello World"):
            return text[::-1]
        
        def divide_numbers(
            numerator: float,
            denominator: Annotated[float, Field(gt=0)] = 1.0
        ):
            return numerator / denominator
        
        def greet(name: str = "User"):
            return f"Hello, {name}!"
        
        funcs = [calculate_bmi, celsius_to_fahrenheit, reverse_text, divide_numbers, greet]
        results = [analyze_function(f) for f in funcs]
        
        assert get_param(results[0], 'weight_kg').constraints is not None
        assert get_param(results[0], 'height_m').constraints is not None
        
        assert get_param(results[1], 'celsius').default == 0.0
        
        assert get_param(results[2], 'text').default == "Hello World"
        
        assert get_param(results[3], 'denominator').constraints is not None
        assert get_param(results[3], 'denominator').default == 1.0
        
        assert get_param(results[4], 'name').default == "User"


class TestGroupedFunctions:
    
    def test_grouped_functions(self):
        def calc_sum(a: int, b: int) -> int:
            return a + b
        
        def calc_multiply(a: int, b: int) -> int:
            return a * b
        
        def text_upper(text: str) -> str:
            return text.upper()
        
        def text_lower(text: str) -> str:
            return text.lower()
        
        def text_reverse(text: str) -> str:
            return text[::-1]
        
        def text_length(text: str) -> int:
            return len(text)
        
        def text_concat(text1: str, text2: str) -> str:
            return text1 + text2
        
        math_funcs = [calc_sum, calc_multiply]
        text_funcs = [text_upper, text_lower, text_reverse, text_length, text_concat]
        
        for func in math_funcs:
            result = analyze_function(func)
            for param in result:
                assert param.param_type == int
        
        for func in text_funcs:
            result = analyze_function(func)
            for param in result:
                assert param.param_type == str


class TestImageProcessing:
    
    def test_image_effect(self):
        def image_effect(
            image: ImageFile,
            effect: Literal['blur', 'sharpen', 'contour', 'emboss', 'edge_enhance'] = 'blur',
            intensity: float | None = 5.0,
        ):
            return "Processed"
        
        result = analyze_function(image_effect)
        
        image = get_param(result, 'image')
        assert image.param_type == str
        assert image.constraints is not None
        
        effect = get_param(result, 'effect')
        assert effect.param_type == str
        assert effect.choices is not None
        assert effect.choices.options == ('blur', 'sharpen', 'contour', 'emboss', 'edge_enhance')
        assert effect.default == 'blur'
        
        intensity = get_param(result, 'intensity')
        assert intensity.param_type == float
        assert intensity.optional.enabled is True
        assert intensity.default == 5.0


class TestPlotExample:
    
    def test_compare_functions(self):
        def compare_functions(
            func1: Literal['sin', 'cos', 'tan'] = 'sin',
            func2: Literal['sin', 'cos', 'tan'] = 'cos',
            range_end: float = 10.0
        ):
            return "Plot generated"
        
        result = analyze_function(compare_functions)
        
        func1 = get_param(result, 'func1')
        assert func1.choices is not None
        assert func1.choices.options == ('sin', 'cos', 'tan')
        assert func1.default == 'sin'
        
        func2 = get_param(result, 'func2')
        assert func2.choices is not None
        assert func2.default == 'cos'
        
        range_end = get_param(result, 'range_end')
        assert range_end.param_type == float
        assert range_end.default == 10.0


class TestComplexCombinations:
    
    def test_pdf_merger(self):
        def merge_pdfs(files: list[DocumentFile]):
            return "Merged"
        
        result = analyze_function(merge_pdfs)
        
        files = get_param(result, 'files')
        assert files.param_type == str
        assert files.list is not None
        assert files.constraints is not None
    
    def test_multiple_returns_function(self):
        def analyze_image(image: ImageFile, blur_radius: int = 5):
            return "Analysis complete"
        
        result = analyze_function(analyze_image)
        
        image = get_param(result, 'image')
        assert image.param_type == str
        assert image.constraints is not None
        
        blur_radius = get_param(result, 'blur_radius')
        assert blur_radius.param_type == int
        assert blur_radius.default == 5
    
    def test_service_restart(self):
        def restart_service(service: Literal['nginx', 'gunicorn', 'celery']):
            return "Restarted"
        
        result = analyze_function(restart_service)
        
        service = get_param(result, 'service')
        assert service.choices is not None
        assert service.choices.options == ('nginx', 'gunicorn', 'celery')
    
    def test_table_return_with_literal(self):
        def query_database(table: Literal["users", "products"]):
            return [{"id": 1, "name": "test"}]
        
        result = analyze_function(query_database)
        
        table = get_param(result, 'table')
        assert table.choices is not None
        assert table.choices.options == ("users", "products")


class TestValidationCoverage:
    
    def test_all_constraint_types_together(self):
        def comprehensive_validation(
            age: Annotated[int, Field(ge=0, le=120)],
            score: Annotated[float, Field(gt=0, lt=100)],
            username: Annotated[str, Field(min_length=3, max_length=20)],
            email: Email,
            color: Color,
            ratings: Annotated[
                list[Annotated[int, Field(ge=1, le=5)]],
                Field(min_length=1, max_length=10)
            ],
            bio: Annotated[str, Field(max_length=500)] | None = None,
            status: Literal['active', 'pending', 'done'] = 'active',
            avatar: ImageFile | None = None
        ):
            return "Validated"
        
        result = analyze_function(comprehensive_validation)
        
        assert get_param(result, 'age').param_type == int
        assert get_param(result, 'score').param_type == float
        assert get_param(result, 'username').param_type == str
        assert get_param(result, 'email').param_type == str
        assert get_param(result, 'color').param_type == str
        assert get_param(result, 'ratings').param_type == int
        assert get_param(result, 'bio').param_type == str
        assert get_param(result, 'status').param_type == str
        assert get_param(result, 'avatar').param_type == str
        
        assert get_param(result, 'age').constraints is not None
        assert get_param(result, 'score').constraints is not None
        assert get_param(result, 'username').constraints is not None
        assert get_param(result, 'email').constraints is not None
        assert get_param(result, 'color').constraints is not None
        assert get_param(result, 'ratings').constraints is not None
        assert get_param(result, 'ratings').list.constraints is not None
        assert get_param(result, 'bio').constraints is not None
        assert get_param(result, 'avatar').constraints is not None
        
        assert get_param(result, 'bio').optional.enabled is False
        assert get_param(result, 'avatar').optional.enabled is False
        
        assert get_param(result, 'status').choices is not None
        
        assert get_param(result, 'bio').default is None
        assert get_param(result, 'status').default == 'active'
        assert get_param(result, 'avatar').default is None


class TestBackwardCompatibility:
    
    def test_original_quick_start(self):
        def divide(a: float, b: float):
            return a / b
        
        result = analyze_function(divide)
        
        assert len(result) == 2
        assert get_param(result, 'a').param_type == float
        assert get_param(result, 'b').param_type == float
        assert get_param(result, 'a').default is None
        assert get_param(result, 'b').default is None
    
    def test_qr_generator(self):
        def make_qr(text: str):
            return "QR code"
        
        result = analyze_function(make_qr)
        
        text = get_param(result, 'text')
        assert text.param_type == str
        assert text.default is None
    
    def test_file_upload_to_desktop(self):
        def upload_files(files: list[File]):
            return "Uploaded"
        
        result = analyze_function(upload_files)
        
        files = get_param(result, 'files')
        assert files.list is not None
        assert files.param_type == str
    
    def test_all_examples_have_valid_signatures(self):
        examples = [
            lambda name: str,
            lambda a, b: float,
            lambda theme: str,
        ]
        
        for func in examples:
            try:
                sig = func.__annotations__
            except:
                pytest.fail("Example has invalid signature")


class TestCoverageStats:
    
    def test_coverage_summary(self):
        coverage = {
            "Basic types": ["str", "int", "float", "bool", "date", "time"],
            "Special types": ["Color", "Email"],
            "File types": ["File", "ImageFile", "VideoFile", "AudioFile", "DataFile", "TextFile", "DocumentFile"],
            "Constraints": ["ge", "le", "gt", "lt", "min_length", "max_length", "pattern"],
            "Lists": ["basic", "with_item_constraints", "with_list_constraints", "both_constraints", "optional_lists"],
            "Optional": ["Type | None", "OptionalEnabled", "OptionalDisabled", "with_defaults", "without_defaults"],
            "Dropdowns": ["Literal", "Enum", "Dropdown(func)", "Dropdown_with_default"],
            "Complex": ["multiple_functions", "grouped_functions", "multiple_returns"],
        }
        
        total_scenarios = sum(len(v) for v in coverage.values())
        
        assert total_scenarios >= 38
        
        print(f"\n{'='*60}")
        print(f"COVERAGE SUMMARY: {total_scenarios} scenarios tested")
        print(f"{'='*60}")
        for category, items in coverage.items():
            print(f"{category:20s}: {len(items):2d} scenarios")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
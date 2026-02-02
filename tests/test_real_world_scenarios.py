import pytest
import sys
from pathlib import Path
from typing import Annotated, Literal
from enum import Enum
from datetime import date, time

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytypeinput.analyzers import analyze_function
from pytypeinput.types import Color, Email, ImageFile, OptionalEnabled, OptionalDisabled
from pydantic import Field


def get_param(result, name):
    for param in result:
        if param.name == name:
            return param
    raise KeyError(f"Parameter '{name}' not found")


class TestRealWorldAPIFunctions:
    
    def test_user_registration_form(self):
        def register_user(
            email: Email,
            password: Annotated[str, Field(min_length=8, max_length=100)],
            username: Annotated[str, Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')],
            age: Annotated[int, Field(ge=13, le=120)],
            country: Literal['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'ES', 'IT', 'JP', 'CN'],
            newsletter: bool = False,
            referral_code: Annotated[str, Field(pattern=r'^[A-Z0-9]{6}$')] | None = None
        ):
            return {"success": True}
        
        result = analyze_function(register_user)
        
        assert len(result) == 7
        assert get_param(result, 'email').widget_type == 'Email'
        assert get_param(result, 'password').constraints is not None
        assert get_param(result, 'username').constraints is not None
        assert get_param(result, 'age').constraints is not None
        
        country = get_param(result, 'country')
        assert country.choices is not None
        assert len(country.choices.options) == 10
        
        assert get_param(result, 'newsletter').default is False
        assert get_param(result, 'referral_code').optional.enabled is False
    
    def test_ecommerce_order_function(self):
        class PaymentMethod(Enum):
            CREDIT_CARD = 'credit_card'
            PAYPAL = 'paypal'
            BANK_TRANSFER = 'bank_transfer'
        
        class ShippingSpeed(Enum):
            STANDARD = 'standard'
            EXPRESS = 'express'
            OVERNIGHT = 'overnight'
        
        def create_order(
            items: Annotated[list[str], Field(min_length=1, max_length=50)],
            payment_method: PaymentMethod,
            shipping_speed: ShippingSpeed = ShippingSpeed.STANDARD,
            coupon_code: Annotated[str, Field(pattern=r'^[A-Z0-9]{8}$')] | None = None,
            gift_message: Annotated[str, Field(max_length=200)] | None = None,
            gift_wrap: bool = False
        ):
            return {"order_id": "12345"}
        
        result = analyze_function(create_order)
        
        assert get_param(result, 'items').list is not None
        assert get_param(result, 'payment_method').choices.enum_class == PaymentMethod
        assert get_param(result, 'shipping_speed').default == 'standard'
        assert get_param(result, 'coupon_code').optional.enabled is False
        assert get_param(result, 'gift_wrap').default is False
    
    def test_content_moderation_function(self):
        class ContentType(Enum):
            TEXT = 'text'
            IMAGE = 'image'
            VIDEO = 'video'
        
        def moderate_content(
            content_type: ContentType,
            text_content: Annotated[str, Field(max_length=10000)] | None = None,
            image_content: ImageFile | None = None,
            severity_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.8,
            auto_flag: bool = True,
            tags: list[str] | None = None
        ):
            return {"status": "reviewed"}
        
        result = analyze_function(moderate_content)
        
        assert get_param(result, 'content_type').choices.enum_class == ContentType
        assert get_param(result, 'text_content').optional.enabled is False
        assert get_param(result, 'image_content').widget_type == 'ImageFile'
        assert get_param(result, 'severity_threshold').default == 0.8
        assert get_param(result, 'auto_flag').default is True


class TestDataProcessingFunctions:
    
    def test_data_filtering_function(self):
        def filter_dataset(
            columns: list[str],
            start_date: date | None = None,
            end_date: date | None = None,
            min_value: float | None = None,
            max_value: float | None = None,
            include_nulls: bool = False,
            sort_by: Literal['date', 'value', 'name'] = 'date',
            ascending: bool = True,
            limit: Annotated[int, Field(ge=1, le=10000)] = 100
        ):
            return {"filtered_rows": 42}
        
        result = analyze_function(filter_dataset)
        
        assert get_param(result, 'columns').list is not None
        assert get_param(result, 'start_date').optional.enabled is False
        assert get_param(result, 'sort_by').choices.options == ('date', 'value', 'name')
        assert get_param(result, 'limit').default == 100
    
    def test_ml_model_training_function(self):
        class Algorithm(Enum):
            LINEAR_REGRESSION = 'linear_regression'
            RANDOM_FOREST = 'random_forest'
            NEURAL_NETWORK = 'neural_network'
        
        def train_model(
            algorithm: Algorithm,
            training_data: list[str],
            test_split: Annotated[float, Field(gt=0.0, lt=1.0)] = 0.2,
            max_iterations: Annotated[int, Field(ge=1, le=10000)] = 1000,
            learning_rate: Annotated[float, Field(gt=0.0, le=1.0)] = 0.01,
            early_stopping: bool = True,
            validation_metric: Literal['accuracy', 'precision', 'recall', 'f1'] = 'accuracy'
        ):
            return {"model_id": "model_123"}
        
        result = analyze_function(train_model)
        
        assert get_param(result, 'algorithm').choices.enum_class == Algorithm
        assert get_param(result, 'test_split').default == 0.2
        assert get_param(result, 'validation_metric').choices is not None


class TestReportGenerationFunctions:
    
    def test_sales_report_generator(self):
        class ReportFormat(Enum):
            PDF = 'pdf'
            EXCEL = 'excel'
            CSV = 'csv'
        
        class TimePeriod(Enum):
            DAILY = 'daily'
            WEEKLY = 'weekly'
            MONTHLY = 'monthly'
            QUARTERLY = 'quarterly'
            YEARLY = 'yearly'
        
        def generate_sales_report(
            start_date: date,
            end_date: date,
            period: TimePeriod,
            output_format: ReportFormat = ReportFormat.PDF,
            include_charts: bool = True,
            regions: list[str] | None = None,
            products: list[str] | None = None,
            email_to: Email | None = None
        ):
            return {"report_url": "https://..."}
        
        result = analyze_function(generate_sales_report)
        
        assert get_param(result, 'start_date').param_type == date
        assert get_param(result, 'period').choices.enum_class == TimePeriod
        assert get_param(result, 'output_format').default == 'pdf'
        assert get_param(result, 'include_charts').default is True


class TestFormBuilderFunctions:
    
    def test_create_survey_question(self):
        class QuestionType(Enum):
            MULTIPLE_CHOICE = 'multiple_choice'
            TEXT = 'text'
            RATING = 'rating'
            YES_NO = 'yes_no'
            DATE = 'date'
        
        def create_question(
            question_text: Annotated[str, Field(min_length=1, max_length=500)],
            question_type: QuestionType,
            required: bool = True,
            options: list[str] | None = None,
            min_rating: Annotated[int, Field(ge=1, le=10)] | None = None,
            max_rating: Annotated[int, Field(ge=1, le=10)] | None = None,
            placeholder: Annotated[str, Field(max_length=100)] | None = None
        ):
            return {"question_id": "q123"}
        
        result = analyze_function(create_question)
        
        assert get_param(result, 'question_text').constraints is not None
        assert get_param(result, 'question_type').choices.enum_class == QuestionType
        assert get_param(result, 'required').default is True
        assert get_param(result, 'options').optional.enabled is False


class TestSchedulingFunctions:
    
    def test_create_meeting(self):
        class MeetingType(Enum):
            ONE_ON_ONE = '1:1'
            TEAM = 'team'
            ALL_HANDS = 'all-hands'
            CLIENT = 'client'
        
        def schedule_meeting(
            title: Annotated[str, Field(min_length=1, max_length=200)],
            start_date: date,
            start_time: time,
            duration_minutes: Annotated[int, Field(ge=15, le=480, multiple_of=15)],
            meeting_type: MeetingType,
            attendees: Annotated[list[Email], Field(min_length=1, max_length=100)],
            description: Annotated[str, Field(max_length=2000)] | None = None,
            location: Annotated[str, Field(max_length=100)] | None = None,
            send_reminders: bool = True,
            reminder_minutes: Annotated[int, Field(ge=5, le=1440)] = 15
        ):
            return {"meeting_id": "mtg_123"}
        
        result = analyze_function(schedule_meeting)
        
        assert get_param(result, 'duration_minutes').constraints is not None
        assert get_param(result, 'attendees').widget_type == 'Email'
        assert get_param(result, 'attendees').list is not None
        assert get_param(result, 'send_reminders').default is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
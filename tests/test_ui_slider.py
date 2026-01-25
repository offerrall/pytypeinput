# tests/test_ui_metadata_slider.py
import pytest
from typing import Annotated
from datetime import date

from pytypeinput import analyze_parameter, Field, Slider, Label, Description, Step, IsPassword, Rows
from typing import Literal
from enum import Enum
import inspect


# ===== VALID CASES =====

def test_slider_basic_int():
    def func(age: Annotated[int, Field(ge=18, le=120), Slider()]): pass
    param = inspect.signature(func).parameters['age']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.show_slider_value is True


def test_slider_basic_float():
    def func(price: Annotated[float, Field(ge=0.0, le=1000.0), Slider()]): pass
    param = inspect.signature(func).parameters['price']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.param_type == float


def test_slider_show_value_false():
    def func(volume: Annotated[int, Field(ge=0, le=100), Slider(show_value=False)]): pass
    param = inspect.signature(func).parameters['volume']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.show_slider_value is False


def test_slider_with_step():
    def func(price: Annotated[float, Field(ge=0.0, le=1000.0), Slider(), Step(10.0)]): pass
    param = inspect.signature(func).parameters['price']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.step == 10.0


def test_slider_with_label_description():
    def func(
        volume: Annotated[
            int,
            Field(ge=0, le=100),
            Slider(),
            Label("Volume Level"),
            Description("Adjust the audio volume")
        ]
    ): pass
    param = inspect.signature(func).parameters['volume']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.label == "Volume Level"
    assert metadata.ui.description == "Adjust the audio volume"


def test_slider_with_default():
    def func(brightness: Annotated[int, Field(ge=0, le=100), Slider()] = 75): pass
    param = inspect.signature(func).parameters['brightness']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.default == 75


def test_slider_optional():
    def func(volume: Annotated[int, Field(ge=0, le=100), Slider()] | None = None): pass
    param = inspect.signature(func).parameters['volume']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.optional is not None


def test_slider_optional_enabled():
    def func(volume: Annotated[int, Field(ge=0, le=100), Slider()] | None = 50): pass
    param = inspect.signature(func).parameters['volume']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.optional is not None
    assert metadata.optional.enabled is True
    assert metadata.default == 50


def test_slider_in_list():
    def func(ratings: list[Annotated[int, Field(ge=1, le=5), Slider()]]): pass
    param = inspect.signature(func).parameters['ratings']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.list is not None


def test_slider_list_with_metadata():
    def func(
        ratings: Annotated[
            list[Annotated[int, Field(ge=1, le=5), Slider()]],
            Field(min_length=1, max_length=10),
            Label("Product Ratings"),
            Description("Rate each product from 1-5")
        ]
    ): pass
    param = inspect.signature(func).parameters['ratings']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.label == "Product Ratings"
    assert metadata.ui.description == "Rate each product from 1-5"
    assert metadata.list is not None


def test_slider_with_gt_lt():
    # gt/lt should also work
    def func(score: Annotated[int, Field(gt=0, lt=100), Slider()]): pass
    param = inspect.signature(func).parameters['score']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True


def test_slider_mixed_constraints():
    # ge + lt
    def func(score: Annotated[int, Field(ge=0, lt=100), Slider()]): pass
    param = inspect.signature(func).parameters['score']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True


def test_slider_negative_values():
    def func(temperature: Annotated[int, Field(ge=-50, le=50), Slider()]): pass
    param = inspect.signature(func).parameters['temperature']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True


def test_slider_float_with_decimals():
    def func(percentage: Annotated[float, Field(ge=0.0, le=1.0), Slider(), Step(0.01)]): pass
    param = inspect.signature(func).parameters['percentage']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.step == 0.01


# ===== ERROR CASES =====

def test_slider_without_constraints_raises():
    def func(age: Annotated[int, Slider()]): pass
    param = inspect.signature(func).parameters['age']
    
    with pytest.raises(TypeError, match="Slider requires Field"):
        analyze_parameter(param)


def test_slider_without_min_raises():
    def func(age: Annotated[int, Field(le=120), Slider()]): pass
    param = inspect.signature(func).parameters['age']
    
    with pytest.raises(TypeError, match="requires both min"):
        analyze_parameter(param)


def test_slider_without_max_raises():
    def func(age: Annotated[int, Field(ge=18), Slider()]): pass
    param = inspect.signature(func).parameters['age']
    
    with pytest.raises(TypeError, match="requires both min"):
        analyze_parameter(param)


def test_slider_on_str_raises():
    def func(name: Annotated[str, Field(min_length=1, max_length=10), Slider()]): pass
    param = inspect.signature(func).parameters['name']
    
    with pytest.raises(TypeError, match="Slider only supported for int/float"):
        analyze_parameter(param)


def test_slider_on_bool_raises():
    def func(active: Annotated[bool, Slider()]): pass
    param = inspect.signature(func).parameters['active']
    
    with pytest.raises(TypeError, match="Slider only supported for int/float"):
        analyze_parameter(param)


def test_slider_on_date_raises():
    def func(birthday: Annotated[date, Slider()]): pass
    param = inspect.signature(func).parameters['birthday']
    
    with pytest.raises(TypeError, match="Slider only supported for int/float"):
        analyze_parameter(param)


# ===== IGNORED COMBINATIONS =====

def test_slider_with_password_ignored():
    # IsPassword se ignora en int (no debería dar error)
    def func(code: Annotated[int, Field(ge=1000, le=9999), Slider(), IsPassword()]): pass
    param = inspect.signature(func).parameters['code']
    metadata = analyze_parameter(param)
    
    # Se crea sin error, IsPassword se ignora
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.is_password is True  # Se almacena pero renderer lo ignora


def test_slider_with_rows_ignored():
    # Rows se ignora en int (no debería dar error)
    def func(count: Annotated[int, Field(ge=1, le=100), Slider(), Rows(5)]): pass
    param = inspect.signature(func).parameters['count']
    metadata = analyze_parameter(param)
    
    # Se crea sin error, Rows se ignora
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.rows == 5  # Se almacena pero renderer lo ignora

# ===== EDGE CASES =====

def test_slider_very_large_range():
    def func(value: Annotated[int, Field(ge=0, le=1000000), Slider()]): pass
    param = inspect.signature(func).parameters['value']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True


def test_slider_very_small_step():
    def func(precision: Annotated[float, Field(ge=0.0, le=1.0), Slider(), Step(0.0001)]): pass
    param = inspect.signature(func).parameters['precision']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True
    assert metadata.ui.step == 0.0001


def test_slider_same_min_max():
    # Min == Max (técnicamente válido pero inútil)
    def func(constant: Annotated[int, Field(ge=42, le=42), Slider()]): pass
    param = inspect.signature(func).parameters['constant']
    metadata = analyze_parameter(param)
    
    assert metadata.ui is not None
    assert metadata.ui.is_slider is True


def test_slider_default_outside_range_raises():
    # Default fuera del rango debería fallar en validación de Pydantic
    def func(age: Annotated[int, Field(ge=18, le=120), Slider()] = 10): pass
    param = inspect.signature(func).parameters['age']
    
    with pytest.raises(ValueError, match="does not satisfy constraints"):
        analyze_parameter(param)


def test_slider_invalid_show_value_type():
    # Slider(show_value=...) solo acepta bool
    with pytest.raises(TypeError, match="show_value must be bool"):
        from pytypeinput import Slider as SliderClass
        SliderClass(show_value="yes")
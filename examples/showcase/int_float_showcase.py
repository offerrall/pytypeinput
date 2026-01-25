from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, Step, Slider

from visual_test_base import run_visual_test


def int_float_test(
    basic_int: int,
    basic_float: float,
    age: Annotated[int, Field(ge=18, le=120)],
    percentage: Annotated[float, Field(gt=0.0, lt=100.0)],
    step_int: Annotated[int, Field(ge=0, le=100), Step(5)],
    step_float: Annotated[float, Field(ge=0.0, le=1.0), Step(0.01)],
    with_placeholder_int: Annotated[int, Field(ge=1, le=100), Placeholder("1-100")],
    with_placeholder_float: Annotated[float, Placeholder("0.00")],
    height_cm: Annotated[
        int,
        Field(ge=50, le=300),
        Step(1),
        Label("Height (cm)"),
        Placeholder("170"),
        Description("Your height in centimeters")
    ],
    volume: Annotated[int, Field(ge=0, le=100), Slider()],
    opacity: Annotated[float, Field(ge=0.0, le=1.0), Slider()],
    brightness: Annotated[int, Field(ge=0, le=100), Slider(show_value=True)],
    contrast: Annotated[int, Field(ge=0, le=100), Slider(show_value=False)],
    slider_step: Annotated[
        float,
        Field(ge=0.0, le=1.0),
        Slider(),
        Step(0.05)
    ],
    audio_volume: Annotated[
        int,
        Field(ge=0, le=100),
        Slider(show_value=True),
        Label("Audio Volume Suu"),
        Description("Adjust the master volume level")
    ],
    slider_placeholder_ignored: Annotated[
        int,
        Field(ge=0, le=100),
        Slider(),
        Placeholder("This should NOT appear"),
        Label("Slider ignores placeholder")
    ],
    temperature: Annotated[
        int,
        Field(ge=-50, le=50),
        Slider(show_value=True),
        Step(1),
        Label("Temperature (°C)"),
        Description("Color temperature adjustment"),
        Placeholder("Ignored in slider")
    ],
    numbers: list[int],
    prices: list[float],
    scores: Annotated[
        list[Annotated[int, Field(ge=0, le=100)]],
        Field(min_length=1, max_length=5)
    ],
    ages_list: list[Annotated[
        int,
        Field(ge=0, le=150),
        Placeholder("Age")
    ]],
    skill_levels: Annotated[
        list[Annotated[
            int,
            Field(ge=1, le=10),
            Slider(show_value=True)
        ]],
        Field(min_length=1, max_length=5),
        Label("Skill Levels (1-10)")
    ],
    skill_levels2: Annotated[
        list[Annotated[
            int,
            Field(ge=1, le=10),
            Slider(show_value=True)
        ]],
        Field(min_length=3, max_length=5),
        Label("Skill Levels 2 (1-10)")
    ],
    rating_levels: Annotated[
        list[Annotated[
            int,
            Field(ge=1, le=5),
            Slider(show_value=True),
            Placeholder("Should be ignored")
        ]],
        Label("Rate Multiple Items"),
        Description("Rate each item from 1-5 stars")
    ],
    optional_int: int | None,
    optional_float: float | None,
    optional_quantity: Annotated[
        int,
        Field(ge=1, le=999),
        Label("Order Quantity"),
        Placeholder("1"),
        Description("Optional: How many units?")
    ] | None,
    optional_numbers: list[int] | None,
    negative_range: Annotated[int, Field(ge=-100, le=100)],
    negative_slider: Annotated[
        int,
        Field(ge=-50, le=50),
        Slider(show_value=True),
        Label("Balance (-50 to +50)")
    ],
    very_precise: Annotated[
        float,
        Field(ge=0.0, le=1.0),
        Step(0.0001),
        Placeholder("0.0000")
    ],
    very_precise_slider: Annotated[
        float,
        Field(ge=0.0, le=1.0),
        Slider(show_value=True),
        Step(0.001),
        Label("Precision Slider")
    ],
    default_int: int = 42,
    default_float: float = 3.14,
    default_slider: Annotated[int, Field(ge=0, le=100), Slider()] = 75,
    default_list: list[int] = [1, 2, 3],
    optional_int_enabled: int | None = 10,
    optional_slider_enabled: Annotated[
        int,
        Field(ge=0, le=100),
        Slider(show_value=True)
    ] | None = 80,
    optional_explicit: int | OptionalEnabled = None,
    optional_disabled: int | OptionalDisabled = 99,
    optional_speed: Annotated[
        float,
        Field(ge=0.5, le=2.0),
        Slider(show_value=True),
        Step(0.1),
        Label("Playback Speed"),
        Description("Optional: Adjust playback speed"),
        Placeholder("Also ignored")
    ] | OptionalEnabled = None,
    optional_scores: list[Annotated[int, Field(ge=0, le=100)]] | None = [90, 85],
):
    pass


if __name__ == "__main__":
    run_visual_test(int_float_test, "Int & Float Test - Complete with Slider")

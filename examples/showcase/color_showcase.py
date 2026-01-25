from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, Color

from visual_test_base import run_visual_test


def color_test(
    basic_color: Color,
    
    primary_color: Annotated[Color, Label("Primary Brand Color")],
    
    accent_color: Annotated[
        Color,
        Description("Choose a color that complements your primary brand color")
    ],
    
    placeholder_color: Annotated[
        Color,
        Placeholder("#FF5733")
    ],
    
    theme_color: Annotated[
        Color,
        Label("Theme Color"),
        Placeholder("#3498DB"),
        Description("Main theme color for the application")
    ],
    
    background_color: Annotated[
        Color,
        Label("Background Color"),
        Placeholder("#FFFFFF"),
        Description("Background color for light theme. Use light colors for better readability.")
    ],
    
    colors: list[Color],
    
    palette_colors: Annotated[
        list[Color],
        Field(min_length=3, max_length=10),
        Label("Color Palette"),
        Description("Create a color palette with 3-10 colors")
    ],
    
    brand_colors: Annotated[
        list[Annotated[
            Color,
            Placeholder("#000000")
        ]],
        Label("Brand Colors"),
        Description("Define your brand color scheme")
    ],
    
    theme_palette: Annotated[
        list[Annotated[
            Color,
            Placeholder("#RRGGBB")
        ]],
        Field(min_length=2, max_length=5),
        Label("Theme Palette"),
        Description("Select 2-5 colors for your theme (2-5 colors)")
    ],
    
    optional_color: Color | None,
    
    optional_highlight: Annotated[
        Color,
        Label("Highlight Color"),
        Description("Optional: Color for highlighting important elements")
    ] | None,
    
    optional_colors: list[Color] | None,
    
    default_color: Color = "#4CAF50",
    
    default_with_label: Annotated[
        Color,
        Label("Success Color")
    ] = "#28A745",
    
    default_list: list[Color] = ["#FF0000", "#00FF00", "#0000FF"],
    
    optional_border: Annotated[
        Color,
        Label("Border Color"),
        Description("Custom border color for containers")
    ] | None = "#DDDDDD",
    
    optional_link: Annotated[
        Color,
        Label("Link Color"),
        Placeholder("#007BFF"),
        Description("Color for hyperlinks")
    ] | None = "#0056B3",
    
    optional_explicit: Color | OptionalEnabled = None,
    optional_disabled: Color | OptionalDisabled = "#CCCCCC",
    
    optional_text: Annotated[
        Color,
        Label("Text Color"),
        Placeholder("#333333"),
        Description("Optional: Default text color for the application")
    ] | OptionalEnabled = None,
    
    optional_error: Annotated[
        Color,
        Label("Error Color"),
        Placeholder("#DC3545"),
        Description("Optional error state color")
    ] | OptionalDisabled = "#F44336",
    
    optional_gradient: Annotated[
        list[Color],
        Label("Gradient Colors"),
        Description("Optional: Define gradient color stops")
    ] | None = ["#FF6B6B", "#4ECDC4", "#45B7D1"],
    
    optional_chart_colors: Annotated[
        list[Annotated[
            Color,
            Placeholder("#000000")
        ]],
        Field(min_length=2, max_length=8),
        Label("Chart Colors"),
        Description("Optional: Colors for data visualization (2-8 colors)")
    ] | None = ["#E74C3C", "#F39C12", "#27AE60"],
):
    pass


if __name__ == "__main__":
    run_visual_test(color_test, "Color Type Test - Complete")
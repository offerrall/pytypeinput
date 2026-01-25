from pytypeinput import Field, Label, Description, Annotated, PatternMessage

from visual_test_base import run_visual_test


Username = Annotated[
    str,
    Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$'),
    Label("Username"),
    Description("Choose a unique username (letters, numbers, underscore only)"),
    PatternMessage("Username can only contain letters, numbers, and underscores.")
]


if __name__ == "__main__":
    run_visual_test(Username, "Type Annotation to GUI", name="username")
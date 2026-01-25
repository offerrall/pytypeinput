from pytypeinput import OptionalEnabled, OptionalDisabled, Description, Label, Field, Annotated

from visual_test_base import run_visual_test


def bool_test(
    basic_bool: bool,
    accept_terms: Annotated[bool, Label("Accept Terms & Conditions")],
    newsletter: Annotated[
        bool,
        Description("Receive weekly updates about new features")
    ],
    notifications: Annotated[
        bool,
        Label("Enable Notifications"),
        Description("Allow push notifications on your device")
    ],
    privacy_consent: Annotated[
        bool,
        Label("Privacy Policy Agreement"),
        Description("I have read and agree to the privacy policy and data processing terms")
    ],
    preferences: list[bool],
    feature_flags: Annotated[
        list[bool],
        Field(min_length=2, max_length=10),
        Label("Feature Flags"),
        Description("Enable or disable features (2-10 items)")
    ],
    permissions: Annotated[
        list[bool],
        Field(min_length=3, max_length=5),
        Label("User Permissions"),
        Description("Grant or revoke permissions for this user (3-5 required)")
    ],
    optional_bool: bool | None,
    optional_marketing: Annotated[
        bool,
        Label("Marketing Emails"),
        Description("Optional: Receive promotional offers")
    ] | None,
    optional_settings: list[bool] | None,
    default_false: bool = False,
    default_true: bool = True,
    default_with_label: Annotated[
        bool,
        Label("Remember Me")
    ] = True,
    default_list: list[bool] = [True, False, True],
    optional_analytics: Annotated[
        bool,
        Label("Analytics Tracking"),
        Description("Help improve our service by sharing usage data")
    ] | None = False,
    optional_updates: Annotated[
        bool,
        Label("Product Updates"),
        Description("Stay informed about product updates")
    ] | None = True,
    optional_explicit: bool | OptionalEnabled = None,
    optional_disabled: bool | OptionalDisabled = True,
    optional_beta: Annotated[
        bool,
        Label("Beta Features"),
        Description("Access experimental features (may be unstable)")
    ] | OptionalDisabled = False,
    optional_dark_mode: Annotated[
        bool,
        Label("Dark Mode"),
        Description("Use dark theme for better readability at night")
    ] | OptionalEnabled = None,
    optional_days: Annotated[
        list[bool],
        Label("Active Days"),
        Description("Select which days the rule applies")
    ] | None = [True, True, True, False, False, False, False],
    optional_notifications: Annotated[
        list[bool],
        Field(min_length=1, max_length=5),
        Label("Notification Types"),
        Description("Choose which notifications to receive (1-5)")
    ] | None = [True, False, True],
):
    pass


if __name__ == "__main__":
    run_visual_test(bool_test, "Bool Type Test - Complete")

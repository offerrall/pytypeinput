from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, Email

from visual_test_base import run_visual_test


def email_test(
    basic_email: Email,
    user_email: Annotated[Email, Label("Email Address")],
    contact_email: Annotated[
        Email,
        Description("We'll use this to contact you about your order")
    ],
    placeholder_email: Annotated[
        Email,
        Placeholder("you@example.com")
    ],
    short_email: Annotated[
        Email,
        Field(max_length=50)
    ],
    work_email: Annotated[
        Email,
        Field(min_length=5, max_length=100),
        Label("Work Email"),
        Placeholder("name@company.com"),
        Description("Your professional email address")
    ],
    registration_email: Annotated[
        Email,
        Field(min_length=5, max_length=150),
        Label("Registration Email"),
        Placeholder("your.email@domain.com"),
        Description("This will be your username for login. Make sure you have access to this email.")
    ],
    emails: list[Email],
    team_emails: Annotated[
        list[Email],
        Field(min_length=2, max_length=10),
        Label("Team Members"),
        Description("Add 2-10 team member emails")
    ],
    cc_recipients: Annotated[
        list[Annotated[
            Email,
            Placeholder("recipient@example.com")
        ]],
        Label("CC Recipients"),
        Description("Copy these people on all communications")
    ],
    notification_list: Annotated[
        list[Annotated[
            Email,
            Field(max_length=100),
            Placeholder("email@example.com")
        ]],
        Field(min_length=1, max_length=5),
        Label("Notification Emails"),
        Description("Send alerts to these addresses (1-5 emails)")
    ],
    optional_email: Email | None,
    optional_recovery: Annotated[
        Email,
        Label("Recovery Email"),
        Description("Optional: For account recovery")
    ] | None,
    optional_emails: list[Email] | None,
    default_email: Email = "user@example.com",
    default_with_label: Annotated[
        Email,
        Label("Primary Email")
    ] = "primary@example.com",
    default_list: list[Email] = ["admin@example.com", "support@example.com"],
    optional_secondary: Annotated[
        Email,
        Label("Secondary Email"),
        Description("Backup email for notifications")
    ] | None = "backup@example.com",
    optional_billing: Annotated[
        Email,
        Label("Billing Email"),
        Placeholder("billing@company.com"),
        Description("Where to send invoices")
    ] | None = "finance@example.com",
    optional_explicit: Email | OptionalEnabled = None,
    optional_disabled: Email | OptionalDisabled = "ignored@example.com",
    optional_support: Annotated[
        Email,
        Field(min_length=5, max_length=100),
        Label("Support Email"),
        Placeholder("support@yourcompany.com"),
        Description("Optional: Your company's support email for customers")
    ] | OptionalEnabled = None,
    optional_marketing: Annotated[
        Email,
        Label("Marketing Email"),
        Placeholder("marketing@company.com"),
        Description("Optional marketing contact")
    ] | OptionalDisabled = "promo@example.com",
    optional_managers: Annotated[
        list[Email],
        Label("Manager Emails"),
        Description("Optional: Add manager emails for escalations")
    ] | None = ["manager1@example.com", "manager2@example.com"],
    optional_admins: Annotated[
        list[Annotated[
            Email,
            Field(max_length=100),
            Placeholder("admin@example.com")
        ]],
        Field(min_length=1, max_length=3),
        Label("Administrator Emails"),
        Description("Optional: System administrators (1-3 emails)")
    ] | None = ["admin@example.com"],
):
    pass


if __name__ == "__main__":
    run_visual_test(email_test, "Email Type Test - Complete")

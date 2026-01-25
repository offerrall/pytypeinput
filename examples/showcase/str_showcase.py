from pytypeinput import OptionalEnabled, OptionalDisabled, IsPassword, Placeholder, PatternMessage, Description, Label, Rows, Field, Annotated

from visual_test_base import run_visual_test


def str_test(
    basic_str: str,
    min_max_str: Annotated[str, Field(min_length=3, max_length=20)],
    username: Annotated[
        str,
        Field(pattern=r'^[a-zA-Z0-9_]+$', min_length=3, max_length=20),
        PatternMessage("letters, numbers, underscore only")
    ],
    with_placeholder: Annotated[str, Placeholder("Enter your email...")],
    password: Annotated[
        str, 
        Field(pattern=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'), 
        IsPassword(),
        PatternMessage("8+ chars with uppercase, lowercase, and number")
    ],
    phone: Annotated[
        str,
        Field(pattern=r'^\d{10}$'),
        PatternMessage("Must be exactly 10 digits"),
        Description("Your mobile phone number (no spaces or dashes)")
    ],
    user_full_name: Annotated[str, Label("Full Name")],
    bio: Annotated[
        str,
        Rows(5),
        Placeholder("Tell us about yourself..."),
        Description("This will appear on your public profile")
    ],
    address: Annotated[
        str,
        Rows(3),
        Label("Street Address"),
        Placeholder("123 Main St"),
        Description("Your shipping address")
    ],
    tags: list[str],
    emails: list[Annotated[
        str,
        Field(pattern=r'^[^@]+@[^@]+\.[^@]+$'),
        PatternMessage("Invalid email format")
    ]],
    skills: Annotated[list[str], Field(min_length=2, max_length=5)],
    skills2: Annotated[
        list[Annotated[
            str,
            Field(min_length=3, max_length=100, pattern=r'^[a-zA-Z0-9\s\-\+\#]+$'),
            Rows(3),
            Placeholder("e.g., Python programming, Machine Learning, Docker..."),
            PatternMessage("Only letters, numbers, spaces, -, +, and # allowed"),
        ]],
        Field(min_length=2, max_length=5),
        Label("Your Top Skills"),
        Description("List 2-5 of your most relevant professional skills (each can be multiple lines)")
    ],
    country: str = "USA",
    languages: list[str] = ["English"],
    optional_disabled: str | None = None,
    optional_enabled: str | None = "default",
    optional_explicit: str | OptionalEnabled = None,
    optional_explicit_disabled: str | OptionalDisabled = "ignored",
    middle_name: Annotated[str, Label("Middle Name Suuu")] | None = None,
    nickname: Annotated[str, Label("Nickname Suu")] | None = "Johnny",
    website: Annotated[
        str,
        Description("Your personal website (optional)")
    ] | None = None,
    twitter: Annotated[
        str,
        Placeholder("@username")
    ] | None = None,
    additional_notes: Annotated[
        str,
        Rows(4),
        Placeholder("Any additional information...")
    ] | None = None,
    company: Annotated[
        str,
        Label("Company Name"),
        Description("Where do you currently work? (optional)")
    ] | None = None,
    linkedin: Annotated[
        str,
        Field(pattern=r'^https://www\.linkedin\.com/in/[a-zA-Z0-9\-]+$'),
        Label("LinkedIn Profile"),
        Placeholder("https://www.linkedin.com/in/yourname"),
        PatternMessage("Must be a valid LinkedIn profile URL"),
        Description("Your LinkedIn profile URL (optional)")
    ] | None = None,
    current_password: Annotated[
        str,
        IsPassword(),
        Label("Current Password"),
        Description("Required only if changing password")
    ] | None = None,
    cover_letter: Annotated[
        str,
        Field(min_length=50, max_length=1000),
        Rows(8),
        Label("Cover Letter"),
        Placeholder("Tell us why you're interested in this position..."),
        Description("Optional but recommended. Help us understand your motivation (50-1000 characters)")
    ] | None = None,
    hobbies: list[str] | None = None,
    certifications: list[str] | None = ["AWS Certified"],
    achievements: Annotated[
        list[Annotated[
            str,
            Field(min_length=10, max_length=200),
            Placeholder("Describe your achievement...")
        ]],
        Label("Key Achievements"),
        Description("Optional: Share your proudest accomplishments")
    ] | None = None,
    projects: Annotated[
        list[Annotated[
            str,
            Field(min_length=20, max_length=500),
            Rows(4),
            Placeholder("Describe the project, your role, and impact..."),
            PatternMessage("Only letters, numbers, and basic punctuation")
        ]],
        Field(min_length=1, max_length=5),
        Label("Personal Projects"),
        Description("Optional: Showcase 1-5 projects you're proud of")
    ] | None = None,
    github: Annotated[
        str,
        Field(pattern=r'^https://github\.com/[a-zA-Z0-9\-]+$'),
        Label("GitHub Profile"),
        Placeholder("https://github.com/yourusername"),
        PatternMessage("Must be a valid GitHub profile URL, like https://github.com/yourusername"),
        Description("Your GitHub profile")
    ] | None = "https://github.com/example",
    portfolio: Annotated[
        str,
        Field(pattern=r'^https?://.*'),
        Label("Portfolio Website"),
        Placeholder("https://yourportfolio.com"),
        PatternMessage("Must be a valid URL"),
        Description("Show us your work!")
    ] | OptionalEnabled = None,
    referral_code: Annotated[
        str,
        Field(min_length=6, max_length=6, pattern=r'^[A-Z0-9]+$'),
        Label("Referral Code"),
        Placeholder("ABC123"),
        PatternMessage("Only uppercase letters and numbers, 6 characters"),
        Description("Optional referral code from a friend")
    ] | OptionalDisabled = "REFER1",
):
    pass


if __name__ == "__main__":
    run_visual_test(str_test, "String Type Test - Complete + Optionals")

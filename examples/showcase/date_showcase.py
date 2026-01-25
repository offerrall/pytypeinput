from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, date

from visual_test_base import run_visual_test


def date_test(
    basic_date: date,
    
    birth_date: Annotated[date, Label("Date of Birth")],
    
    start_date: Annotated[
        date,
        Description("When should this event begin?")
    ],
    
    placeholder_date: Annotated[
        date,
        Placeholder("YYYY-MM-DD")
    ],
    
    appointment_date: Annotated[
        date,
        Label("Appointment Date"),
        Placeholder("Select a date"),
        Description("Choose your preferred appointment date")
    ],
    
    registration_date: Annotated[
        date,
        Label("Registration Date"),
        Placeholder("YYYY-MM-DD"),
        Description("Date when you first registered. This cannot be changed later.")
    ],
    
    dates: list[date],
    
    milestone_dates: Annotated[
        list[date],
        Field(min_length=2, max_length=10),
        Label("Project Milestones"),
        Description("Add 2-10 milestone dates for your project")
    ],
    
    event_dates: Annotated[
        list[Annotated[
            date,
            Placeholder("Event date")
        ]],
        Label("Event Dates"),
        Description("Specify all event dates")
    ],
    
    deadline_dates: Annotated[
        list[Annotated[
            date,
            Placeholder("YYYY-MM-DD")
        ]],
        Field(min_length=1, max_length=5),
        Label("Deadlines"),
        Description("Set 1-5 important deadlines")
    ],
    
    optional_date: date | None,
    
    optional_end_date: Annotated[
        date,
        Label("End Date"),
        Description("Optional: When should this event end?")
    ] | None,
    
    optional_dates: list[date] | None,
    
    default_date: date = date(2024, 1, 1),
    
    default_with_label: Annotated[
        date,
        Label("Contract Start Date")
    ] = date(2024, 6, 1),
    
    default_list: list[date] = [date(2024, 1, 1), date(2024, 6, 1), date(2024, 12, 31)],
    
    optional_reminder: Annotated[
        date,
        Label("Reminder Date"),
        Description("Set a reminder date for this task")
    ] | None = date(2024, 3, 15),
    
    optional_expiry: Annotated[
        date,
        Label("Expiry Date"),
        Placeholder("YYYY-MM-DD"),
        Description("When does this expire?")
    ] | None = date(2025, 12, 31),
    
    optional_explicit: date | OptionalEnabled = None,
    optional_disabled: date | OptionalDisabled = date(2024, 1, 1),
    
    optional_launch: Annotated[
        date,
        Label("Launch Date"),
        Placeholder("Product launch"),
        Description("Optional: Target launch date for the product")
    ] | OptionalEnabled = None,
    
    optional_archived: Annotated[
        date,
        Label("Archive Date"),
        Placeholder("YYYY-MM-DD"),
        Description("Optional archive date")
    ] | OptionalDisabled = date(2023, 12, 31),
    
    optional_holidays: Annotated[
        list[date],
        Label("Holiday Dates"),
        Description("Optional: Mark company holidays")
    ] | None = [date(2024, 12, 25), date(2024, 1, 1)],
    
    optional_reviews: Annotated[
        list[Annotated[
            date,
            Placeholder("Review date")
        ]],
        Field(min_length=2, max_length=4),
        Label("Review Dates"),
        Description("Optional: Quarterly review dates (1-4 dates)")
    ] | None = [date(2024, 3, 31), date(2024, 6, 30)],
):
    pass


if __name__ == "__main__":
    run_visual_test(date_test, "Date Type Test - Complete")
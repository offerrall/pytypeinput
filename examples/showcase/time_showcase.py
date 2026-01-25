from pytypeinput import OptionalEnabled, OptionalDisabled, Placeholder, Description, Label, Field, Annotated, time

from visual_test_base import run_visual_test


def time_test(
    basic_time: time,
    
    meeting_time: Annotated[time, Label("Meeting Time Suu")],
    
    start_time: Annotated[
        time,
        Description("What time should this event start?")
    ],
    
    placeholder_time: Annotated[
        time,
        Placeholder("HH:MM")
    ],
    
    appointment_time: Annotated[
        time,
        Label("Appointment Time"),
        Placeholder("Select a time"),
        Description("Choose your preferred appointment time")
    ],
    
    work_start: Annotated[
        time,
        Label("Work Start Time"),
        Placeholder("HH:MM"),
        Description("When does your workday begin? (24-hour format)")
    ],
    
    times: list[time],
    
    schedule_times: Annotated[
        list[time],
        Field(min_length=2, max_length=10),
        Label("Daily Schedule"),
        Description("Add 2-10 important times in your daily schedule")
    ],
    
    alarm_times: Annotated[
        list[Annotated[
            time,
            Placeholder("Alarm time")
        ]],
        Label("Alarm Times"),
        Description("Set your daily alarms")
    ],
    
    reminder_times: Annotated[
        list[Annotated[
            time,
            Placeholder("HH:MM")
        ]],
        Field(min_length=1, max_length=5),
        Label("Reminders"),
        Description("Set 1-5 reminder times")
    ],
    
    optional_time: time | None,
    
    optional_end_time: Annotated[
        time,
        Label("End Time"),
        Description("Optional: When should this event end?")
    ] | None,
    
    optional_times: list[time] | None,
    
    default_time: time = time(9, 0),
    
    default_with_label: Annotated[
        time,
        Label("Office Opening Time")
    ] = time(8, 30),
    
    default_list: list[time] = [time(9, 0), time(12, 0), time(17, 0)],
    
    optional_lunch: Annotated[
        time,
        Label("Lunch Break"),
        Description("Your preferred lunch break time")
    ] | None = time(12, 30),
    
    optional_notification: Annotated[
        time,
        Label("Notification Time"),
        Placeholder("HH:MM"),
        Description("When to receive daily notifications?")
    ] | None = time(10, 0),
    
    optional_explicit: time | OptionalEnabled = None,
    optional_disabled: time | OptionalDisabled = time(18, 0),
    
    optional_backup: Annotated[
        time,
        Label("Backup Time"),
        Placeholder("Daily backup"),
        Description("Optional: Scheduled time for daily backups")
    ] | OptionalEnabled = None,
    
    optional_maintenance: Annotated[
        time,
        Label("Maintenance Window"),
        Placeholder("HH:MM"),
        Description("Optional maintenance time")
    ] | OptionalDisabled = time(2, 0),
    
    optional_breaks: Annotated[
        list[time],
        Label("Break Times"),
        Description("Optional: Scheduled break times throughout the day")
    ] | None = [time(10, 30), time(15, 0)],
    
    optional_meetings: Annotated[
        list[Annotated[
            time,
            Placeholder("Meeting time")
        ]],
        Field(min_length=1, max_length=6),
        Label("Recurring Meetings"),
        Description("Optional: Regular meeting times (1-6 times)")
    ] | None = [time(9, 30), time(14, 0)],
):
    pass


if __name__ == "__main__":
    run_visual_test(time_test, "Time Type Test - Complete")
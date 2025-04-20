import { API, CREATE_REMINDER_SCHEDULE } from "./constants";

const FORM: HTMLFormElement = document.getElementById("quick-create-reminder-form") as HTMLFormElement;
const ERROR_MSG: HTMLParagraphElement = document.getElementById("error-msg") as HTMLParagraphElement;

interface TimeOfDay {
    hours: number
    minutes: number
}

interface CreateReminderRequest {
    reminder: string
    hint: string
    reminder_times: Date[],
    schedule: number
}

function set_error_message(message: string) {
    ERROR_MSG.innerText = message
}

function increment_date_by_days(date: Date, days: number) {
    date.setDate(date.getDate() + days);
}

function time_string_to_time_of_day(time_string: string): TimeOfDay {
    const [hours_string, minutes_string] = time_string.split(":")
    const hours = Number.parseInt(hours_string)
    const minutes = Number.parseInt(minutes_string)
    return { hours, minutes }
}

FORM.addEventListener("submit", async (e) => {
    e.preventDefault()
    const reminder: string = FORM.elements["reminder"].value
    const hint: string = FORM.elements["hint"].value
    const time_of_day: TimeOfDay = time_string_to_time_of_day(FORM.elements["notification_time"].value)
    const schedule = FORM.elements["schedule"].value

    const date = new Date()
    date.setHours(time_of_day.hours)
    date.setMinutes(time_of_day.minutes)
    date.setSeconds(0)
    date.setMilliseconds(0)
    if (date <= new Date()) {
        increment_date_by_days(date, 1)
    }
    const reminder_times: Date[] = []
    if (schedule === "quick-everyday") { // 5 Days
        for (let i = 0; i < 5; i++) {
            reminder_times.push(new Date(date))
            increment_date_by_days(date, 1)
        }
    } else if (schedule === "quick-probing") { // 6 days. 12 hours, 12 hours, 1 day, 2 days, 3 days
        reminder_times.push(new Date(date))
        increment_date_by_days(date, 0.5)
        reminder_times.push(new Date(date))
        increment_date_by_days(date, 0.5)
        reminder_times.push(new Date(date))
        increment_date_by_days(date, 1)
        reminder_times.push(new Date(date))
        increment_date_by_days(date, 2)
        reminder_times.push(new Date(date))
        increment_date_by_days(date, 3)
        reminder_times.push(new Date(date))
    }

    const reminder_request_body: CreateReminderRequest = {
        reminder,
        hint,
        reminder_times,
        schedule: 1
    }
    const response = await fetch(`${API}/${CREATE_REMINDER_SCHEDULE}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(reminder_request_body)
        }
    )

    if (!response.ok) {
        const error_message = `Error creating reminder schedule: ${response.statusText}.`
        console.error(error_message)
        set_error_message(error_message)
        return
    }
    window.location.href = "/upcoming-reminders.html"
})
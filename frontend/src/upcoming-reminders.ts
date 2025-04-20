import { API, DELETE_REMINDER_SCHEDULE, GET_REMINDER_SCHEDULES } from "./constants"
import { Reminder, ReminderSchedule } from "./types"
const CALENDAR = document.getElementById("calendar")
const REMINDER_SCHEDULE = document.getElementById("reminder-schedule-list")
const ERROR_BOX_ELEMENT = document.getElementById("error-box")
const DAYS_TO_SHOW = 7;

function set_error_message(message: string) {
  if (ERROR_BOX_ELEMENT)
    ERROR_BOX_ELEMENT.innerText = message
}
async function reload() {
  const response = await fetch(`${API}/${GET_REMINDER_SCHEDULES}`,
    {
      method: "GET"
    }
  )
  const reminder_schedules: ReminderSchedule[] = await response.json()
  reminder_schedules.forEach((rs) => {
    rs.creation_time = new Date(rs.creation_time)
    let actual_reminder_times: Date[] = []
    rs.reminder_times.forEach((reminder_time) => {
      actual_reminder_times.push(new Date(reminder_time))
    })
    rs.reminder_times = actual_reminder_times
  })
  const reminder_schedules_grouped_by_day: Map<string, ReminderSchedule[]> = new Map();
  const reminders_grouped_by_day: Map<string, Reminder[]> = new Map();
  if (response.status !== 200) {
    const error_message = `Error fetching reminder schedules: ${response.statusText}.`
    console.error(error_message);
    set_error_message(error_message);
    return;
  }

  // Group by day
  reminder_schedules.forEach((reminder_schedule) => {
    const day = new Date(reminder_schedule.creation_time).toDateString()
    if (!reminder_schedules_grouped_by_day.has(day)) {
      reminder_schedules_grouped_by_day.set(day, [])
    }
    reminder_schedules_grouped_by_day.get(day)?.push(reminder_schedule)
    reminder_schedule.reminder_times.forEach((reminder_time) => {
      const day = reminder_time.toDateString()
      if (!reminders_grouped_by_day.has(day)) {
        reminders_grouped_by_day.set(day, [])
      }
      const _reminder: Reminder = {
        reminder_schedule,
        reminder_time,
      }
      reminders_grouped_by_day.get(day)?.push(_reminder);
    })
  })
  draw_calendar(reminders_grouped_by_day);
  draw_reminder_schedules_list(reminder_schedules);
}

function draw_calendar(reminders_grouped_by_day: Map<string, Reminder[]>) {
  if (CALENDAR)
    CALENDAR.innerHTML = ""

  // Create boxes
  let date = new Date()
  for (let i = 0; i < DAYS_TO_SHOW; i++) {
    const dayBox = document.createElement("div");
    dayBox.setAttribute('class', 'calendar-day');
    const reminders_for_day = reminders_grouped_by_day.get(date.toDateString()) || []
    for (const reminder_for_day of reminders_for_day) {
      const reminderElement = document.createElement("div")
      reminderElement.setAttribute("class", "reminder")
      reminderElement.innerText = `(${reminder_for_day.reminder_schedule.reminder_id}) ${reminder_for_day.reminder_schedule.reminder}`
      dayBox.appendChild(reminderElement);
    }
    dayBox.innerHTML = `${date.getMonth()}/${date.getDate()}/${date.getFullYear()}` + dayBox.innerHTML
    CALENDAR?.appendChild(dayBox)
    date.setDate(date.getDate() + 1)
  }
}

function draw_reminder_schedules_list(reminder_schedules: ReminderSchedule[]) {
  if (REMINDER_SCHEDULE)
    REMINDER_SCHEDULE.innerHTML = ""
  draw_reminder_schedules_header()
  for (const reminder_schedule of reminder_schedules) {
    draw_reminder_schedule(reminder_schedule)
  }
}

function draw_reminder_schedules_header() {
  const headers = ['ID', 'Reminder', 'Hint', 'Creation Time', 'Delete'];
  if (REMINDER_SCHEDULE)

    headers.forEach(text => {
      const th = document.createElement('th');
      th.textContent = text;
      REMINDER_SCHEDULE.appendChild(th);
    });
}

function draw_reminder_schedule(reminder_schedule: ReminderSchedule) {
  const table_row = document.createElement("tr")
  const reminder_id_element = document.createElement("td")
  const reminder_element = document.createElement("td")
  const hint_element = document.createElement("td")
  const creation_time_element = document.createElement("td")
  const delete_reminder_element = document.createElement("td")
  const delete_button_element = document.createElement("button")

  delete_button_element.innerText = "Del"
  delete_button_element.addEventListener("click", async (event) => {
    const response = await fetch(`${API}/${DELETE_REMINDER_SCHEDULE}/${reminder_schedule.reminder_id}`,
      {
        method: "DELETE"
      }
    )
    if (!response.ok) {
      const error_message = `Error deleting schedule with id ${reminder_schedule.reminder_id}: ${response.statusText}.`
      set_error_message(error_message);
      console.error(error_message);
      return;
    }
    reload();
  })

  reminder_id_element.innerText = reminder_schedule.reminder_id.toString()
  reminder_element.innerText = reminder_schedule.reminder.toString()
  hint_element.innerText = reminder_schedule.hint.toString()
  creation_time_element.innerText = reminder_schedule.creation_time.toDateString()
  delete_reminder_element.appendChild(delete_button_element)

  table_row.appendChild(reminder_id_element)
  table_row.appendChild(reminder_element)
  table_row.appendChild(hint_element)
  table_row.appendChild(creation_time_element)
  table_row.appendChild(delete_reminder_element)

  REMINDER_SCHEDULE?.appendChild(table_row);
}

reload()
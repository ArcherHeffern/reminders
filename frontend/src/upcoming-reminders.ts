import {API, GET_REMINDER_SCHEDULES} from "./constants"
import { ReminderSchedule } from "./types"
const reminderList = document.getElementById("reminder-list")
const MAX_REMINDERS_RENDERED = 3

async function get_reminder_schedules() {
  const response = await fetch(`${API}/${GET_REMINDER_SCHEDULES}`,
      {
          method: "GET"
        }
  )
  const reminder_schedules: ReminderSchedule[] = await response.json()
  if (reminderList) {
    reminder_schedules.forEach((rs) => {
      console.log(rs.reminder)
      let upcoming_reminders = ""
      
      reminderList.innerHTML += `
      <div>
        <h3>${rs.reminder}</h3>
        <p>Created: ${rs.creation_time}</p>
      </div> 
      `
    })

  }

  console.log(JSON.stringify(reminder_schedules))
  // if (reminderList != null) {
  //   reminderList.innerHTML = ""
  // }

}

get_reminder_schedules()
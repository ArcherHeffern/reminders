const reminderList = document.getElementById("reminder-list")
import {API, GET_REMINDER_SCHEDULES} from "./constants"

async function get_reminder_schedules() {
  const response = await fetch(`${API}/${GET_REMINDER_SCHEDULES}`,
      {
          method: "GET"
        }
  )
  const reminder_schedules = await response.json()

  console.log("HERE")

}

get_reminder_schedules()
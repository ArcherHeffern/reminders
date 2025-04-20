from fastapi import FastAPI
from datetime import datetime, timezone
from fastapi.exceptions import HTTPException
from constants import Schedule
from database import con, create_database
from pydantic import BaseModel


class CreateReminderSchedule(BaseModel):
    reminder: str
    reminder_times: list[datetime] 
    schedule: int

class ReminderSchedule(BaseModel):
    reminder_id: int
    reminder: str
    creation_time: datetime
    reminder_times: list[datetime] 
    schedule: int

create_database()
app = FastAPI()

@app.post("/reminder_schedule")
async def create_reminder_schedule(create_reminder_schedule_request: CreateReminderSchedule):
    if create_reminder_schedule_request.schedule not in Schedule:
        raise HTTPException(400, "Unrecognized schedule type")
    with con as cur:
        now = datetime.now(timezone.utc)
        last_row_id = cur.execute("""
                    INSERT INTO ReminderSchedule (reminder,creation_date, schedule) VALUES (?,?,?);
                    """, (create_reminder_schedule_request.reminder, now.isoformat(), create_reminder_schedule_request.schedule)).lastrowid
        
        for reminder_time in create_reminder_schedule_request.reminder_times:
            if reminder_time < now:
                cur.rollback()
                raise HTTPException(400, f"Recieved reminder_time before current time (current_time={now.isoformat()}, bad_reminder_time={reminder_time})")
            cur.execute("""
                INSERT INTO Reminder (date, completed, reminder_schedule) VALUES (?,?,?);
            """, (reminder_time.isoformat(), False, last_row_id))
    return 

@app.delete("/reminder_schedule/{reminder_schedule_id}")
async def delete_reminder_schedule(reminder_schdule_id: int):
    ...

@app.get("/reminder_schedules")
async def get_reminder_schedules() -> list[ReminderSchedule]:
    reminder_schedules: list[ReminderSchedule] = []
    with con as cur:
        for row in cur.execute("""
            SELECT * FROM ReminderSchedule;
        """):
            reminder_schedule = ReminderSchedule(
                reminder_id=row[0],
                reminder=row[1],
                creation_time=row[2],
                reminder_times=[],
                schedule=row[3],
            )
            reminder_schedule.reminder_times = []
            for reminder_time in cur.execute("""
                SELECT * FROM Reminder WHERE Reminder.reminder_schedule == ?;
                """, (reminder_schedule.reminder_id,)):
                reminder_schedule.reminder_times.append(reminder_time[0])
            reminder_schedules.append(reminder_schedule)
    return reminder_schedules

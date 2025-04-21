from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi.exceptions import HTTPException
from constants import Schedule
from database import con, create_database
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from chron import ReminderService

class CreateReminderSchedule(BaseModel):
    reminder: str
    hint: str
    reminder_times: list[datetime] 
    schedule: int

class ReminderSchedule(BaseModel):
    reminder_id: int
    reminder: str
    hint: str
    creation_time: datetime
    reminder_times: list[datetime] 
    schedule: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    reminder_service = ReminderService()
    scheduler = BackgroundScheduler()
    reminder_service.trigger()
    scheduler.add_job(reminder_service.trigger, IntervalTrigger(hours=1, start_date=datetime.now()))
    scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/reminder_schedule")
async def create_reminder_schedule(create_reminder_schedule_request: CreateReminderSchedule):
    if create_reminder_schedule_request.schedule not in Schedule:
        raise HTTPException(400, "Unrecognized schedule type")
    with con as cur:
        now = datetime.now(timezone.utc)
        last_row_id = cur.execute("""
                    INSERT INTO ReminderSchedule (reminder,hint,creation_date, schedule) VALUES (?,?,?,?);
                    """, (create_reminder_schedule_request.reminder, create_reminder_schedule_request.hint, now.isoformat(), create_reminder_schedule_request.schedule)).lastrowid
        
        for reminder_time in create_reminder_schedule_request.reminder_times:
            if reminder_time < now:
                cur.rollback()
                raise HTTPException(400, f"Recieved reminder_time before current time (current_time={now.isoformat()}, bad_reminder_time={reminder_time})")
            cur.execute("""
                INSERT INTO Reminder (date, completed, reminder_schedule) VALUES (?,?,?);
            """, (reminder_time.isoformat(), False, last_row_id))
    return 

@app.delete("/reminder_schedule/{reminder_schedule_id}")
async def delete_reminder_schedule(reminder_schedule_id: int):
    with con as cur:
        if cur.execute("SELECT * FROM ReminderSchedule WHERE reminder_id = ?;", (reminder_schedule_id,)).fetchone() is None:
            raise HTTPException(404, f"reminder schedule with id={reminder_schedule_id} not found")
        cur.execute("""
            DELETE FROM Reminder WHERE reminder_schedule = ?;
        """, (reminder_schedule_id,))
        cur.execute("""
            DELETE FROM ReminderSchedule WHERE reminder_id = ?;
        """, (reminder_schedule_id,))

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
                hint=row[2],
                creation_time=row[3],
                reminder_times=[],
                schedule=row[4],
            )
            reminder_schedule.reminder_times = []
            for reminder_time in cur.execute("""
                SELECT * FROM Reminder WHERE Reminder.reminder_schedule == ?;
                """, (reminder_schedule.reminder_id,)):
                reminder_schedule.reminder_times.append(reminder_time[0])
            reminder_schedules.append(reminder_schedule)
    return reminder_schedules

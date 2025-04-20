from datetime import datetime
from sqlite3 import connect, Connection
import constants as constants 
con: Connection = connect("reminder.db")

def create_database():
    with con as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ReminderSchedule (
            reminder_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder        TEXT,
            hint            TEXT,
            creation_date   INTEGER,
            schedule        INTEGER
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS Reminder (
            date                INTEGER,
            completed           BOOLEAN,
            reminder_schedule   INTEGER,
            FOREIGN KEY(reminder_schedule) REFERENCES ReminderSchedule(reminder_id)
        )""")

if __name__ == '__main__':
    create_database()
    with con as cur:
        cur.execute("INSERT INTO ReminderSchedule (reminder,creation_date, schedule) VALUES (?,?,?)", ("hello", datetime.now().isoformat(), constants.Schedule.EVERYDAY.value))
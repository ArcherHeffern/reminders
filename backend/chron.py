from database import con
from dataclasses import dataclass
import os
from twilio.rest import Client
from email.message import EmailMessage
from smtplib import SMTP
from dotenv import load
load()

# Not working, don't want to pay for getting a phone number validated or something
class TwilioClient:
    def __init__(self):
        # Find your Account SID and Auth Token at twilio.com/console
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.from_=os.environ["TWILIO_PHONE_NUMBER_FROM"]
        self.to_=os.environ["TWILIO_PHONE_NUMBER_TO"]
        self.client = Client(account_sid, auth_token)

    def send(self, message: str):
        message = self.client.messages.create(
            body=message,
            from_=self.from_,
            to=self.to_,
        )


# Not working: running into auto issues
class GmailClient:
    def __init__(self):
        gmail_host=os.environ["GMAIL_HOST"]
        gmail_port=int(os.environ["GMAIL_PORT"])
        gmail_account=os.environ["GMAIL_ACCOUNT"]
        google_app_password=os.environ["GOOGLE_APP_PASSWORD"]
        self.to=os.environ["GMAIL_RECIPIANT"]
        self.s = SMTP(gmail_host, gmail_port)
        self.s.ehlo()
        self.s.starttls()
        self.s.ehlo()
        self.s.login(gmail_account, google_app_password)

    def send(self, subject: str, body: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["To"] = self.to
        msg.set_content(body)
        self.s.send_message(msg)
        return self

    def close(self):
        self.s.quit()


@dataclass
class OutstandingReminder:
    reminder_id: int
    reminder: str
    hint: str
    

class ReminderService:
    def trigger(self):
        outstanding_reminders = self.__get_outstanding_reminders()
        self.__send_alerts(outstanding_reminders)

    def __get_outstanding_reminders(self):
        # gets and marks all outstanding reminders as completed
        # Set all results to completed
        # Query for all 
        outstanding_reminders: list[OutstandingReminder] = []
        with con as cur:
            for result in cur.execute("SELECT Reminder.rowid,ReminderSchedule.reminder,ReminderSchedule.hint FROM Reminder INNER JOIN ReminderSchedule on Reminder.reminder_schedule = ReminderSchedule.reminder_id WHERE completed = 0 AND date < datetime('now');"):
                print(result)
                outstanding_reminder = OutstandingReminder(
                    reminder_id=result[0],
                    reminder=result[1],
                    hint=result[2],
                )
                outstanding_reminders.append(outstanding_reminder)
                cur.execute("UPDATE Reminder SET completed = 1 WHERE rowid = ?;", (outstanding_reminder.reminder_id,))
        return outstanding_reminders

    def __send_alerts(self, outstanding_reminders: list[OutstandingReminder]):
        for outstanding_reminder in outstanding_reminders:
            print(outstanding_reminder.reminder)
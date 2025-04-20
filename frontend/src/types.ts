export interface ReminderSchedule {
    reminder_id: number,
    reminder: string,
    hint: string,
    creation_time: Date,
    reminder_times: Date[],
    schedule: number,
};

export interface Reminder {
    reminder_schedule: ReminderSchedule
    reminder_time: Date
}
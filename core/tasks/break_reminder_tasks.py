# tasks/break_reminder_tasks.py

from celery import shared_task
from ..services.break_reminder_service import send_break_reminders


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=60, retry_kwargs={"max_retries": 3})
def send_break_reminders_task(self):
    send_break_reminders()

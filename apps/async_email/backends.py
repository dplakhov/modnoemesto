from django.core.mail.backends.base import BaseEmailBackend

from apps.async_email.tasks import send_email_task


class CeleryEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for msg in email_messages:
            send_email_task.delay(msg)


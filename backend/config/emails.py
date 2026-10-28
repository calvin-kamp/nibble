from django.db import transaction

from .tasks import send_email_task


def send_email(recipients, subject, body):
    """Queues a plain-text e-mail once the current transaction has committed."""
    if isinstance(recipients, str):
        recipients = [recipients]

    if not recipients:
        return

    transaction.on_commit(
        lambda: send_email_task.delay(list(recipients), subject, body)
    )

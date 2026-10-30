from django.db import transaction
from django.template.loader import render_to_string

from .tasks import send_email_task


def send_email(recipients, subject, body, html=None):
    """Queues an e-mail once the current transaction has committed."""
    if isinstance(recipients, str):
        recipients = [recipients]

    if not recipients:
        return

    transaction.on_commit(
        lambda: send_email_task.delay(list(recipients), subject, body, html)
    )


def send_template_email(recipients, subject, template, context):
    """Renders emails/<template>.txt and .html and queues both."""
    body = render_to_string(f"emails/text/{template}.txt", context)
    html = render_to_string(f"emails/html/{template}.html", context)

    send_email(recipients, subject, body, html)

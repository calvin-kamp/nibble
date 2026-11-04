from django.conf import settings
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
    """Renders emails/<template>.txt and .html and queues both.

    Every template gets the frontend address for logo and footer links, and the support
    address for questions.
    """
    context = {
        "frontend_url": settings.FRONTEND_URL.rstrip("/"),
        "support_email": settings.SUPPORT_EMAIL,
        **context,
    }
    body = render_to_string(f"emails/text/{template}.txt", context)
    html = render_to_string(f"emails/html/{template}.html", context)

    send_email(recipients, subject, body, html)

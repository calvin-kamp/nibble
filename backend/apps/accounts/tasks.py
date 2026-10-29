from celery import shared_task
from django.core.management import call_command
from django.utils import timezone

from .models import User
from .services import delete_account


@shared_task
def delete_expired_accounts():
    """Daily job: deletes every account whose 7-day period is over."""
    users = User.objects.filter(deletion_scheduled_for__lte=timezone.now())
    count = 0

    for user in users.select_related("profile"):
        delete_account(user)
        count += 1

    return count


@shared_task
def flush_expired_tokens():
    """Keeps the token blacklist tables small."""
    call_command("flushexpiredtokens")

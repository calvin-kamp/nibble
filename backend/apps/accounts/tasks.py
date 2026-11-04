from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from config.emails import send_email

from .deletion_log import format_line
from .models import DeletionLog, User
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


@shared_task
def send_deletion_log():
    """Daily job: mails new deletion log entries off the server, drops old ones.

    The mail is the copy that survives restoring the whole server, see deletion_log.
    Entries are kept as long as a backup can still contain the account.
    """
    DeletionLog.objects.filter(
        occurred_at__lt=timezone.now() - settings.DELETION_LOG_RETENTION
    ).delete()

    entries = list(DeletionLog.objects.filter(reported_at__isnull=True))
    recipients = settings.DELETION_LOG_RECIPIENTS or list(
        User.objects.filter(is_staff=True, is_active=True).values_list(
            "email", flat=True
        )
    )

    if not entries or not recipients:
        return 0

    lines = "\n".join(format_line(entry) for entry in entries)
    body = (
        "Neue Einträge im Löschprotokoll von nibble. Nur Konto-IDs und Zeitpunkte.\n\n"
        "Wird eine Datensicherung eingespielt, die älter ist als diese Einträge, "
        "die Zeilen in eine Datei kopieren und vor dem Freischalten ausführen:\n"
        "python manage.py reapply_deletions --file <datei>\n\n"
        f"{lines}\n"
    )
    send_email(recipients, f"Löschprotokoll: {len(entries)} neue Einträge", body)

    DeletionLog.objects.filter(pk__in=[entry.pk for entry in entries]).update(
        reported_at=timezone.now()
    )

    return len(entries)

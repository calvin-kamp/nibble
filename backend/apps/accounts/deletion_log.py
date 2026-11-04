"""Log of deletions, so they can be repeated after a backup has been restored.

Every request, cancellation and deletion becomes one entry. The daily mail carries the
same entries as text lines, outside the server: restoring the whole server also turns
the log in the database back. reapply_deletions reads both.

Line format, one entry per line:
    <event> <user id> <joined at> <occurred at> [<scheduled for>]
e.g. "deleted 42 2026-11-01T10:00:00+00:00 2026-11-09T03:00:01+00:00"
"""

from dataclasses import dataclass
from datetime import datetime

from django.db import transaction

from .models import DeletionLog, User

Event = DeletionLog.Event


def record(user, event, scheduled_for=None):
    return DeletionLog.objects.create(
        user_id=user.pk,
        joined_at=user.date_joined,
        event=event,
        scheduled_for=scheduled_for,
    )


def format_line(entry):
    parts = [
        entry.event,
        str(entry.user_id),
        entry.joined_at.isoformat(),
        entry.occurred_at.isoformat(),
    ]

    if entry.scheduled_for:
        parts.append(entry.scheduled_for.isoformat())

    return " ".join(parts)


def parse_line(line):
    """A DeletionLog (not saved) for a line of the mail, None for any other line."""
    parts = line.split()

    if len(parts) not in (4, 5) or parts[0] not in Event.values:
        return None

    try:
        return DeletionLog(
            event=parts[0],
            user_id=int(parts[1]),
            joined_at=datetime.fromisoformat(parts[2]),
            occurred_at=datetime.fromisoformat(parts[3]),
            scheduled_for=datetime.fromisoformat(parts[4]) if len(parts) == 5 else None,
        )
    except ValueError:
        return None


@dataclass
class Outcome:
    user_id: int
    action: str


def reapply(entries, dry_run=False):
    """Brings every account to the last logged state and returns what was done.

    Only an account with the same ID and the same registration time counts: an ID
    given out again after the restore belongs to someone else and stays untouched.
    """
    from .services import delete_account

    latest = {}

    for entry in sorted(entries, key=lambda e: e.occurred_at):
        latest[entry.user_id] = entry

    outcomes = []

    for user_id, entry in sorted(latest.items()):
        user = User.objects.filter(pk=user_id).select_related("profile").first()

        if user is None:
            outcomes.append(Outcome(user_id, "not there, nothing to do"))
            continue

        if user.date_joined != entry.joined_at:
            outcomes.append(Outcome(user_id, "other account with this ID, skipped"))
            continue

        if entry.event == Event.DELETED:
            outcomes.append(Outcome(user_id, "deleted"))

            if not dry_run:
                # The person was told when it happened the first time
                delete_account(user, notify=False)

        elif entry.event == Event.REQUESTED:
            if user.deletion_scheduled_for == entry.scheduled_for:
                outcomes.append(Outcome(user_id, "deletion already scheduled"))
                continue

            outcomes.append(
                Outcome(user_id, f"deletion scheduled for {entry.scheduled_for}")
            )

            if not dry_run:
                user.deletion_scheduled_for = entry.scheduled_for
                user.save(update_fields=["deletion_scheduled_for"])

        elif user.deletion_scheduled_for is not None:
            outcomes.append(Outcome(user_id, "deletion cancelled"))

            if not dry_run:
                user.deletion_scheduled_for = None
                user.save(update_fields=["deletion_scheduled_for"])

        else:
            outcomes.append(Outcome(user_id, "no deletion scheduled, nothing to do"))

    return outcomes


def reapply_atomically(entries, dry_run=False):
    with transaction.atomic():
        return reapply(entries, dry_run=dry_run)

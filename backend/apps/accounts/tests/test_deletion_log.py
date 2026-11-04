import tempfile
from datetime import timedelta
from io import StringIO
from pathlib import Path

from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.accounts.deletion_log import format_line, parse_line
from apps.accounts.models import DeletionLog, User
from apps.accounts.tasks import delete_expired_accounts, send_deletion_log
from config.testing import PASSWORD, ApiTestCase

Event = DeletionLog.Event


class DeletionLogTests(ApiTestCase):
    """Every step of a deletion is logged with ID and timestamps only."""

    def setUp(self):
        super().setUp()
        self.user = self.create_user("gurke@example.com", username="gurke")
        self.login(self.user)

    def test_request_cancel_and_deletion_are_logged(self):
        requested = self.client.post(
            reverse("account_deletion"), {"password": PASSWORD}
        )
        again = self.client.post(reverse("account_deletion"), {"password": PASSWORD})
        cancelled = self.client.delete(reverse("account_deletion"))
        self.client.post(reverse("account_deletion"), {"password": PASSWORD})
        User.objects.filter(pk=self.user.pk).update(
            deletion_scheduled_for=timezone.now() - timedelta(minutes=1)
        )
        delete_expired_accounts()

        self.assertEqual(requested.status_code, status.HTTP_200_OK)
        self.assertEqual(again.status_code, status.HTTP_200_OK)
        self.assertEqual(cancelled.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            list(DeletionLog.objects.values_list("event", flat=True)),
            [Event.REQUESTED, Event.CANCELLED, Event.REQUESTED, Event.DELETED],
        )
        entry = DeletionLog.objects.first()
        self.assertEqual(entry.user_id, self.user.pk)
        self.assertEqual(entry.joined_at, self.user.date_joined)
        self.assertIsNotNone(entry.scheduled_for)

    def test_deleting_in_the_admin_is_logged_too(self):
        self.user.delete()

        self.assertEqual(DeletionLog.objects.get().event, Event.DELETED)

    def test_lines_survive_the_round_trip(self):
        self.client.post(reverse("account_deletion"), {"password": PASSWORD})
        entry = DeletionLog.objects.get()

        parsed = parse_line(format_line(entry))

        self.assertEqual(
            (parsed.event, parsed.user_id, parsed.joined_at, parsed.scheduled_for),
            (entry.event, entry.user_id, entry.joined_at, entry.scheduled_for),
        )
        self.assertIsNone(parse_line("Neue Einträge im Löschprotokoll von nibble."))
        self.assertIsNone(parse_line("deleted keine-id 2026 2026"))


class DeletionLogMailTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.staff = self.create_user("admin@example.com", is_staff=True)
        self.user = self.create_user("gurke@example.com")

    def test_new_entries_go_out_once_and_old_ones_are_dropped(self):
        user_id = self.user.pk
        self.user.delete()
        old = DeletionLog.objects.create(
            user_id=999,
            joined_at=timezone.now(),
            event=Event.DELETED,
            occurred_at=timezone.now() - timedelta(days=31),
        )

        with self.captureOnCommitCallbacks(execute=True):
            first = send_deletion_log()
        with self.captureOnCommitCallbacks(execute=True):
            second = send_deletion_log()

        self.assertEqual((first, second), (1, 0))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.staff.email])
        self.assertIn(f"deleted {user_id} ", mail.outbox[0].body)
        self.assertNotIn(self.user.email, mail.outbox[0].body)
        self.assertFalse(DeletionLog.objects.filter(pk=old.pk).exists())

    @override_settings(DELETION_LOG_RECIPIENTS=["backup@example.com"])
    def test_recipients_can_be_set(self):
        self.user.delete()

        with self.captureOnCommitCallbacks(execute=True):
            send_deletion_log()

        self.assertEqual(mail.outbox[0].to, ["backup@example.com"])


class ReapplyDeletionsTests(ApiTestCase):
    """A restored backup still has the account; the mail or the log knows better."""

    def setUp(self):
        super().setUp()
        self.user = self.create_user("gurke@example.com")
        self.joined = self.user.date_joined

    def log_file(self, *entries):
        text = "Kopf der Mail\n\n" + "\n".join(format_line(entry) for entry in entries)
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        )
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)

        return handle.name

    def entry(self, event, minutes_ago=0, **extra):
        return DeletionLog(
            user_id=self.user.pk,
            joined_at=self.joined,
            event=event,
            occurred_at=timezone.now() - timedelta(minutes=minutes_ago),
            **extra,
        )

    def run_command(self, *args):
        out = StringIO()

        with self.captureOnCommitCallbacks(execute=True):
            call_command("reapply_deletions", *args, stdout=out)

        return out.getvalue()

    def test_deleted_account_from_the_mail_is_deleted_again_without_mail(self):
        path = self.log_file(self.entry(Event.REQUESTED, 60), self.entry(Event.DELETED))

        output = self.run_command("--file", path)

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("2 entries", output)
        self.assertIn(f"account {self.user.pk}: deleted", output)

    def test_lost_request_is_scheduled_again(self):
        scheduled = timezone.now() + timedelta(days=5)
        path = self.log_file(self.entry(Event.REQUESTED, scheduled_for=scheduled))

        self.run_command("--file", path)

        self.user.refresh_from_db()
        self.assertEqual(self.user.deletion_scheduled_for, scheduled)

    def test_cancellation_after_the_request_wins(self):
        User.objects.filter(pk=self.user.pk).update(
            deletion_scheduled_for=timezone.now() + timedelta(days=5)
        )
        path = self.log_file(
            self.entry(Event.REQUESTED, 60, scheduled_for=timezone.now()),
            self.entry(Event.CANCELLED),
        )

        self.run_command("--file", path)

        self.user.refresh_from_db()
        self.assertIsNone(self.user.deletion_scheduled_for)

    def test_reused_id_of_another_account_stays_untouched(self):
        other = self.entry(Event.DELETED)
        other.joined_at = self.joined - timedelta(days=3)

        output = self.run_command("--file", self.log_file(other))

        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertIn("other account with this ID, skipped", output)

    def test_dry_run_changes_nothing(self):
        output = self.run_command(
            "--dry-run", "--file", self.log_file(self.entry(Event.DELETED))
        )

        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertIn("Dry run", output)

    def test_log_in_the_database_is_read_too(self):
        self.entry(Event.DELETED).save()

        self.run_command()

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

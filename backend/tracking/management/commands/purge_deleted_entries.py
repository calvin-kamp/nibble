"""Deletes diary entries removed longer ago than the undo window.

Removing an entry only marks it, so "Rückgängig" can bring it back. Run this
regularly (e.g. daily via cron) to delete marked entries for good:

    manage.py purge_deleted_entries --hours 24
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from tracking.models import DiaryEntry


class Command(BaseCommand):
    help = "Deletes diary entries that were removed more than --hours ago."

    def add_arguments(self, parser):
        parser.add_argument("--hours", type=int, default=24)

    def handle(self, *args, hours, **options):
        cutoff = timezone.now() - timedelta(hours=hours)
        count, _ = DiaryEntry.objects.filter(deleted_at__lt=cutoff).delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} rows."))

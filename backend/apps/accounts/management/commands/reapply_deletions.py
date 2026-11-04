from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.accounts.deletion_log import parse_line, reapply_atomically
from apps.accounts.models import DeletionLog


class Command(BaseCommand):
    help = (
        "After restoring a backup: repeats every deletion, request and cancellation "
        "from the deletion log. Run it before the site goes back online."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            action="append",
            default=[],
            help="Text file with lines from the daily deletion log mails; repeatable. "
            "Other lines in the file are ignored.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only shows what would happen.",
        )

    def handle(self, *args, **options):
        entries = list(DeletionLog.objects.all())

        for name in options["file"]:
            path = Path(name)

            if not path.is_file():
                raise CommandError(f"File not found: {path}")

            parsed = [parse_line(line) for line in path.read_text("utf-8").splitlines()]
            found = [entry for entry in parsed if entry is not None]
            self.stdout.write(f"{path}: {len(found)} entries")
            entries += found

        if not entries:
            self.stdout.write("The deletion log is empty, nothing to do.")
            return

        outcomes = reapply_atomically(entries, dry_run=options["dry_run"])

        for outcome in outcomes:
            self.stdout.write(f"  account {outcome.user_id}: {outcome.action}")

        prefix = "Dry run, nothing changed. " if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(f"{prefix}{len(outcomes)} accounts checked.")
        )

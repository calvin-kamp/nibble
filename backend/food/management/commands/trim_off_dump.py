"""Turns the Open Food Facts CSV export into a small file for ``import_foods``.

    manage.py trim_off_dump en.openfoodfacts.org.products.csv.gz off-dach.csv.gz

Streams the export row by row, so the uncompressed 10 GB never sit in memory.
See food/off.py for what is kept.
"""

from django.core.management.base import BaseCommand

from food.off import (
    DEFAULT_COUNTRIES,
    open_text,
    read_export,
    trim_export,
    write_trimmed,
)


class Command(BaseCommand):
    help = "Keeps the products and columns Nibble needs from the OFF export."

    def add_arguments(self, parser):
        parser.add_argument("source", help="en.openfoodfacts.org.products.csv(.gz)")
        parser.add_argument("target", help="Trimmed CSV, gzipped if it ends in .gz")
        parser.add_argument(
            "--countries",
            default=",".join(sorted(DEFAULT_COUNTRIES)),
            help="Comma-separated countries_tags, default: %(default)s",
        )

    def handle(self, *args, source, target, countries, **options):
        tags = frozenset(tag.strip() for tag in countries.split(",") if tag.strip())

        with open_text(source) as raw, open_text(target, "wt") as trimmed:
            count = write_trimmed(trimmed, trim_export(read_export(raw), tags))

        self.stdout.write(self.style.SUCCESS(f"Kept {count} products in {target}."))

"""Loads a file from ``trim_off_dump`` into the food database.

    manage.py import_foods off-dach.csv.gz

Products are matched by barcode: new ones are created, known ones get the
current name, brand, values, portion and popularity. Nothing is deleted, because
diary entries and meals may point to products that left the export.
"""

from decimal import Decimal
from itertools import batched

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from food.models import Food, FoodUnit
from food.off import open_text, read_trimmed

BATCH_SIZE = 2000

UPDATED_FIELDS = [
    "name",
    "brand",
    "basis",
    "kcal_per_100",
    "protein_per_100",
    "carbs_per_100",
    "fat_per_100",
    "popularity",
    "source",
    "updated_at",
]


def decimal(value):
    return Decimal(str(value))


def to_food(item):
    return Food(
        barcode=item.barcode,
        name=item.name,
        brand=item.brand,
        basis=item.basis,
        kcal_per_100=decimal(item.kcal),
        protein_per_100=decimal(item.protein),
        carbs_per_100=decimal(item.carbs),
        fat_per_100=decimal(item.fat),
        popularity=item.scans,
        source=Food.Source.OPEN_FOOD_FACTS,
    )


class Command(BaseCommand):
    help = "Creates or updates foods from a trimmed Open Food Facts file."

    def add_arguments(self, parser):
        parser.add_argument("source", help="Output of trim_off_dump")

    def handle(self, *args, source, **options):
        total = 0

        try:
            with open_text(source) as stream:
                for batch in batched(read_trimmed(stream), BATCH_SIZE):
                    self.upsert(batch)
                    total += len(batch)

                    if total % (BATCH_SIZE * 25) == 0:
                        self.stdout.write(f"{total} products …")
        except ValueError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(self.style.SUCCESS(f"Imported {total} products."))

    @transaction.atomic
    def upsert(self, items):
        Food.objects.bulk_create(
            [to_food(item) for item in items],
            update_conflicts=True,
            unique_fields=["barcode"],
            update_fields=UPDATED_FIELDS,
        )

        # Upserts don't return every id on every database, so look them up.
        ids = dict(
            Food.objects.filter(
                barcode__in=[item.barcode for item in items]
            ).values_list("barcode", "id")
        )
        servings = {ids[item.barcode]: item.serving for item in items}

        FoodUnit.objects.filter(
            food_id__in=[food for food, serving in servings.items() if serving is None],
            kind=FoodUnit.Kind.PORTION,
        ).delete()
        FoodUnit.objects.bulk_create(
            [
                FoodUnit(
                    food_id=food, kind=FoodUnit.Kind.PORTION, amount=decimal(serving)
                )
                for food, serving in servings.items()
                if serving is not None
            ],
            update_conflicts=True,
            unique_fields=["food", "kind"],
            update_fields=["amount"],
        )

"""Basic foods without barcode, with household measures Open Food Facts lacks.

Rounded reference values per 100 g (or 100 ml) for everyday foods like an
apple or a slice of bread. Safe to run repeatedly: existing basic foods (same
name, no brand, no barcode) get the values and units below.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from food.models import Basis, Food, FoodUnit

G = Basis.GRAM
ML = Basis.MILLILITRE

PIECE = FoodUnit.Kind.PIECE
SLICE = FoodUnit.Kind.SLICE
SPOON = FoodUnit.Kind.TABLESPOON
PORTION = FoodUnit.Kind.PORTION

# name, basis, kcal, protein, carbs, fat (per 100), units {kind: amount}
FOODS = [
    ("Apfel", G, 52, 0.3, 11.4, 0.2, {PIECE: 150}),
    ("Avocado", G, 160, 2, 1.9, 14.7, {PIECE: 140}),
    ("Banane", G, 89, 1.1, 20, 0.2, {PIECE: 120}),
    ("Basmatireis, roh", G, 351, 8, 77, 0.9, {PORTION: 75}),
    ("Brokkoli", G, 34, 2.8, 2.7, 0.4, {}),
    ("Butter", G, 741, 0.7, 0.6, 83, {SPOON: 10}),
    ("Ei (Hühnerei)", G, 140, 12.5, 0.7, 9.7, {PIECE: 60}),
    ("Erdnussbutter", G, 610, 25, 13, 50, {SPOON: 16}),
    ("Gouda jung", G, 356, 24, 0, 29, {SLICE: 20}),
    ("Gurke", G, 13, 0.6, 1.8, 0.2, {PIECE: 400}),
    ("Haferdrink", ML, 45, 1, 6.5, 1.5, {}),
    ("Haferflocken", G, 372, 13.5, 58.7, 7, {PORTION: 40, SPOON: 10}),
    ("Hähnchenbrustfilet", G, 105, 23.5, 0, 1.2, {PIECE: 150}),
    ("Heidelbeeren", G, 42, 0.6, 7.4, 0.6, {PORTION: 125}),
    ("Honig", G, 304, 0.3, 80, 0, {SPOON: 20}),
    ("Kartoffeln", G, 72, 2, 15, 0.1, {PIECE: 80}),
    ("Kichererbsen, gegart", G, 120, 7, 16, 2.5, {}),
    ("Lachsfilet", G, 200, 20, 0, 13.5, {PIECE: 125}),
    ("Magerquark", G, 67, 12, 4, 0.2, {SPOON: 30}),
    ("Mandeln", G, 580, 24, 6, 52, {PORTION: 30}),
    ("Mozzarella", G, 240, 18, 1, 18, {PIECE: 125}),
    ("Naturjoghurt 3,5 %", G, 62, 3.5, 4, 3.5, {SPOON: 15}),
    ("Olivenöl", ML, 819, 0, 0, 91, {SPOON: 10}),
    ("Paprika, rot", G, 31, 1, 6, 0.3, {PIECE: 150}),
    ("Rote Linsen, roh", G, 340, 24, 50, 1.5, {PORTION: 60}),
    ("Skyr natur", G, 63, 11, 4, 0.2, {PORTION: 150}),
    ("Tomate", G, 18, 0.9, 2.6, 0.2, {PIECE: 80}),
    ("Toastbrot", G, 260, 8, 48, 3.5, {SLICE: 25}),
    ("Vollkornbrot", G, 216, 7, 38, 1.2, {SLICE: 50}),
    ("Vollkornnudeln, roh", G, 340, 13, 64, 2.5, {PORTION: 100}),
    ("Vollmilch 3,5 %", ML, 64, 3.3, 4.8, 3.5, {}),
]


class Command(BaseCommand):
    help = "Creates or updates the basic foods with their household measures."

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0

        for name, basis, kcal, protein, carbs, fat, units in FOODS:
            food, is_new = Food.objects.update_or_create(
                name=name,
                brand="",
                barcode=None,
                defaults={
                    "basis": basis,
                    "kcal_per_100": Decimal(str(kcal)),
                    "protein_per_100": Decimal(str(protein)),
                    "carbs_per_100": Decimal(str(carbs)),
                    "fat_per_100": Decimal(str(fat)),
                    "source": Food.Source.NIBBLE,
                },
            )
            created += is_new

            food.units.exclude(kind__in=units).delete()

            for kind, amount in units.items():
                FoodUnit.objects.update_or_create(
                    food=food, kind=kind, defaults={"amount": Decimal(amount)}
                )

        self.stdout.write(
            self.style.SUCCESS(f"Foods: {created} new, {len(FOODS) - created} updated.")
        )

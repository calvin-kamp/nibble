"""Loose foods without a barcode, e.g. a banana, so they can be found in the search.

Values per 100 g of the edible part, rounded, carbohydrates without fibre as on EU labels.
Serving is one average piece where that is how people count it. Staff can correct every
value in the admin; the import never touches these products.
"""

from django.db import migrations
from django.utils import timezone

# name, kcal, protein, carbs, fat, one piece in g (or None)
FOODS = (
    # Fruit
    ("Apfel", 54, 0.3, 11.4, 0.2, 150),
    ("Banane", 89, 1.1, 20.2, 0.3, 120),
    ("Birne", 57, 0.4, 12.1, 0.1, 160),
    ("Orange", 47, 0.9, 9.4, 0.1, 150),
    ("Mandarine", 53, 0.8, 11.5, 0.3, 60),
    ("Grapefruit", 42, 0.8, 9.1, 0.1, 250),
    ("Zitrone", 29, 1.1, 6.5, 0.3, 60),
    ("Kiwi", 61, 1.1, 11.7, 0.5, 70),
    ("Erdbeeren", 32, 0.7, 5.7, 0.3, None),
    ("Heidelbeeren", 57, 0.7, 12.1, 0.3, None),
    ("Himbeeren", 52, 1.2, 5.4, 0.7, None),
    ("Weintrauben", 69, 0.7, 17.2, 0.2, None),
    ("Kirschen", 63, 1.1, 13.9, 0.2, None),
    ("Pflaume", 46, 0.7, 10.0, 0.3, 35),
    ("Pfirsich", 39, 0.9, 8.0, 0.3, 130),
    ("Nektarine", 44, 1.1, 8.9, 0.3, 130),
    ("Aprikose", 48, 1.4, 9.1, 0.4, 40),
    ("Ananas", 50, 0.5, 11.7, 0.1, None),
    ("Mango", 60, 0.8, 13.4, 0.4, 300),
    ("Wassermelone", 30, 0.6, 7.2, 0.2, None),
    ("Honigmelone", 36, 0.5, 8.2, 0.1, None),
    ("Avocado", 160, 2.0, 1.8, 14.7, 140),
    # Vegetables
    ("Tomate", 18, 0.9, 2.7, 0.2, 100),
    ("Cherrytomaten", 18, 0.9, 2.7, 0.2, None),
    ("Gurke", 15, 0.7, 3.1, 0.1, 400),
    ("Paprika rot", 31, 1.0, 3.9, 0.3, 150),
    ("Paprika grün", 20, 0.9, 2.9, 0.2, 150),
    ("Karotte", 41, 0.9, 6.8, 0.2, 70),
    ("Zucchini", 17, 1.2, 2.1, 0.3, 250),
    ("Aubergine", 25, 1.0, 2.9, 0.2, 300),
    ("Brokkoli", 34, 2.8, 4.0, 0.4, None),
    ("Blumenkohl", 25, 1.9, 3.0, 0.3, None),
    ("Kohlrabi", 27, 1.7, 2.6, 0.1, 250),
    ("Champignons", 22, 3.1, 2.3, 0.3, None),
    ("Spinat", 23, 2.9, 1.4, 0.4, None),
    ("Eisbergsalat", 14, 0.9, 1.8, 0.1, None),
    ("Zwiebel", 40, 1.1, 7.6, 0.1, 80),
    ("Knoblauch", 149, 6.4, 30.9, 0.5, 4),
    ("Kartoffeln", 77, 2.0, 15.3, 0.1, 100),
    ("Süßkartoffel", 86, 1.6, 17.1, 0.1, 250),
    # Other loose food
    ("Hühnerei", 143, 12.6, 0.7, 9.5, 60),
)


def add_foods(apps, schema_editor):
    FoodProduct = apps.get_model("foods", "FoodProduct")
    now = timezone.now()

    FoodProduct.objects.bulk_create(
        [
            FoodProduct(
                code=f"n{index:05d}",
                name=name,
                base_unit="g",
                kcal_per_100=kcal,
                protein_per_100=protein,
                carbs_per_100=carbs,
                fat_per_100=fat,
                serving_quantity=piece,
                generic=True,
                imported_at=now,
                curated_at=now,
            )
            for index, (name, kcal, protein, carbs, fat, piece) in enumerate(FOODS, start=1)
        ],
        ignore_conflicts=True,
    )


def remove_foods(apps, schema_editor):
    FoodProduct = apps.get_model("foods", "FoodProduct")
    FoodProduct.objects.filter(generic=True, code__startswith="n").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("foods", "0004_generic_and_reports"),
    ]

    operations = [
        migrations.RunPython(add_foods, remove_foods),
    ]

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("foods", "0003_curated_and_missing_barcodes"),
    ]

    operations = [
        migrations.AddField(
            model_name="foodproduct",
            name="generic",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="FoodReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("nutrition", "Nährwerte falsch"),
                            ("unit", "Gramm und Milliliter vertauscht"),
                            ("quantity", "Portion oder Packung falsch"),
                            ("name", "Name oder Marke falsch"),
                            ("other", "Etwas anderes"),
                        ],
                        max_length=20,
                    ),
                ),
                ("comment", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="foods.foodproduct",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

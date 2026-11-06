from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracking", "0004_remove_meal_note"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trackingentry",
            name="source",
            field=models.CharField(
                choices=[
                    ("off", "Open Food Facts"),
                    ("meal", "Eigene Mahlzeit"),
                    ("manual", "Selbst eingetragen"),
                ],
                default="off",
                max_length=6,
            ),
        ),
    ]

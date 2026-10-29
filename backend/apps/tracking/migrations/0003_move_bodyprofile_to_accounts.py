# Body data moved to the accounts app (accounts/0003_bodyprofile).
# The table is only renamed, the rows stay.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0002_body_profile_meal_note"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AlterModelTable(
                    name="bodyprofile",
                    table="accounts_bodyprofile",
                ),
            ],
            state_operations=[
                migrations.DeleteModel(
                    name="BodyProfile",
                ),
            ],
        ),
    ]

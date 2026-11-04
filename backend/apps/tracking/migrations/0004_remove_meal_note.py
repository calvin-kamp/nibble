# Meals no longer have notes. Dropping the column deletes the notes stored so far.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0003_move_bodyprofile_to_accounts"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="meal",
            name="note",
        ),
    ]

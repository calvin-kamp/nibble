"""Trigram indexes for the food search on PostgreSQL.

``icontains`` becomes ``UPPER(column) LIKE UPPER('%term%')``, which a B-tree
index can't serve. With hundreds of thousands of Open Food Facts products the
search needs GIN indexes over exactly these expressions. Other databases
(SQLite in tests) skip this migration.

Creating the pg_trgm extension needs a role that may create extensions; the
owner of the Docker database can.
"""

from django.db import migrations

INDEXES = {
    "food_food_name_trgm": "name",
    "food_food_brand_trgm": "brand",
}


def create_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    for index, column in INDEXES.items():
        schema_editor.execute(
            f"CREATE INDEX IF NOT EXISTS {index} ON food_food "
            f'USING gin ((UPPER("{column}"::text)) gin_trgm_ops)'
        )


def drop_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    for index in INDEXES:
        schema_editor.execute(f"DROP INDEX IF EXISTS {index}")


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_indexes, drop_indexes),
    ]

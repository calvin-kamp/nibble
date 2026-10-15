"""Reading a diary day: entries grouped by section, totals and recent foods."""

from decimal import Decimal

from django.db.models import Prefetch

from food.models import NUTRIENTS

from .models import DiaryEntry, DiaryEntryItem, Section

RECENT_LIMIT = 20
# Enough history to find 20 different foods without scanning everything.
RECENT_SCAN = 300


def empty_totals():
    return dict.fromkeys(NUTRIENTS, Decimal(0))


def add_totals(totals, values):
    for name in NUTRIENTS:
        totals[name] += values[name]

    return totals


def entries_of_day(user, date):
    return (
        DiaryEntry.objects.active()
        .filter(owner=user, date=date)
        .select_related("food")
        .prefetch_related(
            Prefetch("items", queryset=DiaryEntryItem.objects.order_by("id")),
            "food__units",
        )
    )


def sections_of(entries):
    """All five sections in their fixed order, each with its entries and totals."""
    grouped = {section: [] for section in Section.values}

    for entry in entries:
        grouped[entry.section].append(entry)

    sections = []

    for section in Section:
        totals = empty_totals()

        for entry in grouped[section.value]:
            add_totals(totals, entry.nutrients(entry.items.all()))

        sections.append(
            {
                "key": section.value,
                "name": section.label,
                "totals": totals,
                "entries": grouped[section.value],
            }
        )

    return sections


def day_totals(sections):
    totals = empty_totals()

    for section in sections:
        add_totals(totals, section["totals"])

    return totals


def recent_foods(user, limit=RECENT_LIMIT):
    """Different foods logged last, each with the amount and unit used last time.

    Foods that left the database (food is null) are skipped, they can't be
    logged again.
    """
    entries = (
        DiaryEntry.objects.active()
        .filter(owner=user, kind=DiaryEntry.Kind.FOOD, food__isnull=False)
        .select_related("food")
        .prefetch_related("food__units")
        .order_by("-created_at", "-id")[:RECENT_SCAN]
    )
    seen = set()
    recent = []

    for entry in entries:
        if entry.food_id in seen:
            continue

        seen.add(entry.food_id)
        recent.append(entry)

        if len(recent) == limit:
            break

    return recent

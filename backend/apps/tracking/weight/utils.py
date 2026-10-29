"""Weekly weight averages over ISO calendar weeks (Monday to Sunday).

Each week is compared with the latest earlier week that has entries; weeks
without entries are skipped.
"""

import re
from collections import defaultdict
from datetime import date, timedelta

from rest_framework import serializers

from apps.tracking.utils import round1

WEEK_PATTERN = re.compile(r"^(?P<year>[0-9]{4})-W(?P<week>0[1-9]|[1-4][0-9]|5[0-3])$")
PAGE_SIZE = 10


def week_label(iso_year, iso_week):
    return f"{iso_year}-W{iso_week:02d}"


def week_start(iso_year, iso_week, field="before"):
    """Monday of the week; 400 for a week 53 in a year that has only 52."""
    try:
        return date.fromisocalendar(iso_year, iso_week, 1)
    except ValueError as exc:
        raise serializers.ValidationError(
            {field: "Diese Kalenderwoche gibt es nicht."}
        ) from exc


def parse_week(value):
    """'2026-W40' → (2026, 40)."""
    match = WEEK_PATTERN.match(value)

    if match is None:
        raise serializers.ValidationError(
            {"before": "Gib die Woche im Format JJJJ-Www an, z. B. 2026-W40."}
        )

    week = int(match["year"]), int(match["week"])
    week_start(*week)

    return week


def trend(change):
    if change is None:
        return None

    if change > 0:
        return "up"

    if change < 0:
        return "down"

    return "same"


def summarize_weeks(entries):
    """All weeks with entries, newest first, each with its comparison week."""
    grouped = defaultdict(list)

    for entry in entries:
        grouped[tuple(entry.measured_on.isocalendar()[:2])].append(entry)

    weeks = []

    for iso_year, iso_week in sorted(grouped, reverse=True):
        week_entries = sorted(grouped[iso_year, iso_week], key=lambda e: e.measured_on)
        monday = date.fromisocalendar(iso_year, iso_week, 1)

        weeks.append(
            {
                "iso_year": iso_year,
                "iso_week": iso_week,
                "week_start": monday,
                "week_end": monday + timedelta(days=6),
                "average_kg": round1(
                    sum(e.weight_kg for e in week_entries) / len(week_entries)
                ),
                "entries_count": len(week_entries),
                "entries": week_entries,
            }
        )

    for week, previous in zip(weeks, [*weeks[1:], None]):
        change = None if previous is None else week["average_kg"] - previous["average_kg"]
        week["change_kg"] = change
        week["trend"] = trend(change)
        week["previous_week"] = previous

    return weeks

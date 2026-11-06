"""Paging over ISO calendar weeks with entries, shared by the food and weight diaries.

Both lists show five weeks with entries at a time, newest first. ?before=2026-W40 continues
after that week, ?from= and ?to= (days) keep the weeks that overlap the range. total_weeks
counts every week of the range, so the frontend knows whether loading more makes sense.
"""

import re
from datetime import date

from rest_framework import serializers

PAGE_SIZE = 5

WEEK_PATTERN = re.compile(r"^(?P<year>[0-9]{4})-W(?P<week>0[1-9]|[1-4][0-9]|5[0-3])$")


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


def date_param(params, field):
    value = params.get(field)

    if not value:
        return None

    try:
        return serializers.DateField().to_internal_value(value)
    except serializers.ValidationError as exc:
        raise serializers.ValidationError({field: exc.detail}) from exc


def date_range(params):
    """from and to of the query, each optional; to must not lie before from."""
    first = date_param(params, "from")
    last = date_param(params, "to")

    if first and last and last < first:
        raise serializers.ValidationError({"to": ["Darf nicht vor from liegen."]})

    return first, last


def in_range(weeks, first, last):
    """Weeks that share at least one day with the range."""
    return [
        week
        for week in weeks
        if (first is None or week["week_end"] >= first)
        and (last is None or week["week_start"] <= last)
    ]


def page_of_weeks(weeks, params, serializer_class):
    """One page of weeks (newest first, each with iso_year, iso_week, week_start, week_end)."""
    first, last = date_range(params)
    weeks = in_range(weeks, first, last)
    total = len(weeks)
    before = params.get("before")

    if before:
        before_week = parse_week(before)
        weeks = [w for w in weeks if (w["iso_year"], w["iso_week"]) < before_week]

    page = weeks[:PAGE_SIZE]
    has_more = len(weeks) > PAGE_SIZE

    return {
        "results": serializer_class(page, many=True).data,
        "next_before": (
            week_label(page[-1]["iso_year"], page[-1]["iso_week"]) if has_more else None
        ),
        "total_weeks": total,
    }

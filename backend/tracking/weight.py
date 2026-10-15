"""Weight over a period: measurements, ISO week averages and key figures.

Weeks follow ISO 8601 (Monday to Sunday). A week's average uses only the days
that have a measurement. The change of a week is the difference to the average
of the calendar week before, None if that week has no measurement.
"""

from collections import defaultdict
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from .models import WeightEntry

PERIODS = {"7": 7, "30": 30, "90": 90, "180": 180, "365": 365, "alle": None}
DEFAULT_PERIOD = "30"

ONE_DECIMAL = Decimal("0.1")
DAYS_PER_WEEK = 7


def round_weight(value):
    return Decimal(value).quantize(ONE_DECIMAL, rounding=ROUND_HALF_UP)


def period_start(end, period):
    """First day of the period ending on ``end``; None for the whole history."""
    days = PERIODS[period]

    return None if days is None else end - timedelta(days=days - 1)


def monday_of(day):
    return day - timedelta(days=day.weekday())


def weeks_of(entries, start, end, today):
    """ISO weeks touching the period, newest first.

    ``entries`` may reach back one week before ``start``; that week only serves
    as the "week before" of the oldest one and isn't returned.
    """
    by_week = defaultdict(list)

    for entry in entries:
        by_week[monday_of(entry.date)].append(entry)

    averages = {
        monday: round_weight(sum(e.weight for e in items) / len(items))
        for monday, items in by_week.items()
    }
    first_monday = monday_of(start) if start else min(by_week, default=None)
    weeks = []

    for monday in sorted(by_week, reverse=True):
        if first_monday is None or monday < first_monday or monday > end:
            continue

        before = averages.get(monday - timedelta(days=DAYS_PER_WEEK))
        year, week, _ = monday.isocalendar()
        sunday = monday + timedelta(days=6)

        weeks.append(
            {
                "year": year,
                "week": week,
                "start": monday,
                "end": sunday,
                "average": averages[monday],
                "change": None if before is None else averages[monday] - before,
                "is_current": monday <= today <= sunday,
                # All of the week, also days before the period: the average uses them.
                "measurements": by_week[monday],
            }
        )

    return weeks


def stats_of(measurements):
    """Start, current, change, change per week and count; None without data."""
    if not measurements:
        return None

    first, last = measurements[0], measurements[-1]
    change = last.weight - first.weight
    days = (last.date - first.date).days
    # Below a week the tempo would be extrapolated from a few days' water weight.
    per_week = (
        round_weight(change / (Decimal(days) / DAYS_PER_WEEK))
        if days >= DAYS_PER_WEEK
        else None
    )

    return {
        "start": first.weight,
        "current": last.weight,
        "change": change,
        "per_week": per_week,
        "count": len(measurements),
    }


def weight_overview(user, period, end, today):
    start = period_start(end, period)
    entries = WeightEntry.objects.filter(owner=user, date__lte=end)

    if start is not None:
        # One more week, for the change of the oldest week in the period.
        entries = entries.filter(date__gte=monday_of(start) - timedelta(days=7))

    entries = list(entries.order_by("date"))
    measurements = [e for e in entries if start is None or e.date >= start]
    latest = WeightEntry.objects.filter(owner=user).order_by("-date").first()

    return {
        "period": period,
        "start": start,
        "end": end,
        "latest": latest,
        "measurements": measurements,
        "weeks": weeks_of(entries, start, end, today),
        "stats": stats_of(measurements),
    }

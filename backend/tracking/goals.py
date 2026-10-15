"""Daily goals: the version that applies to a day, and the hint that the weight
has moved away from the one the goal was calculated with."""

from django.db import transaction
from django.utils import timezone

from .models import BodyData, DailyGoal, WeightEntry
from .weight import monday_of, round_weight

# From this difference between the current week's average and the weight of the
# calculation on, a new calculation probably fits better. Only a hint.
WEIGHT_CHANGE_HINT = 2


def goal_on(user, day):
    """The goal version valid on ``day``; None before the first one."""
    return (
        DailyGoal.objects.filter(owner=user, valid_from__lte=day)
        .order_by("-valid_from", "-id")
        .first()
    )


def goals_for(user, day):
    goal = goal_on(user, day)

    if goal is None:
        return None

    return {
        "kcal": goal.kcal,
        "protein": goal.protein,
        "carbs": goal.carbs,
        "fat": goal.fat,
    }


def current_week_average(user):
    """Average of the newest ISO week that has measurements."""
    latest = WeightEntry.objects.filter(owner=user).order_by("-date").first()

    if latest is None:
        return None

    monday = monday_of(latest.date)
    weights = list(
        WeightEntry.objects.filter(owner=user, date__gte=monday).values_list(
            "weight", flat=True
        )
    )

    return round_weight(sum(weights) / len(weights))


def weight_change(user, goal):
    if goal is None or goal.weight is None:
        return None

    average = current_week_average(user)

    if average is None:
        return None

    change = average - goal.weight

    return change if abs(change) >= WEIGHT_CHANGE_HINT else None


def goal_overview(user, today=None):
    today = today or timezone.localdate()
    current = goal_on(user, today)
    latest_weight = WeightEntry.objects.filter(owner=user).order_by("-date").first()

    return {
        "current": current,
        "previous": (
            DailyGoal.objects.filter(owner=user, valid_from__lt=today)
            .order_by("-valid_from", "-id")
            .first()
        ),
        "last_calculated": (
            DailyGoal.objects.filter(owner=user, source=DailyGoal.Source.CALCULATED)
            .order_by("-valid_from", "-id")
            .first()
        ),
        "body": BodyData.objects.filter(owner=user).first(),
        "latest_weight": latest_weight,
        "weight_change": weight_change(user, current),
        "today": today,
    }


@transaction.atomic
def save_goal(user, goal, body=None, record_weight=False, today=None):
    """Saves a goal version valid from today, with the inputs it came from.

    Earlier versions of today stay but no longer apply (the newest wins).

    ``body`` updates only the fields it names. With ``record_weight`` the
    goal's weight becomes today's measurement (replacing one that exists).
    """
    today = today or timezone.localdate()

    if body is not None:
        body = dict(body)

        if "age" in body:
            body["age_given_on"] = today if body["age"] is not None else None

        BodyData.objects.update_or_create(owner=user, defaults=body)

    DailyGoal.objects.create(owner=user, valid_from=today, **goal)

    if record_weight and goal.get("weight") is not None:
        WeightEntry.objects.update_or_create(
            owner=user, date=today, defaults={"weight": goal["weight"]}
        )

from django.dispatch import receiver

from accounts.signals import (
    health_data_consent_revoked,
    health_data_summary,
    personal_data_export,
)

from .models import BodyData, DailyGoal, DiaryEntry, Meal, WeightEntry


@receiver(health_data_consent_revoked)
def delete_health_data(sender, user, **kwargs):
    """Body data, goals, diary and weight are health data: without consent they go.

    Own meals stay. A meal is a combination of foods like a recipe; what was
    eaten when is only in the diary.
    """
    DiaryEntry.objects.filter(owner=user).delete()
    WeightEntry.objects.filter(owner=user).delete()
    DailyGoal.objects.filter(owner=user).delete()
    BodyData.objects.filter(owner=user).delete()


@receiver(health_data_summary)
def summarize_health_data(sender, user, **kwargs):
    return {
        "diary_entries": DiaryEntry.objects.active().filter(owner=user).count(),
        "weight_entries": WeightEntry.objects.filter(owner=user).count(),
        "goals": DailyGoal.objects.filter(owner=user).count(),
        "body_data": BodyData.objects.filter(owner=user).count(),
    }


def nutrient_values(values):
    return {name: round(value, 1) for name, value in values.items()}


@receiver(personal_data_export)
def export_tracking_data(sender, user, **kwargs):
    body = BodyData.objects.filter(owner=user).first()
    entries = (
        DiaryEntry.objects.active()
        .filter(owner=user)
        .prefetch_related("items")
        .order_by("date", "created_at")
    )
    meals = Meal.objects.filter(owner=user).prefetch_related("items__food")

    return {
        "body_data": body
        and {
            "sex": body.sex,
            "age": body.age,
            "age_given_on": body.age_given_on,
            "height": body.height,
            "steps": body.steps,
            "workouts": body.workouts,
            "goal": body.goal,
        },
        "daily_goals": [
            {
                "valid_from": goal.valid_from,
                "source": goal.source,
                "kcal": goal.kcal,
                "protein": goal.protein,
                "carbs": goal.carbs,
                "fat": goal.fat,
                "custom_macros": goal.custom_macros,
                "weight": goal.weight,
            }
            for goal in DailyGoal.objects.filter(owner=user).order_by("valid_from")
        ],
        "diary": [
            {
                "date": entry.date,
                "section": entry.section,
                "kind": entry.kind,
                "name": entry.name,
                "brand": entry.brand,
                "quantity": entry.quantity,
                "unit": entry.unit_name or None,
                "servings": entry.servings,
                "nutrients": nutrient_values(entry.nutrients(entry.items.all())),
            }
            for entry in entries
        ],
        "weight": [
            {"date": entry.date, "weight": entry.weight}
            for entry in WeightEntry.objects.filter(owner=user).order_by("date")
        ],
        "meals": [
            {
                "name": meal.name,
                "foods": [
                    {
                        "name": item.food.name,
                        "brand": item.food.brand,
                        "amount": item.amount,
                        "basis": item.food.basis,
                    }
                    for item in meal.items.all()
                ],
            }
            for meal in meals
        ],
    }

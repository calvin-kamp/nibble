from apps.accounts.models import BodyProfile

from .models import GoalSetting, Meal, NutritionEntry, WeightEntry


def delete_tracking_data(profile):
    """Revoking the consent deletes all health data for good: tracking, goal history,
    meals and the body data. The consent history stays."""
    for model in (WeightEntry, NutritionEntry, Meal, GoalSetting, BodyProfile):
        model.objects.filter(profile=profile).delete()

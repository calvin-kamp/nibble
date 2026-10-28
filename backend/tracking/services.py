from .models import BodyProfile, GoalSetting, Meal, TrackingEntry, WeightEntry


def delete_tracking_data(profile):
    """Revoking the consent deletes all health data for good: tracking, goal history,
    meals with their notes and the body data. The consent history stays."""
    for model in (WeightEntry, TrackingEntry, Meal, GoalSetting, BodyProfile):
        model.objects.filter(profile=profile).delete()

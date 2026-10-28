from accounts.models import User
from foods.models import FoodProduct
from recipes.models import Recipe
from tracking.models import TrackingEntry

CACHE_KEY = "public_stats"
# Counting the entry table on every landing page visit would be wasteful; a few minutes old is fine.
CACHE_SECONDS = 10 * 60


def collect_stats():
    return {
        # Accounts awaiting deletion have already said goodbye
        "users": User.objects.filter(
            is_active=True, is_staff=False, deletion_scheduled_for__isnull=True
        ).count(),
        "recipes": Recipe.objects.filter(status=Recipe.Status.APPROVED).count(),
        "foods": FoodProduct.objects.count(),
        "entries": TrackingEntry.objects.count(),
    }

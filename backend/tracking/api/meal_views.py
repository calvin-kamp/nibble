from django.db.models import Prefetch
from rest_framework import viewsets

from tracking.models import Meal, MealItem

from .meal_serializers import MealSerializer


class MealViewSet(viewsets.ModelViewSet):
    """The user's own meals; other people's meals answer with 404.

    GET /meals/ lists all of them, not paginated. PUT replaces name and foods;
    days already logged keep their own copy (see DiaryEntryItem).
    """

    serializer_class = MealSerializer
    pagination_class = None
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        return Meal.objects.filter(owner=self.request.user).prefetch_related(
            Prefetch(
                "items",
                queryset=MealItem.objects.select_related("food").prefetch_related(
                    "food__units"
                ),
            )
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

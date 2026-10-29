from django.urls import path
from rest_framework import routers

from .views import (
    DaySummaryView,
    EntryCreateView,
    EntryDetailView,
    EntryFromMealView,
    GoalView,
    MealViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"meals", MealViewSet, basename="meal")

urlpatterns = [
    path("goal", GoalView.as_view(), name="goal"),
    path("entries", EntryCreateView.as_view(), name="entry_create"),
    path("entries/from-meal", EntryFromMealView.as_view(), name="entry_from_meal"),
    path("entries/<int:pk>", EntryDetailView.as_view(), name="entry_detail"),
    path("days/<str:date>", DaySummaryView.as_view(), name="day_summary"),
    *router.urls,
]

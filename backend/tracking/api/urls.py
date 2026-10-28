from django.urls import path
from rest_framework import routers

from .views import (
    BodyProfileView,
    DaySummaryView,
    EntryCreateView,
    EntryDetailView,
    EntryFromMealView,
    GoalView,
    MealViewSet,
    WeekDetailView,
    WeekListView,
    WeightDetailView,
    WeightListView,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"meals", MealViewSet, basename="meal")

urlpatterns = [
    path("goal", GoalView.as_view(), name="goal"),
    path("body", BodyProfileView.as_view(), name="body"),
    path("entries", EntryCreateView.as_view(), name="entry_create"),
    path("entries/from-meal", EntryFromMealView.as_view(), name="entry_from_meal"),
    path("entries/<int:pk>", EntryDetailView.as_view(), name="entry_detail"),
    path("days/<str:date>", DaySummaryView.as_view(), name="day_summary"),
    path("weights", WeightListView.as_view(), name="weights"),
    path("weights/weeks", WeekListView.as_view(), name="weight_weeks"),
    path(
        "weights/weeks/<int:iso_year>/<int:iso_week>",
        WeekDetailView.as_view(),
        name="weight_week_detail",
    ),
    path("weights/<int:pk>", WeightDetailView.as_view(), name="weight_detail"),
    *router.urls,
]

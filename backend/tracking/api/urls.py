from django.urls import path, register_converter
from rest_framework import routers

from .converters import IsoDateConverter
from .diary_views import (
    DiaryCalendarView,
    DiaryDayView,
    DiaryEntryViewSet,
    DiarySummaryView,
    RecentFoodsView,
)
from .goal_views import GoalView
from .meal_views import MealViewSet
from .weight_views import WeightDayView, WeightOverviewView

register_converter(IsoDateConverter, "isodate")

diary_router = routers.SimpleRouter()
diary_router.register(r"entries", DiaryEntryViewSet, basename="diary-entry")

meal_router = routers.SimpleRouter()
meal_router.register(r"", MealViewSet, basename="meal")

diary_urlpatterns = [
    path("days/<isodate:date>/", DiaryDayView.as_view(), name="diary-day"),
    path(
        "days/<isodate:date>/summary/",
        DiarySummaryView.as_view(),
        name="diary-summary",
    ),
    path("calendar/", DiaryCalendarView.as_view(), name="diary-calendar"),
    path("recent/", RecentFoodsView.as_view(), name="diary-recent"),
    *diary_router.urls,
]

meal_urlpatterns = meal_router.urls

weight_urlpatterns = [
    path("", WeightOverviewView.as_view(), name="weight-overview"),
    path("<isodate:date>/", WeightDayView.as_view(), name="weight-day"),
]

goal_urlpatterns = [
    path("", GoalView.as_view(), name="goals"),
]

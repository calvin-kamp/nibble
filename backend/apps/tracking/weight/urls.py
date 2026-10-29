from django.urls import path

from .views import WeekDetailView, WeekListView, WeightDetailView, WeightListView

urlpatterns = [
    path("weights", WeightListView.as_view(), name="weights"),
    path("weights/weeks", WeekListView.as_view(), name="weight_weeks"),
    path(
        "weights/weeks/<int:iso_year>/<int:iso_week>",
        WeekDetailView.as_view(),
        name="weight_week_detail",
    ),
    path("weights/<int:pk>", WeightDetailView.as_view(), name="weight_detail"),
]

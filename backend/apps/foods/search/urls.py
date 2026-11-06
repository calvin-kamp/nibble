from django.urls import path

from .views import FoodReportView, FoodSearchView

urlpatterns = [
    path("search", FoodSearchView.as_view(), name="food_search"),
    path("<str:code>/report", FoodReportView.as_view(), name="food_report"),
]

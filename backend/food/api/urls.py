from django.urls import path

from .views import FoodBarcodeView, FoodDetailView, FoodSearchView

urlpatterns = [
    path("", FoodSearchView.as_view(), name="food-search"),
    path("<int:pk>/", FoodDetailView.as_view(), name="food-detail"),
    path("barcode/<str:barcode>/", FoodBarcodeView.as_view(), name="food-barcode"),
]

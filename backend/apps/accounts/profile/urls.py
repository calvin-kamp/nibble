from django.urls import path

from .views import BodyProfileView, ProfileView

urlpatterns = [
    path("profile", ProfileView.as_view(), name="profile"),
    path("tracking/body", BodyProfileView.as_view(), name="body"),
]

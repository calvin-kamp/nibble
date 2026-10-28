from django.urls import path

from .views import ProfileView, UsernameAvailabilityView

urlpatterns = [
    path("profile", ProfileView.as_view(), name="profile"),
    path(
        "profile/username-availability",
        UsernameAvailabilityView.as_view(),
        name="username_availability",
    ),
]

from django.urls import path

from .views import OnboardingCompleteView, OnboardingView

urlpatterns = [
    path("onboarding", OnboardingView.as_view(), name="onboarding"),
    path(
        "onboarding/complete",
        OnboardingCompleteView.as_view(),
        name="onboarding_complete",
    ),
]

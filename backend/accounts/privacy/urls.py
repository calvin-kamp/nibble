from django.urls import path

from .views import ConsentView

urlpatterns = [
    path("privacy/consent", ConsentView.as_view(), name="privacy_consent"),
]

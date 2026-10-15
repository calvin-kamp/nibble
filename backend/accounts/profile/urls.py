from django.urls import path

from .views import ConsentView, ExportView, ProfileView

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path("consent/", ConsentView.as_view(), name="profile-consent"),
    path("export/", ExportView.as_view(), name="profile-export"),
]

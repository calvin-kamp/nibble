from django.urls import path

from .views import AccountDeletionView, AccountExportView

urlpatterns = [
    path("deletion", AccountDeletionView.as_view(), name="account_deletion"),
    path("export", AccountExportView.as_view(), name="account_export"),
]

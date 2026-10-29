"""
URL configuration for config project.

Every endpoint of the OpenAPI spec lives at the root, without trailing slash.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("stats", include("stats.api.urls")),
    path("auth/", include("accounts.auth.urls")),
    path("account/", include("accounts.account.urls")),
    path("", include("accounts.onboarding.urls")),
    path("", include("accounts.profile.urls")),
    path("", include("accounts.privacy.urls")),
    path("", include("recipes.api.urls")),
    path("moderation/", include("recipes.moderation.urls")),
    path("foods/", include("foods.api.urls")),
    path("tracking/", include("tracking.api.urls")),
    # Recipe images. No separate web server serves the media volume, so Django does.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

handler404 = "config.views.not_found"
handler500 = "config.views.server_error"

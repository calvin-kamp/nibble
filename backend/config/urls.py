"""
URL configuration for config project.

Every endpoint of the OpenAPI spec lives at the root, without trailing slash.
"""

from django.contrib import admin
from django.urls import include, path, re_path

from apps.recipes.media import recipe_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("stats", include("apps.stats.api.urls")),
    path("auth/", include("apps.accounts.auth.urls")),
    path("account/", include("apps.accounts.account.urls")),
    path("", include("apps.accounts.onboarding.urls")),
    path("", include("apps.accounts.profile.urls")),
    path("", include("apps.accounts.privacy.urls")),
    path("", include("apps.recipes.catalog.urls")),
    path("moderation/", include("apps.recipes.moderation.urls")),
    path("moderation/", include("apps.foods.moderation.urls")),
    path("foods/", include("apps.foods.search.urls")),
    path("tracking/", include("apps.tracking.nutrition.urls")),
    path("tracking/", include("apps.tracking.weight.urls")),
    # Recipe images. Django serves them, recipes under review only to author and staff.
    re_path(r"^media/(?P<path>recipes/.+)$", recipe_media, name="recipe_media"),
]

handler404 = "config.views.not_found"
handler500 = "config.views.server_error"

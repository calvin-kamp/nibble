"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from tracking.api.urls import (
    diary_urlpatterns,
    goal_urlpatterns,
    meal_urlpatterns,
    weight_urlpatterns,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.auth.urls")),
    path("profile/", include("accounts.profile.urls")),
    path("recipes/", include("recipes.api.urls")),
    path("foods/", include("food.api.urls")),
    path("diary/", include(diary_urlpatterns)),
    path("meals/", include(meal_urlpatterns)),
    path("weight/", include(weight_urlpatterns)),
    path("goals/", include(goal_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

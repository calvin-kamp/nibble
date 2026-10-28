from rest_framework import routers

from .views import RecipeViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"recipes", RecipeViewSet, basename="recipe")

urlpatterns = router.urls

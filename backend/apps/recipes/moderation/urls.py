from rest_framework import routers

from .views import SubmissionViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"submissions", SubmissionViewSet, basename="submission")

urlpatterns = router.urls

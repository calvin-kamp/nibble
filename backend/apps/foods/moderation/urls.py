from rest_framework import routers

from .views import FoodViewSet, MissingBarcodeViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"missing-barcodes", MissingBarcodeViewSet, basename="missing_barcode")

router.register(r"foods", FoodViewSet, basename="moderation_food")

urlpatterns = router.urls

from django.utils import timezone

from apps.foods.models import FoodProduct
from config.testing import ApiTestCase

OATS = "4000000000001"
MILK = "4000000000002"


class TrackingTestCase(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(username="gurke", consent=True)
        self.login(self.user)
        self.today = timezone.localdate()
        now = timezone.now()

        FoodProduct.objects.create(
            code=OATS,
            name="Haferflocken",
            brand="Kölln",
            kcal_per_100=372,
            protein_per_100=13.5,
            carbs_per_100=58.7,
            fat_per_100=7,
            serving_quantity=40,
            imported_at=now,
        )
        FoodProduct.objects.create(
            code=MILK,
            name="Milch 1,5 %",
            base_unit="ml",
            kcal_per_100=47,
            protein_per_100=3.4,
            carbs_per_100=4.9,
            fat_per_100=1.5,
            imported_at=now,
        )

    def track(self, code=OATS, amount=50, unit="g", **extra):
        return self.client.post(
            "/tracking/entries",
            {
                "off_code": code,
                "amount": amount,
                "unit": unit,
                "consumed_on": str(extra.pop("consumed_on", self.today)),
                "meal_type": extra.pop("meal_type", "breakfast"),
            },
        )

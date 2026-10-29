from django.db.models import Q
from rest_framework import generics

from apps.foods.models import FoodProduct
from config.pagination import PagePagination

from .serializers import FoodProductSerializer, FoodSearchSerializer


class FoodSearchView(generics.ListAPIView):
    serializer_class = FoodProductSerializer
    pagination_class = PagePagination
    filter_backends = []

    def get_queryset(self):
        serializer = FoodSearchSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data.get("q")
        barcode = serializer.validated_data.get("barcode")
        queryset = FoodProduct.objects.all()

        if barcode:
            queryset = queryset.filter(code=barcode)

        # Every word has to appear in the name or the brand, e.g. "yfood vanilla"
        # finds "smooth vanilla" by yfood.
        for word in (query or "").split():
            queryset = queryset.filter(Q(name__icontains=word) | Q(brand__icontains=word))

        return queryset.order_by("name", "code")

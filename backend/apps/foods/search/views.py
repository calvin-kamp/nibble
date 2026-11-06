from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.foods.models import FoodProduct
from apps.foods.services import record_missing_barcode, report_product
from config.pagination import PagePagination
from config.throttles import UserThrottle

from .serializers import FoodProductSerializer, FoodReportInputSerializer, FoodSearchSerializer


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
        self.barcode_only = barcode if barcode and not query else None

        if barcode:
            queryset = queryset.filter(code=barcode)

        if code := serializer.validated_data.get("code"):
            queryset = queryset.filter(code=code)

        # Every word has to appear in the name or the brand, e.g. "yfood vanilla"
        # finds "smooth vanilla" by yfood.
        for word in (query or "").split():
            queryset = queryset.filter(Q(name__icontains=word) | Q(brand__icontains=word))

        # Loose foods first: "Banane" should find the banana before banana chips.
        return queryset.order_by("-generic", "name", "code")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Staff add missing products in the admin; the list there only holds the barcode.
        if self.barcode_only and not response.data["count"]:
            record_missing_barcode(self.barcode_only)

        return response


class FoodReportThrottle(UserThrottle):
    scope = "food_report"


class FoodReportView(APIView):
    """A user says something about a product is wrong; staff check it in the admin."""

    throttle_classes = [FoodReportThrottle]

    def post(self, request, code):
        product = get_object_or_404(FoodProduct, code=code)
        serializer = FoodReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report_product(product, **serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

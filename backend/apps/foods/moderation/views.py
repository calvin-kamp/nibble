from django.db.models import Count, Max, Prefetch
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.foods import off, services
from apps.foods.models import FoodProduct, FoodReport, MissingBarcode
from apps.foods.search.serializers import FoodProductSerializer
from config.pagination import PagePagination
from config.permissions import IsStaff

from .serializers import (
    FoodProductInputSerializer,
    FoodProductUpdateSerializer,
    MissingBarcodeDetailSerializer,
    MissingBarcodeSerializer,
    ModerationProductSerializer,
    ReportedProductSerializer,
)


class MissingBarcodeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Staff only; barcodes nobody found, most searched first."""

    permission_classes = [IsStaff]
    pagination_class = PagePagination
    queryset = MissingBarcode.objects.order_by("-lookups", "-last_searched_at", "code")
    serializer_class = MissingBarcodeSerializer
    lookup_value_regex = r"[0-9]{8,14}"

    def retrieve(self, request, *args, **kwargs):
        missing = self.get_object()
        context = {
            **self.get_serializer_context(),
            "off_product": off.fetch_product(missing.code),
        }

        return Response(MissingBarcodeDetailSerializer(missing, context=context).data)

    @action(detail=True, methods=["post"])
    def product(self, request, pk=None):
        """Adds the product here and on Open Food Facts, the barcode leaves the list."""
        missing = self.get_object()
        serializer = FoodProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product, synced = services.add_product(
            {**serializer.validated_data, "code": missing.code}, request.user.profile
        )

        return Response(
            {
                "product": FoodProductSerializer(product).data,
                "off_synced": synced,
            },
            status=status.HTTP_201_CREATED,
        )


class FoodViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Staff only; corrects products, lists reported ones and adds generic foods."""

    permission_classes = [IsStaff]
    pagination_class = PagePagination
    queryset = FoodProduct.objects.prefetch_related("reports")
    serializer_class = ModerationProductSerializer
    # Barcode, or the code of a generic food, e.g. "n00002".
    lookup_value_regex = r"[0-9]{8,14}|n[0-9]{5}"

    @action(detail=False, methods=["get"])
    def reported(self, request):
        """Products with open reports, the most reported first."""
        queryset = (
            FoodProduct.objects.filter(reports__isnull=False)
            .annotate(report_count=Count("reports"), last_reported_at=Max("reports__created_at"))
            .prefetch_related(Prefetch("reports", queryset=FoodReport.objects.only("reason", "product")))
            .order_by("-report_count", "-last_reported_at", "code")
        )
        page = self.paginate_queryset(queryset)

        return self.get_paginated_response(ReportedProductSerializer(page, many=True).data)

    def update(self, request, *args, **kwargs):
        """Saves the correction here and, for products with a barcode, on Open Food Facts."""
        product = self.get_object()
        serializer = FoodProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        synced = services.update_product(product, serializer.validated_data, request.user.profile)
        product.refresh_from_db()

        return Response({"product": ModerationProductSerializer(product).data, "off_synced": synced})

    @action(detail=True, methods=["delete"])
    def reports(self, request, pk=None):
        """The reports were wrong; the product stays as it is."""
        self.get_object().reports.all().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def generic(self, request):
        """Adds a loose food without a barcode, e.g. a banana. Stays in nibble only."""
        serializer = FoodProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = services.add_generic_product(serializer.validated_data)

        return Response(ModerationProductSerializer(product).data, status=status.HTTP_201_CREATED)

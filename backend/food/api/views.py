from django.db.models import Case, IntegerField, Q, Value, When
from django.http import Http404
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from food.models import Food

from .serializers import FoodSerializer

SEARCH_MIN_LENGTH = 2
SEARCH_MAX_RESULTS = 20


def barcode_variants(code):
    """The same product may be stored as UPC-A (12 digits) or as EAN-13 with a 0."""
    variants = {code}

    if len(code) == 12:
        variants.add(f"0{code}")
    elif len(code) == 13 and code.startswith("0"):
        variants.add(code[1:])

    return variants


class FoodSearchView(generics.ListAPIView):
    """GET /foods/?suche=hafer – at most 20 hits, not paginated.

    Every word must appear in the name or the brand ("hafer kölln"). Names
    starting with the term come first, then the products scanned most often on
    Open Food Facts.
    """

    serializer_class = FoodSerializer
    pagination_class = None

    def get_queryset(self):
        term = " ".join(self.request.query_params.get("suche", "").split())

        if len(term) < SEARCH_MIN_LENGTH:
            raise ValidationError(
                {"suche": [f"Gib mindestens {SEARCH_MIN_LENGTH} Zeichen ein."]}
            )

        queryset = Food.objects.prefetch_related("units")

        for word in term.split(" "):
            queryset = queryset.filter(
                Q(name__icontains=word) | Q(brand__icontains=word)
            )

        return queryset.annotate(
            rank=Case(
                When(name__istartswith=term, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("rank", "-popularity", "name", "brand")[:SEARCH_MAX_RESULTS]


class FoodDetailView(generics.RetrieveAPIView):
    """GET /foods/12/"""

    serializer_class = FoodSerializer
    queryset = Food.objects.prefetch_related("units")


class FoodBarcodeView(generics.RetrieveAPIView):
    """GET /foods/barcode/4009249001256/ – the product with this code, or 404."""

    serializer_class = FoodSerializer

    def get_object(self):
        code = self.kwargs["barcode"]
        food = (
            Food.objects.prefetch_related("units")
            .filter(barcode__in=barcode_variants(code))
            .first()
        )

        if food is None:
            raise Http404

        return food

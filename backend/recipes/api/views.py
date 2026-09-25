from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient

from .filters import RecipeFilter
from .pagination import RecipePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TAXONOMY_FIELDS,
    RecipeDetailSerializer,
    RecipeImageSerializer,
    RecipeListSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(*TAXONOMY_FIELDS).order_by("-id")

        if self.action == "list":
            return queryset

        return queryset.prefetch_related(
            Prefetch(
                "ingredients",
                queryset=RecipeIngredient.objects.select_related("ingredient"),
            ),
            "cooking_steps",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer

        return RecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        instance.image.delete(save=False)
        instance.delete()

    @action(
        detail=True,
        methods=["put", "delete"],
        parser_classes=[MultiPartParser],
        serializer_class=RecipeImageSerializer,
    )
    def image(self, request, pk=None):
        """PUT replaces the image (multipart, field "image"), DELETE removes it."""
        recipe = self.get_object()
        previous = recipe.image.name

        if request.method == "DELETE":
            recipe.image.delete(save=True)

            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = RecipeImageSerializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if previous:
            recipe.image.storage.delete(previous)

        detail = RecipeDetailSerializer(recipe, context=self.get_serializer_context())

        return Response(detail.data)

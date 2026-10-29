from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.recipes import services
from apps.recipes.models import Recipe, RecipeSubmission, SavedRecipe
from config.pagination import PagePagination

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeDetailSerializer,
    RecipeImageSerializer,
    RecipeInputSerializer,
    RecipeListSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = PagePagination
    lookup_value_regex = r"\d+"
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.visible_to(user).annotate(
            revision_pending=Exists(
                RecipeSubmission.objects.filter(
                    recipe=OuterRef("pk"),
                    kind=RecipeSubmission.Kind.REVISION,
                    status=Recipe.Status.PENDING,
                )
            )
        )

        if user.is_authenticated:
            queryset = queryset.annotate(
                saved=Exists(
                    SavedRecipe.objects.filter(
                        recipe=OuterRef("pk"), profile=user.profile
                    )
                )
            )

        if self.action != "list":
            queryset = queryset.prefetch_related("ingredients", "steps")

        return queryset.order_by("-created_at", "-id")

    def filter_queryset(self, queryset):
        # get_object() goes through here too; detail views must not be filtered.
        if self.action != "list":
            return queryset

        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer

        return RecipeDetailSerializer

    def get_permissions(self):
        # Saving works for every visible approved recipe, also foreign ones.
        if self.action == "saved":
            return [IsAuthenticated()]

        return super().get_permissions()

    def detail_response(self, recipe, status_code=status.HTTP_200_OK):
        """Reloads the recipe with annotations, so the response is complete."""
        recipe = self.get_queryset().get(pk=recipe.pk)

        return Response(
            RecipeDetailSerializer(recipe, context=self.get_serializer_context()).data,
            status=status_code,
        )

    def create(self, request, *args, **kwargs):
        serializer = RecipeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = services.create_recipe(
            request.user.profile, serializer.validated_data
        )

        return self.detail_response(recipe, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        serializer = RecipeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.update_recipe(recipe, serializer.validated_data)

        return self.detail_response(recipe)

    def perform_destroy(self, instance):
        services.delete_recipe(instance)

    @action(detail=True, methods=["put", "delete"], parser_classes=[MultiPartParser])
    def image(self, request, pk=None):
        """PUT replaces the image (multipart, field "image"), DELETE removes it."""
        recipe = self.get_object()

        if request.method == "DELETE":
            services.remove_image(recipe)
        else:
            serializer = RecipeImageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            services.replace_image(recipe, serializer.validated_data["image"])

        return self.detail_response(recipe)

    @action(detail=True, methods=["put", "delete"])
    def saved(self, request, pk=None):
        recipe = self.get_object()

        if recipe.status != Recipe.Status.APPROVED:
            raise NotFound()

        if request.method == "DELETE":
            SavedRecipe.objects.filter(
                profile=request.user.profile, recipe=recipe
            ).delete()
        else:
            SavedRecipe.objects.get_or_create(profile=request.user.profile, recipe=recipe)

        return Response(status=status.HTTP_204_NO_CONTENT)

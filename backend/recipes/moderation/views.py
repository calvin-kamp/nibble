from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from config.pagination import PagePagination
from recipes.models import Recipe, RecipeSubmission
from recipes.services import submissions

from .serializers import (
    RejectSerializer,
    SubmissionDetailSerializer,
    SubmissionSummarySerializer,
)


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Staff only; oldest submissions first."""

    permission_classes = [IsAdminUser]
    pagination_class = PagePagination
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        queryset = RecipeSubmission.objects.select_related(
            "recipe__author", "reviewed_by"
        ).order_by("submitted_at", "id")

        if self.action == "list":
            queryset = queryset.filter(status=self.status_param())

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return SubmissionSummarySerializer

        return SubmissionDetailSerializer

    def status_param(self):
        field = serializers.ChoiceField(choices=Recipe.Status)
        value = self.request.query_params.get("status", Recipe.Status.PENDING)

        try:
            return field.run_validation(value)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({"status": exc.detail}) from exc

    def detail_response(self, submission):
        return Response(
            SubmissionDetailSerializer(
                submission, context=self.get_serializer_context()
            ).data
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        submission = submissions.approve(self.get_object(), request.user.profile)

        return self.detail_response(submission)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = submissions.reject(
            self.get_object(),
            request.user.profile,
            serializer.validated_data["reason"],
        )

        return self.detail_response(submission)

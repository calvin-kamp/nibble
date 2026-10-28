from rest_framework import serializers

from recipes.api.serializers import RecipeInputSerializer, absolute_url, author_data
from recipes.models import RecipeSubmission


class SubmissionSummarySerializer(serializers.ModelSerializer):
    recipe_id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = RecipeSubmission
        fields = ("id", "recipe_id", "kind", "status", "name", "author", "submitted_at")

    def get_name(self, submission):
        return submission.content.get("name")

    def get_author(self, submission):
        return author_data(submission.recipe.author)


class SubmissionDetailSerializer(SubmissionSummarySerializer):
    content = serializers.JSONField(read_only=True)
    current = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    reviewed_by = serializers.SerializerMethodField()

    class Meta(SubmissionSummarySerializer.Meta):
        fields = SubmissionSummarySerializer.Meta.fields + (
            "content",
            "current",
            "image_url",
            "rejection_reason",
            "reviewed_by",
            "reviewed_at",
        )

    def get_current(self, submission):
        """The live version for comparison, revisions only."""
        if submission.kind != RecipeSubmission.Kind.REVISION:
            return None

        return RecipeInputSerializer(submission.recipe).data

    def get_image_url(self, submission):
        return absolute_url(self.context.get("request"), submission.effective_image)

    def get_reviewed_by(self, submission):
        return submission.reviewed_by.username if submission.reviewed_by else None


class RejectSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=1000)

from rest_framework import serializers

from accounts.auth.serializers import PasswordField
from recipes.api.serializers import absolute_url
from recipes.models import RecipeSubmission


class DeletionRequestSerializer(serializers.Serializer):
    password = PasswordField()

    def validate_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Das Passwort ist falsch.")

        return value


class DeletionStatusSerializer(serializers.Serializer):
    scheduled_for = serializers.DateTimeField(source="deletion_scheduled_for")


class SubmissionExportSerializer(serializers.ModelSerializer):
    """The user's own submissions; the reviewing moderator stays out of the export."""

    recipe_id = serializers.IntegerField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = RecipeSubmission
        fields = (
            "id",
            "recipe_id",
            "kind",
            "status",
            "submitted_at",
            "reviewed_at",
            "rejection_reason",
            "content",
            "image_action",
            "image_url",
        )

    def get_image_url(self, submission):
        return absolute_url(self.context.get("request"), submission.image)

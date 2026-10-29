from rest_framework import serializers

from apps.accounts.models import ConsentRecord, Profile


class ConsentStateSerializer(serializers.ModelSerializer):
    accepted = serializers.BooleanField(source="consent_accepted", allow_null=True)
    decided_at = serializers.DateTimeField(source="consent_decided_at")
    policy_version = serializers.CharField(source="consent_policy_version")

    class Meta:
        model = Profile
        fields = ("accepted", "decided_at", "policy_version")


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ("accepted", "policy_version", "decided_at")


class ConsentDecisionSerializer(serializers.Serializer):
    """The version is required for revoking, too: the history shows what was revoked."""

    accepted = serializers.BooleanField()
    policy_version = serializers.CharField(
        max_length=32,
        error_messages={"required": "Gib die Version des Datenschutztexts an."},
    )

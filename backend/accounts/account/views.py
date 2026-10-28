from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.services.emails import send_deletion_scheduled_email
from accounts.services.export import build_export

from .serializers import DeletionRequestSerializer, DeletionStatusSerializer
from .throttles import AccountDeletionThrottle, AccountExportThrottle


class AccountDeletionView(APIView):
    """POST starts the 7-day period right away, DELETE takes it back."""

    def get_throttles(self):
        if self.request.method == "POST":
            return [AccountDeletionThrottle()]

        return super().get_throttles()

    def post(self, request):
        serializer = DeletionRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user

        # Asking again keeps the date, the period doesn't start over.
        if user.deletion_scheduled_for is None:
            user.deletion_scheduled_for = (
                timezone.now() + settings.ACCOUNT_DELETION_GRACE_PERIOD
            )
            user.save(update_fields=["deletion_scheduled_for"])
            send_deletion_scheduled_email(user)

        return Response(DeletionStatusSerializer(user).data)

    def delete(self, request):
        user = request.user

        if user.deletion_scheduled_for is None:
            raise NotFound("Es ist keine Löschung geplant.")

        user.deletion_scheduled_for = None
        user.save(update_fields=["deletion_scheduled_for"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountExportView(APIView):
    throttle_classes = [AccountExportThrottle]

    def get(self, request):
        return Response(
            build_export(request),
            headers={"Content-Disposition": 'attachment; filename="export.json"'},
        )

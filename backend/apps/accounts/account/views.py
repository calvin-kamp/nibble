from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import build_export, cancel_deletion, schedule_deletion

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
        schedule_deletion(request.user)

        return Response(DeletionStatusSerializer(request.user).data)

    def delete(self, request):
        user = request.user

        if user.deletion_scheduled_for is None:
            raise NotFound("Es ist keine Löschung geplant.")

        cancel_deletion(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountExportView(APIView):
    throttle_classes = [AccountExportThrottle]

    def get(self, request):
        return Response(
            build_export(request),
            headers={"Content-Disposition": 'attachment; filename="export.json"'},
        )

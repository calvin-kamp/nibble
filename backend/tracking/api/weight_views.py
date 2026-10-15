from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HealthDataConsent
from tracking.models import WeightEntry
from tracking.weight import weight_overview

from .weight_serializers import (
    MeasurementSerializer,
    WeightInputSerializer,
    WeightOverviewSerializer,
    WeightQuerySerializer,
)


class WeightOverviewView(APIView):
    """GET /weight/?zeitraum=30&bis=2026-10-14

    Measurements of the period (oldest first), ISO weeks (newest first), key
    figures and the latest measurement overall (for "Zuletzt 78,6 kg am …").
    """

    def get(self, request):
        query = WeightQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        end = query.validated_data.get("bis") or timezone.localdate()
        overview = weight_overview(
            request.user, query.validated_data["zeitraum"], end, end
        )

        return Response(WeightOverviewSerializer(overview).data)


class WeightDayView(APIView):
    """PUT /weight/2026-10-14/ saves or replaces the day, DELETE removes it."""

    permission_classes = [IsAuthenticated, HealthDataConsent]

    def put(self, request, date):
        data = WeightInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        entry, created = WeightEntry.objects.update_or_create(
            owner=request.user,
            date=date,
            defaults={"weight": data.validated_data["weight"]},
        )

        return Response(
            MeasurementSerializer(entry).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, date):
        get_object_or_404(WeightEntry, owner=request.user, date=date).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

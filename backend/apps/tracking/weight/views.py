from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tracking.mixins import TrackingMixin
from apps.tracking.weight.exceptions import WeightEntryExists
from apps.tracking.weeks import page_of_weeks, week_start
from apps.tracking.weight.utils import summarize_weeks

from .serializers import (
    WeekDetailSerializer,
    WeekSummarySerializer,
    WeightEntrySerializer,
)

WEIGHT_RANGES = {"7d": 7, "14d": 14, "1m": 30, "1y": 365, "all": None}


class WeightListView(TrackingMixin, APIView):
    def get(self, request):
        range_name = request.query_params.get("range", "7d")

        if range_name not in WEIGHT_RANGES:
            raise serializers.ValidationError(
                {"range": f"Erlaubt sind: {', '.join(WEIGHT_RANGES)}."}
            )

        entries = self.profile.weight_entries.order_by("measured_on")
        today = timezone.localdate()
        days = WEIGHT_RANGES[range_name]

        if days is None:
            first = entries.first()
            start = first.measured_on if first else today
        else:
            start = today - timedelta(days=days - 1)

        entries = entries.filter(measured_on__gte=start, measured_on__lte=today)

        return Response(
            {
                "range": range_name,
                "from": start,
                "to": today,
                "results": WeightEntrySerializer(entries, many=True).data,
            }
        )

    def post(self, request):
        serializer = WeightEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_weight(serializer, profile=self.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WeightDetailView(TrackingMixin, generics.GenericAPIView):
    def get_queryset(self):
        return self.profile.weight_entries.all()

    def patch(self, request, pk):
        serializer = WeightEntrySerializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        save_weight(serializer)

        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


def save_weight(serializer, **kwargs):
    """One entry per day: another entry on the same day answers 409."""
    measured_on = serializer.validated_data.get("measured_on")
    instance = serializer.instance
    profile = kwargs.get("profile") or instance.profile

    if measured_on is not None:
        others = profile.weight_entries.filter(measured_on=measured_on)

        if instance is not None:
            others = others.exclude(pk=instance.pk)

        if others.exists():
            raise WeightEntryExists()

    try:
        with transaction.atomic():
            serializer.save(**kwargs)
    except IntegrityError as exc:
        raise WeightEntryExists() from exc


class WeekListView(TrackingMixin, APIView):
    def get(self, request):
        # Comparisons are made over all weeks, the range only picks which ones are listed.
        weeks = summarize_weeks(self.profile.weight_entries.all())

        return Response(
            page_of_weeks(weeks, request.query_params, WeekSummarySerializer)
        )


class WeekDetailView(TrackingMixin, APIView):
    def get(self, request, iso_year, iso_week):
        if not 2000 <= iso_year <= 2100:
            raise serializers.ValidationError(
                {"iso_year": "Das Jahr muss zwischen 2000 und 2100 liegen."}
            )

        week_start(iso_year, iso_week, field="iso_week")
        weeks = summarize_weeks(self.profile.weight_entries.all())
        week = next(
            (
                w
                for w in weeks
                if w["iso_year"] == iso_year and w["iso_week"] == iso_week
            ),
            None,
        )

        if week is None:
            raise NotFound("In dieser Woche gibt es keine Einträge.")

        return Response(WeekDetailSerializer(week).data)

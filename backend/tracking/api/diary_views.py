import calendar
from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HealthDataConsent
from tracking.diary import day_totals, entries_of_day, recent_foods, sections_of
from tracking.goals import goals_for
from tracking.models import DiaryEntry

from .diary_serializers import (
    DiaryDaySerializer,
    DiaryEntryCreateSerializer,
    DiaryEntrySerializer,
    DiaryEntryUpdateSerializer,
    DiarySummarySerializer,
    RecentFoodSerializer,
    recent_food_data,
)


class DiaryDayView(APIView):
    """GET /diary/days/2026-10-14/ – goals, totals and the five sections."""

    def get(self, request, date):
        sections = sections_of(entries_of_day(request.user, date))
        day = {
            "date": date,
            "goals": goals_for(request.user, date),
            "totals": day_totals(sections),
            "sections": sections,
        }

        return Response(DiaryDaySerializer(day).data)


class DiarySummaryView(APIView):
    """GET /diary/days/2026-10-14/summary/ – the dashboard's short form."""

    def get(self, request, date):
        sections = sections_of(entries_of_day(request.user, date))
        summary = {
            "date": date,
            "goals": goals_for(request.user, date),
            "totals": day_totals(sections),
            "sections": [
                {
                    "key": section["key"],
                    "name": section["name"],
                    "count": len(section["entries"]),
                    "kcal": section["totals"]["kcal"],
                }
                for section in sections
            ],
        }

        return Response(DiarySummarySerializer(summary).data)


class DiaryCalendarView(APIView):
    """GET /diary/calendar/?monat=2026-10 – the days of a month with entries."""

    def get(self, request):
        value = request.query_params.get("monat", "")

        try:
            year, month = (int(part) for part in value.split("-"))
            first = date(year, month, 1)
        except ValueError as error:
            raise ValidationError(
                {"monat": ["Erwartet wird z. B. 2026-10."]}
            ) from error

        last = first.replace(day=calendar.monthrange(year, month)[1])
        days = (
            DiaryEntry.objects.active()
            .filter(owner=request.user, date__range=(first, last))
            .values_list("date", flat=True)
            .distinct()
            .order_by("date")
        )

        return Response({"month": value, "days": [day.isoformat() for day in days]})


class RecentFoodsView(APIView):
    """GET /diary/recent/ – up to 20 foods logged last, with their last amount."""

    def get(self, request):
        data = [recent_food_data(entry) for entry in recent_foods(request.user)]

        return Response(RecentFoodSerializer(data, many=True).data)


class DiaryEntryViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """POST /diary/entries/, PATCH and DELETE /diary/entries/<id>/.

    DELETE only marks the entry, POST …/restore/ brings it back ("Rückgängig").
    """

    http_method_names = ["post", "patch", "delete"]
    permission_classes = [IsAuthenticated, HealthDataConsent]

    def get_queryset(self):
        entries = DiaryEntry.objects.filter(owner=self.request.user)

        if self.action != "restore":
            entries = entries.active()

        return entries.select_related("food").prefetch_related("items", "food__units")

    def get_serializer_class(self):
        if self.action == "create":
            return DiaryEntryCreateSerializer

        return DiaryEntryUpdateSerializer

    def respond(self, entry, status_code=status.HTTP_200_OK):
        # Fresh from the database: items and units may have changed on save.
        entry = (
            DiaryEntry.objects.select_related("food")
            .prefetch_related("items", "food__units")
            .get(pk=entry.pk)
        )

        return Response(DiaryEntrySerializer(entry).data, status=status_code)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.respond(serializer.save(), status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        return self.respond(serializer.save())

    def perform_destroy(self, entry):
        entry.deleted_at = timezone.now()
        entry.save(update_fields=["deleted_at", "updated_at"])

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def restore(self, request, pk=None):
        entry = self.get_object()
        entry.deleted_at = None
        entry.save(update_fields=["deleted_at", "updated_at"])

        return self.respond(entry)

from collections import defaultdict
from datetime import date, timedelta

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import Step, advance
from apps.tracking.mixins import TrackingMixin
from apps.tracking.models import (
    FoodUnit,
    GoalSetting,
    Meal,
    MealItem,
    MealType,
    NutritionEntry,
)
from apps.tracking.nutrition.utils import MACROS, total
from apps.tracking.utils import round1
from apps.tracking.weeks import page_of_weeks

from .serializers import (
    EMPTY_GOAL_STATE,
    EntryFromMealSerializer,
    EntryInputSerializer,
    EntryPatchSerializer,
    FoodWeekSerializer,
    GoalStateSerializer,
    GoalUpdateSerializer,
    ManualEntrySerializer,
    MealInputSerializer,
    MealSerializer,
    NutritionEntrySerializer,
    TargetsSerializer,
)


class GoalView(TrackingMixin, APIView):
    def get(self, request):
        setting = GoalSetting.valid_on(self.profile, timezone.localdate())

        return Response(goal_state(setting))

    @transaction.atomic
    def patch(self, request):
        """Every change applies from today on; earlier days keep their values."""
        serializer = GoalUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        today = timezone.localdate()

        current = GoalSetting.valid_on(self.profile, today)
        setting, _ = GoalSetting.objects.get_or_create(
            profile=self.profile,
            valid_from=today,
            defaults={
                field: getattr(current, field, None) for field in ("goal", *MACROS)
            },
        )

        if "goal" in data:
            setting.goal = data["goal"]

        if "targets" in data:
            for field, value in data["targets"].items():
                setattr(setting, field, value)

        setting.save()

        if "goal" in data:
            advance(self.profile, Step.GOAL, Step.TARGETS)

        if "targets" in data:
            advance(self.profile, Step.TARGETS, Step.SUMMARY)

        return Response(goal_state(setting))


def goal_state(setting):
    return GoalStateSerializer(setting).data if setting else EMPTY_GOAL_STATE


class EntryCreateView(TrackingMixin, APIView):
    def post(self, request):
        serializer = EntryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = NutritionEntry.objects.create(
            profile=self.profile,
            source=NutritionEntry.Source.OFF,
            **serializer.validated_data,
        )

        return Response(
            NutritionEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )


class ManualEntryView(TrackingMixin, APIView):
    """A food with name and values typed in by the user, tracked as one portion."""

    def post(self, request):
        serializer = ManualEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = NutritionEntry.objects.create(
            profile=self.profile,
            source=NutritionEntry.Source.MANUAL,
            **serializer.validated_data,
        )

        return Response(
            NutritionEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )


class EntryFromMealView(TrackingMixin, APIView):
    """Tracks the stored totals of an own meal as one portion; recipes can't be tracked."""

    def post(self, request):
        serializer = EntryFromMealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        meal = get_object_or_404(Meal, pk=data["meal_id"], profile=self.profile)

        entry = NutritionEntry.objects.create(
            profile=self.profile,
            source=NutritionEntry.Source.MEAL,
            food_name=meal.name,
            amount=1,
            unit=FoodUnit.PORTION,
            consumed_on=data["consumed_on"],
            meal_type=data["meal_type"],
            **{key: getattr(meal, key) for key in MACROS},
        )

        return Response(
            NutritionEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )


class EntryDetailView(TrackingMixin, generics.GenericAPIView):
    def get_queryset(self):
        return self.profile.tracking_entries.all()

    def patch(self, request, pk):
        entry = self.get_object()
        serializer = EntryPatchSerializer(entry, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(NutritionEntrySerializer(entry).data)

    def delete(self, request, pk):
        self.get_object().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# At most a quarter of a year per request; the diary list loads five weeks at once.
MAX_DAY_RANGE = 92


def day_summary(profile, day, entries):
    """Entries, sums and the targets valid on that day, as one day in the diary."""
    intake = total(entries)

    # Compared with the targets valid on that day, not today's.
    setting = GoalSetting.valid_on(profile, day)
    targets = None
    difference = None

    if setting and setting.has_targets:
        targets = TargetsSerializer(setting).data
        difference = {key: intake[key] - getattr(setting, key) for key in MACROS}

    by_meal_type = {}

    for meal_type in MealType.values:
        meal_entries = [entry for entry in entries if entry.meal_type == meal_type]

        if meal_entries:
            by_meal_type[meal_type] = total(meal_entries)

    return {
        "date": day,
        "targets": targets,
        "intake": intake,
        "difference": difference,
        "by_meal_type": by_meal_type,
        "entries": NutritionEntrySerializer(entries, many=True).data,
    }


class DaySummaryView(TrackingMixin, APIView):
    def get(self, request, date):
        day = parse_date(date)
        entries = list(self.profile.tracking_entries.filter(consumed_on=day))

        return Response(day_summary(self.profile, day, entries))


class DayRangeView(TrackingMixin, APIView):
    """Several days in one request, newest first: ?from=2026-10-01&to=2026-11-04."""

    def get(self, request):
        first = parse_date(request.query_params.get("from", ""), "from")
        last = parse_date(request.query_params.get("to", ""), "to")

        if last < first:
            raise serializers.ValidationError({"to": ["Darf nicht vor from liegen."]})

        if (last - first).days >= MAX_DAY_RANGE:
            raise serializers.ValidationError(
                {"to": [f"Höchstens {MAX_DAY_RANGE} Tage pro Anfrage."]}
            )

        entries = list(
            self.profile.tracking_entries.filter(consumed_on__range=(first, last))
        )
        days = []
        day = last

        while day >= first:
            days.append(
                day_summary(
                    self.profile,
                    day,
                    [entry for entry in entries if entry.consumed_on == day],
                )
            )
            day -= timedelta(days=1)

        return Response(days)


def summarize_food_weeks(days):
    """Weeks with entries, newest first, from (day, kcal) pairs of the days with entries."""
    grouped = defaultdict(list)

    for day, kcal in days:
        grouped[tuple(day.isocalendar()[:2])].append(kcal)

    weeks = []

    for iso_year, iso_week in sorted(grouped, reverse=True):
        monday = date.fromisocalendar(iso_year, iso_week, 1)
        kcal = grouped[iso_year, iso_week]

        weeks.append(
            {
                "iso_year": iso_year,
                "iso_week": iso_week,
                "week_start": monday,
                "week_end": monday + timedelta(days=6),
                "days_count": len(kcal),
                "average_kcal": round1(sum(kcal) / len(kcal)),
            }
        )

    return weeks


class DayWeekListView(TrackingMixin, APIView):
    """Weeks with food entries for the diary list, five per page, see apps.tracking.weeks."""

    def get(self, request):
        days = (
            self.profile.tracking_entries.values_list("consumed_on")
            .annotate(kcal=Sum("kcal"))
            .order_by()
        )

        return Response(
            page_of_weeks(
                summarize_food_weeks(days), request.query_params, FoodWeekSerializer
            )
        )


def parse_date(value, field="date"):
    try:
        return serializers.DateField().to_internal_value(value)
    except serializers.ValidationError as exc:
        raise serializers.ValidationError({field: exc.detail}) from exc


class MealViewSet(TrackingMixin, viewsets.ModelViewSet):
    serializer_class = MealSerializer
    pagination_class = None
    lookup_value_regex = r"\d+"
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_queryset(self):
        return self.profile.meals.prefetch_related("items").order_by(
            Lower("name"), "id"
        )

    def create(self, request, *args, **kwargs):
        meal = self.save_meal(Meal(profile=self.profile))

        return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Replaces name and items; entries tracked from this meal stay as they are."""
        meal = self.save_meal(self.get_object())

        return Response(MealSerializer(meal).data)

    @transaction.atomic
    def save_meal(self, meal):
        serializer = MealInputSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["items"]

        meal.name = serializer.validated_data["name"]

        for key, value in total(items).items():
            setattr(meal, key, value)

        meal.save()
        meal.items.all().delete()
        MealItem.objects.bulk_create(
            MealItem(meal=meal, position=position, **item)
            for position, item in enumerate(items)
        )

        return Meal.objects.prefetch_related("items").get(pk=meal.pk)

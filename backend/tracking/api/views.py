from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HasPrivacyConsent
from accounts.services.onboarding import Step, advance
from tracking.exceptions import WeightEntryExists
from tracking.models import (
    BodyProfile,
    FoodUnit,
    GoalSetting,
    Meal,
    MealItem,
    MealType,
    TrackingEntry,
)
from tracking.utils.nutrition import MACROS, total
from tracking.utils.weeks import (
    PAGE_SIZE,
    parse_week,
    summarize_weeks,
    week_label,
    week_start,
)

from .serializers import (
    EMPTY_BODY_PROFILE,
    EMPTY_GOAL_STATE,
    BodyProfileSerializer,
    EntryFromMealSerializer,
    EntryInputSerializer,
    EntryPatchSerializer,
    GoalStateSerializer,
    GoalUpdateSerializer,
    MealInputSerializer,
    MealSerializer,
    TargetsSerializer,
    TrackingEntrySerializer,
    WeekDetailSerializer,
    WeekSummarySerializer,
    WeightEntrySerializer,
)

WEIGHT_RANGES = {"7d": 7, "14d": 14, "1m": 30, "1y": 365, "all": None}


class TrackingMixin:
    """All tracking endpoints need login and a given privacy consent."""

    permission_classes = [IsAuthenticated, HasPrivacyConsent]

    @property
    def profile(self):
        return self.request.user.profile


# ------------------------------------------------------------------------------
# Goal
# ------------------------------------------------------------------------------


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
                field: getattr(current, field, None)
                for field in ("goal", *MACROS)
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


# ------------------------------------------------------------------------------
# Entries
# ------------------------------------------------------------------------------


class EntryCreateView(TrackingMixin, APIView):
    def post(self, request):
        serializer = EntryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = TrackingEntry.objects.create(
            profile=self.profile,
            source=TrackingEntry.Source.OFF,
            **serializer.validated_data,
        )

        return Response(
            TrackingEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )


class EntryFromMealView(TrackingMixin, APIView):
    """Tracks the stored totals of an own meal as one portion; recipes can't be tracked."""

    def post(self, request):
        serializer = EntryFromMealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        meal = get_object_or_404(Meal, pk=data["meal_id"], profile=self.profile)

        entry = TrackingEntry.objects.create(
            profile=self.profile,
            source=TrackingEntry.Source.MEAL,
            food_name=meal.name,
            amount=1,
            unit=FoodUnit.PORTION,
            consumed_on=data["consumed_on"],
            meal_type=data["meal_type"],
            **{key: getattr(meal, key) for key in MACROS},
        )

        return Response(
            TrackingEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )


class EntryDetailView(TrackingMixin, generics.GenericAPIView):
    def get_queryset(self):
        return self.profile.tracking_entries.all()

    def patch(self, request, pk):
        entry = self.get_object()
        serializer = EntryPatchSerializer(entry, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TrackingEntrySerializer(entry).data)

    def delete(self, request, pk):
        self.get_object().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DaySummaryView(TrackingMixin, APIView):
    def get(self, request, date):
        day = parse_date(date)
        entries = list(self.profile.tracking_entries.filter(consumed_on=day))
        intake = total(entries)

        # Compared with the targets valid on that day, not today's.
        setting = GoalSetting.valid_on(self.profile, day)
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

        return Response(
            {
                "date": day,
                "targets": targets,
                "intake": intake,
                "difference": difference,
                "by_meal_type": by_meal_type,
                "entries": TrackingEntrySerializer(entries, many=True).data,
            }
        )


def parse_date(value):
    try:
        return serializers.DateField().to_internal_value(value)
    except serializers.ValidationError as exc:
        raise serializers.ValidationError({"date": exc.detail}) from exc


# ------------------------------------------------------------------------------
# Meals
# ------------------------------------------------------------------------------


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
        meal.note = serializer.validated_data.get("note", "").strip()

        for key, value in total(items).items():
            setattr(meal, key, value)

        meal.save()
        meal.items.all().delete()
        MealItem.objects.bulk_create(
            MealItem(meal=meal, position=position, **item)
            for position, item in enumerate(items)
        )

        return Meal.objects.prefetch_related("items").get(pk=meal.pk)


# ------------------------------------------------------------------------------
# Body
# ------------------------------------------------------------------------------


class BodyProfileView(TrackingMixin, APIView):
    """Date of birth, height and sex; health data, so only with consent."""

    def get(self, request):
        body = BodyProfile.objects.filter(profile=self.profile).first()

        if body is None:
            return Response(EMPTY_BODY_PROFILE)

        return Response(BodyProfileSerializer(body).data)

    def patch(self, request):
        """Changes the given fields only; null clears one."""
        body = BodyProfile.objects.filter(profile=self.profile).first()
        serializer = BodyProfileSerializer(body, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        body = serializer.save(profile=self.profile)

        return Response(BodyProfileSerializer(body).data)


# ------------------------------------------------------------------------------
# Weight
# ------------------------------------------------------------------------------


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
        weeks = summarize_weeks(self.profile.weight_entries.all())
        before = request.query_params.get("before")

        if before:
            before_week = parse_week(before)
            weeks = [w for w in weeks if (w["iso_year"], w["iso_week"]) < before_week]

        page = weeks[:PAGE_SIZE]
        has_more = len(weeks) > PAGE_SIZE

        return Response(
            {
                "results": WeekSummarySerializer(page, many=True).data,
                "next_before": (
                    week_label(page[-1]["iso_year"], page[-1]["iso_week"])
                    if has_more
                    else None
                ),
            }
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

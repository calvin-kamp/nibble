from django_filters import rest_framework as filters
from rest_framework.exceptions import NotAuthenticated

from apps.recipes.models import Recipe

# A diet filter also shows the stricter diets.
DIET_HIERARCHY = {
    Recipe.Diet.VEGAN: [Recipe.Diet.VEGAN],
    Recipe.Diet.VEGETARIAN: [Recipe.Diet.VEGETARIAN, Recipe.Diet.VEGAN],
    Recipe.Diet.PESCETARIAN: [
        Recipe.Diet.PESCETARIAN,
        Recipe.Diet.VEGETARIAN,
        Recipe.Diet.VEGAN,
    ],
}


class RecipeFilter(filters.FilterSet):
    q = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        max_length=100,
    )
    diet = filters.ChoiceFilter(
        choices=Recipe.Diet.choices,
        method="filter_diet",
    )
    intolerances = filters.MultipleChoiceFilter(
        choices=Recipe.Intolerance.choices,
        method="filter_all",
    )
    meal_types = filters.MultipleChoiceFilter(
        choices=Recipe.MealType.choices,
        method="filter_any",
    )
    properties = filters.MultipleChoiceFilter(
        choices=Recipe.Property.choices,
        method="filter_all",
    )
    equipment = filters.MultipleChoiceFilter(
        choices=Recipe.Equipment.choices,
        method="filter_equipment",
    )
    mine = filters.BooleanFilter(method="filter_mine")
    saved = filters.BooleanFilter(method="filter_saved")

    class Meta:
        model = Recipe
        fields = (
            "q",
            "diet",
            "intolerances",
            "meal_types",
            "properties",
            "equipment",
            "mine",
            "saved",
        )

    def filter_queryset(self, queryset):
        # The list shows approved recipes; mine=true shows the own ones in any status.
        if not self.form.cleaned_data.get("mine"):
            queryset = queryset.filter(status=Recipe.Status.APPROVED)

        return super().filter_queryset(queryset)

    def filter_diet(self, queryset, name, value):
        return queryset.filter(diet__in=DIET_HIERARCHY[value])

    def filter_all(self, queryset, name, value):
        return queryset.filter(**{f"{name}__contains": value})

    def filter_any(self, queryset, name, value):
        return queryset.filter(**{f"{name}__overlap": value})

    def filter_equipment(self, queryset, name, value):
        """Only recipes whose equipment is fully covered; none needed matches always."""
        return queryset.filter(equipment__contained_by=value)

    def filter_mine(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(author=self.profile())

    def filter_saved(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(saved_by__profile=self.profile())

    def profile(self):
        user = self.request.user

        if not user.is_authenticated:
            raise NotAuthenticated()

        return user.profile

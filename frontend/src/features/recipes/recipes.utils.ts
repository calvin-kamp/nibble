import type {
	Diet,
	Equipment,
	IngredientDraft,
	IngredientUnit,
	Intolerance,
	Recipe,
	RecipeContent,
	RecipeFact,
	RecipeFormValues,
	RecipeListView,
	RecipeSummary,
	RecipeTag,
	ActiveFilter,
	FilterGroupId,
	RecipeFilterValues,
} from '@features/recipes/recipes.types'
import type { LocationQuery, LocationQueryRaw } from 'vue-router'

import { macrosToKcal } from '@features/calorie-calculator/calorie-calculator.utils'
import {
	DIET_LABELS,
	EMPTY_FILTERS,
	EQUIPMENT_LABELS,
	FILTER_GROUPS,
	INGREDIENT_UNIT_LABELS,
	INTOLERANCE_LABELS,
	MEAL_TYPE_LABELS,
	TAG_LABELS,
	VIEW_QUERY,
} from '@features/recipes/recipes.constants'
import { formatNumber } from '@shared/utils/number'
import { slugify } from '@shared/utils/slug'

/**
 * Amount for a different number of servings. At the original count the amount stays as entered,
 * otherwise it is rounded: grams and millilitres to 5, everything else to half units.
 */
export function formatAmount(
	amount: number,
	unit: IngredientUnit,
	servings: number,
	baseServings: number,
): string {
	const label = INGREDIENT_UNIT_LABELS[unit]

	if (servings === baseServings) {
		return `${formatNumber(amount, Number.isInteger(amount) ? 0 : 1)} ${label}`
	}

	const scaled: number = (amount * servings) / baseServings

	if (unit === 'g' || unit === 'ml') {
		return `${formatNumber(Math.max(Math.round(scaled / 5) * 5, 5))} ${label}`
	}

	const rounded: number = Math.max(Math.round(scaled * 2) / 2, 0.5)

	return `${formatNumber(rounded, Number.isInteger(rounded) ? 0 : 1)} ${label}`
}

export function emptyIngredient(): IngredientDraft {
	return { name: '', amount: undefined, unit: 'g' }
}

/** Completely empty rows do not count, they are simply left alone */
export function isEmptyIngredient(ingredient: IngredientDraft): boolean {
	return !ingredient.name.trim() && ingredient.amount === undefined
}

/** Image and content for the form. With a pending change, editing continues from that one. */
export function toFormValues(recipe: Recipe): RecipeFormValues {
	const revision = recipe.pendingRevision

	if (revision) return contentToFormValues(revision.content, revision.imageUrl ?? null)

	return contentToFormValues(recipe, recipe.imageUrl ?? null)
}

function contentToFormValues(recipe: RecipeContent, image: string | null): RecipeFormValues {
	return {
		title: recipe.title,
		description: recipe.description ?? '',
		image,
		servings: recipe.servings,
		durationMinutes: recipe.durationMinutes,
		protein: recipe.protein,
		carbs: recipe.carbs,
		fat: recipe.fat,
		diet: recipe.diet,
		freeFrom: [...recipe.freeFrom],
		equipment: [...recipe.equipment],
		mealTypes: [...recipe.mealTypes],
		ingredients: recipe.ingredients.map((ingredient) => ({ ...ingredient })),
		steps: [...recipe.steps],
	}
}

/** Calories per serving from the macros, rounded */
export function kcalOf(values: Pick<RecipeFormValues, 'protein' | 'carbs' | 'fat'>): number {
	return Math.round(macrosToKcal(values))
}

/**
 * Params for a recipe's routes, e.g. /rezepte/3-linsen-bowl-mit-joghurtdip.
 * Lookup uses the ID only; the name in the path makes the address readable.
 */
export function recipeParams(recipe: Pick<RecipeSummary, 'id' | 'title'>): {
	id: string
	slug: string
} {
	return { id: recipe.id, slug: slugify(recipe.title) }
}

// Filtering happens in the backend, see searchRecipes(). Vegan recipes also count as
// vegetarian there, and vegetarian ones as pescatarian.

/** Number of active filters excluding the search, e.g. for "Filter (2)" */
export function countActiveFilters(filters: RecipeFilterValues): number {
	return (
		Number(filters.diet !== 'omnivore') +
		filters.freeFrom.length +
		filters.equipment.length +
		filters.tags.length
	)
}

// The address holds readable values, e.g. ?ernaehrung=vegan&ohne=glutenfrei&geraete=herd.
// They are generated from the labels; unknown values are dropped when reading.

function fromSlug<TKey extends string>(
	labels: Record<TKey, string | null>,
	slug: string,
): TKey | undefined {
	return (Object.keys(labels) as TKey[]).find((key) => {
		const label = labels[key]

		return label !== null && slugify(label) === slug
	})
}

function toSlugs<TKey extends string>(
	labels: Record<TKey, string>,
	keys: TKey[],
): string | undefined {
	return keys.length ? keys.map((key) => slugify(labels[key])).join(',') : undefined
}

function fromSlugs<TKey extends string>(labels: Record<TKey, string>, value: unknown): TKey[] {
	if (typeof value !== 'string') return []

	return value
		.split(',')
		.map((slug) => fromSlug(labels, slug))
		.filter((key): key is TKey => key !== undefined)
}

export function filtersFromQuery(query: LocationQuery): RecipeFilterValues {
	return {
		query: typeof query.q === 'string' ? query.q : '',
		diet:
			(typeof query.ernaehrung === 'string' && fromSlug(DIET_LABELS, query.ernaehrung)) ||
			'omnivore',
		freeFrom: fromSlugs(INTOLERANCE_LABELS, query.ohne),
		equipment: fromSlugs(EQUIPMENT_LABELS, query.geraete),
		tags: fromSlugs(TAG_LABELS, query.eigenschaften),
	}
}

/** Empty filters are left out of the address entirely */
export function filtersToQuery(filters: RecipeFilterValues): LocationQueryRaw {
	const diet = DIET_LABELS[filters.diet]

	return {
		q: filters.query.trim() || undefined,
		ernaehrung: diet ? slugify(diet) : undefined,
		ohne: toSlugs(INTOLERANCE_LABELS, filters.freeFrom),
		geraete: toSlugs(EQUIPMENT_LABELS, filters.equipment),
		eigenschaften: toSlugs(TAG_LABELS, filters.tags),
	}
}

export function viewFromQuery(query: LocationQuery): RecipeListView {
	if (query.ansicht === VIEW_QUERY.own) return 'own'
	if (query.ansicht === VIEW_QUERY.saved) return 'saved'

	return 'all'
}

/** Value of a group, as the radios or checkboxes expect it */
export function groupValue(filters: RecipeFilterValues, id: FilterGroupId): string | string[] {
	if (id === 'diet') return filters.diet

	return filters[id]
}

export function withGroupValue(
	filters: RecipeFilterValues,
	id: FilterGroupId,
	value: string | string[],
): RecipeFilterValues {
	if (id === 'diet') return { ...filters, diet: value as Diet }
	if (id === 'freeFrom') return { ...filters, freeFrom: value as Intolerance[] }
	if (id === 'tags') return { ...filters, tags: value as RecipeTag[] }

	return { ...filters, equipment: value as Equipment[] }
}

/** Group without a selection, e.g. for "Zurücksetzen" within a group */
export function withoutGroup(filters: RecipeFilterValues, id: FilterGroupId): RecipeFilterValues {
	return withGroupValue(filters, id, groupValue(EMPTY_FILTERS, id))
}

/** Active filters one by one, e.g. as removable chips */
export function activeFilters(filters: RecipeFilterValues): ActiveFilter[] {
	return FILTER_GROUPS.flatMap((group) => {
		const value = groupValue(filters, group.id)
		const empty = groupValue(EMPTY_FILTERS, group.id)
		const selected = Array.isArray(value) ? value : value === empty ? [] : [value]

		return selected.map((item) => ({
			key: `${group.id}:${item}`,
			label: group.options.find((option) => option.value === item)?.label ?? item,
			remove: (current: RecipeFilterValues) =>
				Array.isArray(value)
					? withGroupValue(
							current,
							group.id,
							(groupValue(current, group.id) as string[]).filter(
								(entry) => entry !== item,
							),
						)
					: withoutGroup(current, group.id),
		}))
	})
}

/** Time, meals, diet, intolerances and appliances, e.g. for the row below the title */
export function recipeFacts(recipe: RecipeContent): RecipeFact[] {
	const { diet, durationMinutes, equipment, freeFrom, mealTypes } = recipe
	const list: RecipeFact[] = [{ label: 'Zubereitungszeit', value: `${durationMinutes} Minuten` }]

	if (mealTypes.length) {
		list.push({
			label: 'Passt zu',
			value: mealTypes.map((item) => MEAL_TYPE_LABELS[item]).join(', '),
		})
	}

	if (DIET_LABELS[diet]) list.push({ label: 'Ernährungsform', value: DIET_LABELS[diet] })

	if (freeFrom.length) {
		list.push({
			// Soft hyphen: in the single row from tablet up, the word is wider than its column
			label: 'Unverträg\u00adlichkeiten',
			value: freeFrom.map((item) => INTOLERANCE_LABELS[item]).join(', '),
		})
	}

	list.push({
		label: 'Geräte',
		value: equipment.length
			? equipment.map((item) => EQUIPMENT_LABELS[item]).join(', ')
			: 'Kein Gerät nötig',
	})

	return list
}

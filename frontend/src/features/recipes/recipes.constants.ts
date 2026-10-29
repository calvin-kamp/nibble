import type {
	Diet,
	Equipment,
	FilterGroup,
	IngredientUnit,
	Intolerance,
	RecipeFilterValues,
	RecipeFormSection,
	RecipeListView,
	RecipeMealType,
	RecipeTag,
} from '@features/recipes/recipes.types'

/** The backend always returns 20 recipes per page */
export const RECIPES_PAGE_SIZE = 20

/** null means: show no tag */
export const DIET_LABELS: Record<Diet, string | null> = {
	omnivore: null,
	pescetarian: 'Pescetarisch',
	vegetarian: 'Vegetarisch',
	vegan: 'Vegan',
}

export const INTOLERANCE_LABELS: Record<Intolerance, string> = {
	gluten_free: 'Glutenfrei',
	lactose_free: 'Laktosefrei',
}

export const TAG_LABELS: Record<RecipeTag, string> = {
	protein_rich: 'Proteinreich',
	few_ingredients: 'Wenig Zutaten',
	low_calorie: 'Kalorienarm',
	under_30_min: 'Unter 30 Min.',
}

export const EQUIPMENT_LABELS: Record<Equipment, string> = {
	stove: 'Herd',
	oven: 'Backofen',
	mixer: 'Mixer',
	airfryer: 'Airfryer',
}

export const MEAL_TYPE_LABELS: Record<RecipeMealType, string> = {
	breakfast: 'Frühstück',
	lunch: 'Mittagessen',
	dinner: 'Abendessen',
	snack: 'Snack',
	dessert: 'Dessert',
}

/** German unit names; the values themselves come from the backend */
export const INGREDIENT_UNIT_LABELS: Record<IngredientUnit, string> = {
	g: 'g',
	kg: 'kg',
	ml: 'ml',
	l: 'l',
	tbsp: 'EL',
	tsp: 'TL',
	piece: 'Stück',
	pinch: 'Prise',
	cup: 'Tasse',
	slice: 'Scheibe',
	bunch: 'Bund',
	clove: 'Zehe',
	can: 'Dose',
	pack: 'Packung',
}

export const INGREDIENT_UNITS = Object.keys(INGREDIENT_UNIT_LABELS) as IngredientUnit[]

export const MIN_SERVINGS = 1
export const MAX_SERVINGS = 12

/** Recipe form sections in order. On phones, each one is a separate step. */
export const RECIPE_FORM_SECTIONS: readonly RecipeFormSection[] = [
	'basics',
	'nutrition',
	'properties',
	'ingredients',
	'steps',
]

export const EMPTY_FILTERS: RecipeFilterValues = {
	query: '',
	diet: 'omnivore',
	freeFrom: [],
	equipment: [],
	tags: [],
}

export const VIEW_QUERY: Record<RecipeListView, string | undefined> = {
	all: undefined,
	own: 'eigene',
	saved: 'gespeichert',
}

/** The filters in order. Drawer, desktop bar and active filters all read from here. */
export const FILTER_GROUPS: FilterGroup[] = [
	{
		id: 'tags',
		legend: 'Eigenschaften',
		type: 'checkbox',
		options: Object.entries(TAG_LABELS).map(([value, label]) => ({ value, label })),
	},
	{
		id: 'diet',
		legend: 'Ernährungsform',
		type: 'radio',
		options: [
			{ value: 'omnivore', label: 'Alle' },
			...(['pescetarian', 'vegetarian', 'vegan'] as const).map((diet) => ({
				value: diet,
				label: DIET_LABELS[diet]!,
			})),
		],
	},
	{
		id: 'freeFrom',
		legend: 'Unverträglichkeiten',
		type: 'checkbox',
		options: Object.entries(INTOLERANCE_LABELS).map(([value, label]) => ({ value, label })),
	},
	{
		id: 'equipment',
		legend: 'Küchengeräte',
		type: 'checkbox',
		options: Object.entries(EQUIPMENT_LABELS).map(([value, label]) => ({ value, label })),
	},
]

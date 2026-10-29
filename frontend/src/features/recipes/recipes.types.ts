import type { ChoiceOption } from '@shared/ui/types'

/** omnivore stands for recipes without a diet (e.g. with meat), null in the backend */
export type Diet = 'omnivore' | 'pescetarian' | 'vegetarian' | 'vegan'

/** What a recipe is free from, e.g. gluten-free */
export type Intolerance = 'gluten_free' | 'lactose_free'

export type Equipment = 'stove' | 'oven' | 'mixer' | 'airfryer'

/** Which meals a recipe suits, at least one */
export type RecipeMealType = 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'dessert'

/** Properties the backend derives on save from nutrition values, ingredients and time */
export type RecipeTag = 'protein_rich' | 'low_calorie' | 'few_ingredients' | 'under_30_min'

/** Values as in the backend; the German names from INGREDIENT_UNIT_LABELS are displayed */
export type IngredientUnit =
	| 'g'
	| 'kg'
	| 'ml'
	| 'l'
	| 'tbsp'
	| 'tsp'
	| 'piece'
	| 'pinch'
	| 'cup'
	| 'slice'
	| 'bunch'
	| 'clove'
	| 'can'
	| 'pack'

/** Approval by moderation. New and changed recipes start out as pending. */
export type RecipeStatus = 'pending' | 'approved' | 'rejected'

export interface Ingredient {
	name: string
	/** Amount for recipe.servings servings */
	amount: number
	unit: IngredientUnit
}

/** Recipe in the list, without ingredients and instructions */
export interface RecipeSummary {
	id: string
	title: string
	diet: Diet
	durationMinutes: number
	kcalPerServing: number
	/** Grams per serving */
	protein: number
	carbs: number
	fat: number
	freeFrom: Intolerance[]
	/** Empty means: no appliance needed */
	equipment: Equipment[]
	mealTypes: RecipeMealType[]
	/** Assigned by the backend, not part of the form */
	tags: RecipeTag[]
	imageUrl?: string
	/** null when signed out */
	isSaved: boolean | null
	status: RecipeStatus
	/** Whether a change is waiting for approval */
	hasPendingRevision: boolean
}

/** Recipe content as submitted */
export interface RecipeContent {
	title: string
	description?: string
	diet: Diet
	durationMinutes: number
	/** Servings the ingredient amounts apply to */
	servings: number
	kcalPerServing: number
	protein: number
	carbs: number
	fat: number
	freeFrom: Intolerance[]
	equipment: Equipment[]
	mealTypes: RecipeMealType[]
	ingredients: Ingredient[]
	steps: string[]
}

/** Changed version of an approved recipe that is still waiting for moderation */
export interface RecipeRevision {
	status: 'pending' | 'rejected'
	rejectionReason: string | null
	imageUrl?: string
	content: RecipeContent
}

export interface Recipe extends RecipeSummary, RecipeContent {
	/** Own recipes can be edited. The backend decides; usernames are never compared. */
	isOwn: boolean
	/** Reason when a never-approved recipe was rejected */
	rejectionReason: string | null
	/** Only visible to the author and moderation */
	pendingRevision: RecipeRevision | null
}

/** Values in the create and edit form */
export interface RecipeFormValues {
	title: string
	description: string
	/** Newly chosen file, URL of the saved photo, or null */
	image: File | string | null
	servings: number
	durationMinutes: number
	protein: number
	carbs: number
	fat: number
	diet: Diet
	freeFrom: Intolerance[]
	equipment: Equipment[]
	mealTypes: RecipeMealType[]
	ingredients: IngredientDraft[]
	steps: string[]
}

/** Ingredient in the form. The amount is missing until something is entered. */
export interface IngredientDraft {
	name: string
	amount?: number
	unit: IngredientUnit
}

export interface RecipeFilterValues {
	query: string
	/** omnivore means: every diet */
	diet: Diet
	freeFrom: Intolerance[]
	/** Appliances the user has. Empty means: whatever a recipe needs. */
	equipment: Equipment[]
	/** Properties from the backend; every selected one has to apply */
	tags: RecipeTag[]
}

/** Which recipes the list shows. Own and saved recipes require signing in. */
export type RecipeListView = 'all' | 'own' | 'saved'

export type FilterGroupId = 'tags' | 'diet' | 'freeFrom' | 'equipment'

export interface FilterGroup {
	id: FilterGroupId
	legend: string
	type: 'radio' | 'checkbox'
	options: ChoiceOption[]
}

export interface ActiveFilter {
	/** Unique, e.g. "freeFrom:gluten" */
	key: string
	label: string
	remove: (filters: RecipeFilterValues) => RecipeFilterValues
}

/** Recipe form sections in order. On phones, each one is a separate step. */
export type RecipeFormSection = 'basics' | 'nutrition' | 'properties' | 'ingredients' | 'steps'

export interface RecipePage {
	recipes: RecipeSummary[]
	/** Total number of matches across all pages */
	total: number
}

export interface MacrosResponse {
	kcal: number
	protein: number
	carbs: number
	fat: number
}

/** Content as submitted (RecipeInput), fields in snake_case */
export interface RecipeInputResponse {
	name: string
	description: string
	prep_time_minutes: number
	diet: Exclude<Diet, 'omnivore'> | null
	intolerances: Intolerance[]
	equipment: Equipment[]
	meal_types: RecipeMealType[]
	servings: number
	nutrition_per_serving: MacrosResponse
	ingredients: { name: string; amount: number; unit: IngredientUnit }[]
	steps: { step_number: number; text: string }[]
}

export interface RecipeListItemResponse {
	id: number
	name: string
	image_url: string | null
	prep_time_minutes: number
	diet: Exclude<Diet, 'omnivore'> | null
	intolerances: Intolerance[]
	equipment: Equipment[]
	meal_types: RecipeMealType[]
	properties: RecipeTag[]
	nutrition_per_serving: MacrosResponse
	/** Whether the signed-in user wrote it; null when signed out. The API never names authors. */
	is_own: boolean | null
	status: RecipeStatus
	has_pending_revision: boolean
	is_saved: boolean | null
}

export interface RecipeDetailResponse extends RecipeInputResponse {
	id: number
	image_url: string | null
	properties: RecipeTag[]
	is_own: boolean | null
	status: RecipeStatus
	rejection_reason: string | null
	pending_revision: {
		id: number
		status: 'pending' | 'rejected'
		submitted_at: string
		rejection_reason: string | null
		image_url?: string | null
		content: RecipeInputResponse
	} | null
	is_saved: boolean | null
}

/** A detail with a label, e.g. "Zubereitungszeit: 25 Minuten" */
export interface RecipeFact {
	label: string
	value: string
}

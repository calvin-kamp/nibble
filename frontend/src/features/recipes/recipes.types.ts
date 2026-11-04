import type { ChoiceOption } from '@shared/ui/types'

/** omnivore stands for recipes without a diet (e.g. with meat), null in the backend */
export type Diet = 'omnivore' | 'pescetarian' | 'vegetarian' | 'vegan'

export type Intolerance = 'gluten_free' | 'lactose_free'

export type Equipment = 'stove' | 'oven' | 'mixer' | 'airfryer'

export type RecipeMealType = 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'dessert'

/** Properties the backend derives on save from nutrition values, ingredients and time */
export type RecipeTag = 'protein_rich' | 'low_calorie' | 'few_ingredients' | 'under_30_min'

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
	tags: RecipeTag[]
	imageUrl?: string
	/** null when signed out */
	isSaved: boolean | null
	status: RecipeStatus
	hasPendingRevision: boolean
}

export interface RecipeContent {
	title: string
	description?: string
	diet: Diet
	durationMinutes: number
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

export type RecipeListView = 'all' | 'own' | 'saved'

export type RecipeSort = 'newest' | 'popular'

export type FilterGroupId = 'tags' | 'diet' | 'freeFrom' | 'equipment'

export interface FilterGroup {
	id: FilterGroupId
	legend: string
	type: 'radio' | 'checkbox'
	options: ChoiceOption[]
}

export interface ActiveFilter {
	key: string
	label: string
	remove: (filters: RecipeFilterValues) => RecipeFilterValues
}

export type RecipeFormSection = 'basics' | 'nutrition' | 'properties' | 'ingredients' | 'steps'

export interface RecipePage {
	recipes: RecipeSummary[]
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

export interface RecipeFact {
	label: string
	value: string
}

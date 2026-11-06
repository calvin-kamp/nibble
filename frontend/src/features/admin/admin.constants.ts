import type {
	FoodBaseUnit,
	FoodCountry,
	SubmissionKind,
	SubmissionStatus,
} from '@features/admin/admin.types'
import type { RecipeContent } from '@features/recipes/recipes.types'

import { PAGE_SIZE } from '@shared/constants'

export const SUBMISSIONS_PAGE_SIZE = PAGE_SIZE

export const SUBMISSION_STATUS_LABELS: Record<SubmissionStatus, string> = {
	pending: 'Offen',
	approved: 'Freigegeben',
	rejected: 'Abgelehnt',
}

export const SUBMISSION_KIND_LABELS: Record<SubmissionKind, string> = {
	new: 'Neues Rezept',
	revision: 'Änderung',
}

export const STATUS_QUERY: Record<SubmissionStatus, string | undefined> = {
	pending: undefined,
	approved: 'freigegeben',
	rejected: 'abgelehnt',
}

export const CONTENT_LABELS: Record<keyof RecipeContent, string> = {
	title: 'Titel',
	description: 'Beschreibung',
	diet: 'Ernährungsform',
	durationMinutes: 'Zubereitungszeit',
	servings: 'Portionen',
	kcalPerServing: 'Kalorien',
	protein: 'Protein',
	carbs: 'Kohlenhydrate',
	fat: 'Fett',
	freeFrom: 'Unverträglichkeiten',
	equipment: 'Geräte',
	mealTypes: 'Mahlzeiten',
	ingredients: 'Zutaten',
	steps: 'Zubereitung',
}

/** Same limit as in the backend */
export const MAX_REJECTION_REASON_LENGTH = 1000

export const MISSING_BARCODES_PAGE_SIZE = PAGE_SIZE

export const FOOD_COUNTRY_OPTIONS: { value: FoodCountry; label: string }[] = [
	{ value: 'en:germany', label: 'Deutschland' },
	{ value: 'en:austria', label: 'Österreich' },
	{ value: 'en:switzerland', label: 'Schweiz' },
]

export const FOOD_UNIT_OPTIONS: { value: FoodBaseUnit; label: string; description: string }[] = [
	{ value: 'g', label: 'Gramm', description: 'Feste Lebensmittel' },
	{ value: 'ml', label: 'Milliliter', description: 'Getränke' },
]

export const REPORTED_FOODS_PAGE_SIZE = PAGE_SIZE

export { FOOD_REPORT_REASON_LABELS } from '@features/tracking/tracking.constants'

/** Same limits as in the backend and the food import */
export const MAX_KCAL_PER_100 = 900
export const MAX_GRAMS_PER_100 = 100
export const MAX_SERVING_QUANTITY = 5000
export const MAX_PACKAGE_QUANTITY = 100000

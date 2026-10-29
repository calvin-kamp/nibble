import type { SubmissionKind, SubmissionStatus } from '@features/admin/admin.types'
import type { RecipeContent } from '@features/recipes/recipes.types'

/** The backend always returns 20 submissions per page */
export const SUBMISSIONS_PAGE_SIZE = 20

export const SUBMISSION_STATUS_LABELS: Record<SubmissionStatus, string> = {
	pending: 'Offen',
	approved: 'Freigegeben',
	rejected: 'Abgelehnt',
}

export const SUBMISSION_KIND_LABELS: Record<SubmissionKind, string> = {
	new: 'Neues Rezept',
	revision: 'Änderung',
}

/** Status in the address, e.g. /verwaltung?status=abgelehnt. Open submissions need none. */
export const STATUS_QUERY: Record<SubmissionStatus, string | undefined> = {
	pending: undefined,
	approved: 'freigegeben',
	rejected: 'abgelehnt',
}

/** Fields of a recipe in the order the detail page shows them, for the list of changes */
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

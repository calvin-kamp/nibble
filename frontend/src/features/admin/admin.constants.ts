import type { SubmissionKind, SubmissionStatus } from '@features/admin/admin.types'
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

import type { SubmissionChange, SubmissionStatus } from '@features/admin/admin.types'
import type { RecipeContent } from '@features/recipes/recipes.types'
import type { LocationQuery } from 'vue-router'

import { CONTENT_LABELS, STATUS_QUERY } from '@features/admin/admin.constants'

export function statusFromQuery(query: LocationQuery): SubmissionStatus {
	if (query.status === STATUS_QUERY.approved) return 'approved'
	if (query.status === STATUS_QUERY.rejected) return 'rejected'

	return 'pending'
}

/** Fields in which a revision differs from the live version, in display order */
export function changedFields(content: RecipeContent, current: RecipeContent): SubmissionChange[] {
	return (Object.keys(CONTENT_LABELS) as (keyof RecipeContent)[])
		.filter((key) => JSON.stringify(content[key]) !== JSON.stringify(current[key]))
		.map((key) => ({ key, label: CONTENT_LABELS[key] }))
}

/** E.g. "27. Oktober 2026, 14:05" */
export function formatTimestamp(iso: string): string {
	return new Date(iso).toLocaleString('de-DE', {
		day: 'numeric',
		month: 'long',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})
}

import type {
	SubmissionDetail,
	SubmissionDetailResponse,
	SubmissionPage,
	SubmissionStatus,
	SubmissionSummary,
	SubmissionSummaryResponse,
} from '@features/admin/admin.types'
import type { Paginated } from '@shared/api/client'

import { toRecipeContent } from '@features/recipes/recipes.api'
import { apiRequest, toQuery } from '@shared/api/client'

// Moderation of submitted recipes, staff only; everyone else gets 403. Every function throws
// ApiError, e.g. 409 submission_not_pending when someone else has already decided.

function toSummary(submission: SubmissionSummaryResponse): SubmissionSummary {
	return {
		id: String(submission.id),
		recipeId: String(submission.recipe_id),
		kind: submission.kind,
		status: submission.status,
		title: submission.name ?? 'Ohne Titel',
		author: submission.author?.username ?? null,
		submittedAt: submission.submitted_at,
	}
}

function toDetail(submission: SubmissionDetailResponse): SubmissionDetail {
	return {
		...toSummary(submission),
		content: toRecipeContent(submission.content),
		current: submission.current ? toRecipeContent(submission.current) : null,
		imageUrl: submission.image_url ?? undefined,
		rejectionReason: submission.rejection_reason,
		reviewedBy: submission.reviewed_by,
		reviewedAt: submission.reviewed_at,
	}
}

/** One page of submissions with this status, oldest first */
export async function fetchSubmissions(
	status: SubmissionStatus,
	page: number,
): Promise<SubmissionPage> {
	const query = toQuery({ status, page: page > 1 ? page : undefined })
	const { count, results } = await apiRequest<Paginated<SubmissionSummaryResponse>>(
		`/moderation/submissions${query}`,
	)

	return { submissions: results.map(toSummary), total: count }
}

export async function fetchSubmission(id: string): Promise<SubmissionDetail> {
	return toDetail(await apiRequest<SubmissionDetailResponse>(`/moderation/submissions/${id}`))
}

/** A new recipe becomes visible, a revision replaces the live version. The author gets an email. */
export async function approveSubmission(id: string): Promise<SubmissionDetail> {
	return toDetail(
		await apiRequest<SubmissionDetailResponse>(`/moderation/submissions/${id}/approve`, {
			method: 'POST',
		}),
	)
}

/** The author gets the reason by email and sees it on the recipe */
export async function rejectSubmission(id: string, reason: string): Promise<SubmissionDetail> {
	return toDetail(
		await apiRequest<SubmissionDetailResponse>(`/moderation/submissions/${id}/reject`, {
			method: 'POST',
			body: { reason: reason.trim() },
		}),
	)
}

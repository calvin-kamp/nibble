import type {
	RecipeContent,
	RecipeInputResponse,
	RecipeStatus,
} from '@features/recipes/recipes.types'

/** A new recipe, or a change to one that is already approved */
export type SubmissionKind = 'new' | 'revision'

/** Same values as a recipe's status */
export type SubmissionStatus = RecipeStatus

export interface SubmissionSummary {
	id: string
	recipeId: string
	kind: SubmissionKind
	status: SubmissionStatus
	title: string
	/** null once the author has deleted the account, or before onboarding */
	author: string | null
	/** ISO timestamp */
	submittedAt: string
}

export interface SubmissionDetail extends SubmissionSummary {
	content: RecipeContent
	/** Live version for comparison, revisions only */
	current: RecipeContent | null
	imageUrl?: string
	rejectionReason: string | null
	/** Username of the moderator */
	reviewedBy: string | null
	/** ISO timestamp */
	reviewedAt: string | null
}

export interface SubmissionPage {
	submissions: SubmissionSummary[]
	/** Total across all pages */
	total: number
}

/** A field of a revision that differs from the live version, e.g. "Zutaten" */
export interface SubmissionChange {
	key: keyof RecipeContent
	label: string
}

export interface SubmissionSummaryResponse {
	id: number
	recipe_id: number
	kind: SubmissionKind
	status: SubmissionStatus
	name: string | null
	author: { username: string | null } | null
	submitted_at: string
}

export interface SubmissionDetailResponse extends SubmissionSummaryResponse {
	content: RecipeInputResponse
	current: RecipeInputResponse | null
	image_url: string | null
	rejection_reason: string | null
	reviewed_by: string | null
	reviewed_at: string | null
}

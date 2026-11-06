import type {
	FoodFormValues,
	FoodNutritionResponse,
	FoodNutritionValues,
	MissingBarcode,
	MissingBarcodeDetail,
	MissingBarcodeDetailResponse,
	MissingBarcodePage,
	MissingBarcodeResponse,
	ModerationFood,
	ModerationFoodResponse,
	OffProductResponse,
	ReportedFood,
	ReportedFoodPage,
	ReportedFoodResponse,
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

// Barcodes nobody found, staff only. Adding a product saves it in nibble and on Open Food Facts.

function toMissingBarcode(missing: MissingBarcodeResponse): MissingBarcode {
	return {
		code: missing.code,
		lookups: missing.lookups,
		firstSearchedAt: missing.first_searched_at,
		lastSearchedAt: missing.last_searched_at,
	}
}

function toNutrition(nutrition: FoodNutritionResponse): FoodNutritionValues {
	return {
		kcal: nutrition.kcal ?? undefined,
		fat: nutrition.fat ?? undefined,
		carbs: nutrition.carbs ?? undefined,
		protein: nutrition.protein ?? undefined,
	}
}

/** Request body of create, correct and generic; countries only when the form has them */
function toFoodBody(values: FoodFormValues) {
	const { nutrition } = values

	return {
		name: values.name.trim(),
		brand: values.brand?.trim() ?? '',
		base_unit: values.baseUnit,
		package_quantity: values.packageQuantity ?? null,
		serving_quantity: values.servingQuantity ?? null,
		...(values.countries ? { countries: values.countries } : {}),
		nutrition_per_100: {
			kcal: nutrition.kcal,
			fat: nutrition.fat,
			carbs: nutrition.carbs,
			protein: nutrition.protein,
		},
	}
}

function toOffProduct(product: OffProductResponse): Partial<FoodFormValues> {
	return {
		name: product.name ?? undefined,
		brand: product.brand ?? undefined,
		baseUnit: product.base_unit,
		packageQuantity: product.package_quantity ?? undefined,
		servingQuantity: product.serving_quantity ?? undefined,
		countries: product.countries.length ? product.countries : undefined,
		nutrition: toNutrition(product.nutrition_per_100),
	}
}

export async function fetchMissingBarcodes(page: number): Promise<MissingBarcodePage> {
	const query = toQuery({ page: page > 1 ? page : undefined })
	const { count, results } = await apiRequest<Paginated<MissingBarcodeResponse>>(
		`/moderation/missing-barcodes${query}`,
	)

	return { barcodes: results.map(toMissingBarcode), total: count }
}

export async function fetchMissingBarcode(code: string): Promise<MissingBarcodeDetail> {
	const missing = await apiRequest<MissingBarcodeDetailResponse>(
		`/moderation/missing-barcodes/${code}`,
	)

	return {
		...toMissingBarcode(missing),
		offProduct: missing.off_product ? toOffProduct(missing.off_product) : null,
	}
}

/** For barcodes that aren't food or were mistyped */
export async function dismissMissingBarcode(code: string): Promise<void> {
	await apiRequest(`/moderation/missing-barcodes/${code}`, { method: 'DELETE' })
}

/**
 * 409 product_exists if the import brought it in the meantime, 502 off_unavailable if Open Food
 * Facts refused it (then nothing is saved). offSynced is false without an OFF account in the
 * backend, the product is then only in nibble.
 */
export async function addFoodProduct(
	code: string,
	values: FoodFormValues,
): Promise<{ offSynced: boolean }> {
	const result = await apiRequest<{ off_synced: boolean }>(
		`/moderation/missing-barcodes/${code}/product`,
		{ method: 'POST', body: toFoodBody(values) },
	)

	return { offSynced: result.off_synced }
}

/** Backend field names of the food forms -> form field names */
export const FOOD_FIELD_NAMES: Record<string, string> = {
	name: 'name',
	brand: 'brand',
	base_unit: 'baseUnit',
	package_quantity: 'packageQuantity',
	serving_quantity: 'servingQuantity',
	countries: 'countries',
	'nutrition_per_100.kcal': 'nutrition.kcal',
	'nutrition_per_100.fat': 'nutrition.fat',
	'nutrition_per_100.carbs': 'nutrition.carbs',
	'nutrition_per_100.protein': 'nutrition.protein',
}

// Products users reported and loose foods without barcode, staff only.

function toReportedFood(food: ReportedFoodResponse): ReportedFood {
	return {
		code: food.code,
		name: food.name,
		brand: food.brand,
		generic: food.generic,
		reportCount: food.report_count,
		lastReportedAt: food.last_reported_at,
		reasons: food.reasons,
	}
}

function toModerationFood(food: ModerationFoodResponse): ModerationFood {
	return {
		code: food.code,
		generic: food.generic,
		values: {
			name: food.name,
			brand: food.brand ?? undefined,
			baseUnit: food.base_unit,
			packageQuantity: food.package_quantity ?? undefined,
			servingQuantity: food.serving_quantity ?? undefined,
			nutrition: { ...food.nutrition_per_100 },
		},
		reports: food.reports.map((report) => ({
			id: report.id,
			reason: report.reason,
			comment: report.comment,
			createdAt: report.created_at,
		})),
	}
}

export async function fetchReportedFoods(page: number): Promise<ReportedFoodPage> {
	const query = toQuery({ page: page > 1 ? page : undefined })
	const { count, results } = await apiRequest<Paginated<ReportedFoodResponse>>(
		`/moderation/foods/reported${query}`,
	)

	return { foods: results.map(toReportedFood), total: count }
}

export async function fetchModerationFood(code: string): Promise<ModerationFood> {
	return toModerationFood(await apiRequest<ModerationFoodResponse>(`/moderation/foods/${code}`))
}

/**
 * Saves the correction and closes the reports. Name and brand stay in nibble, the rest goes to
 * Open Food Facts too (not for generic foods). 502 off_unavailable if OFF refused it, then
 * nothing is saved.
 */
export async function correctFood(
	code: string,
	values: FoodFormValues,
): Promise<{ offSynced: boolean }> {
	const result = await apiRequest<{ off_synced: boolean }>(`/moderation/foods/${code}`, {
		method: 'PUT',
		body: toFoodBody({ ...values, countries: undefined }),
	})

	return { offSynced: result.off_synced }
}

/** The reports were wrong; the product stays as it is */
export async function dismissFoodReports(code: string): Promise<void> {
	await apiRequest(`/moderation/foods/${code}/reports`, { method: 'DELETE' })
}

/** Loose food without barcode, e.g. a banana. Stays in nibble only. */
export async function addGenericFood(values: FoodFormValues): Promise<void> {
	await apiRequest('/moderation/foods/generic', {
		method: 'POST',
		body: toFoodBody({ ...values, brand: undefined, countries: undefined }),
	})
}

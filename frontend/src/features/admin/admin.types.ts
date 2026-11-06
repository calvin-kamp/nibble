import type {
	RecipeContent,
	RecipeInputResponse,
	RecipeStatus,
} from '@features/recipes/recipes.types'
import type { FoodReportReason } from '@features/tracking/tracking.types'

/** A new recipe, or a change to one that is already approved */
export type SubmissionKind = 'new' | 'revision'

export type SubmissionStatus = RecipeStatus

export interface SubmissionSummary {
	id: string
	recipeId: string
	kind: SubmissionKind
	status: SubmissionStatus
	title: string
	/** null once the author has deleted the account, or before onboarding */
	author: string | null
	submittedAt: string
}

export interface SubmissionDetail extends SubmissionSummary {
	content: RecipeContent
	/** Live version for comparison, revisions only */
	current: RecipeContent | null
	imageUrl?: string
	rejectionReason: string | null
	reviewedBy: string | null
	reviewedAt: string | null
}

export interface SubmissionPage {
	submissions: SubmissionSummary[]
	total: number
}

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

/** Barcode someone looked up without a result. Holds nothing about who searched. */
export interface MissingBarcode {
	code: string
	lookups: number
	firstSearchedAt: string
	lastSearchedAt: string
}

export interface MissingBarcodePage {
	barcodes: MissingBarcode[]
	total: number
}

export type FoodCountry = 'en:germany' | 'en:austria' | 'en:switzerland'

export type FoodBaseUnit = 'g' | 'ml'

/** Per 100 g or ml; nibble needs energy and the three macros only */
export interface FoodNutritionValues {
	kcal?: number
	fat?: number
	carbs?: number
	protein?: number
}

export interface FoodFormValues {
	name: string
	brand?: string
	baseUnit: FoodBaseUnit
	packageQuantity?: number
	servingQuantity?: number
	/** New products with barcode only */
	countries?: FoodCountry[]
	nutrition: FoodNutritionValues
}

export type FoodFormMode = 'create' | 'correct' | 'generic'

interface FoodReport {
	id: number
	reason: FoodReportReason
	comment: string
	createdAt: string
}

/** Product with open reports, for the list */
export interface ReportedFood {
	code: string
	name: string
	brand: string | null
	generic: boolean
	reportCount: number
	lastReportedAt: string
	reasons: FoodReportReason[]
}

export interface ReportedFoodPage {
	foods: ReportedFood[]
	total: number
}

/** A product with its values and open reports, to correct it */
export interface ModerationFood {
	code: string
	generic: boolean
	values: FoodFormValues
	reports: FoodReport[]
}

interface FoodReportResponse {
	id: number
	reason: FoodReportReason
	comment: string
	created_at: string
}

export interface ReportedFoodResponse {
	code: string
	name: string
	brand: string | null
	generic: boolean
	report_count: number
	last_reported_at: string
	reasons: FoodReportReason[]
}

export interface ModerationFoodResponse {
	code: string
	name: string
	brand: string | null
	generic: boolean
	base_unit: FoodBaseUnit
	serving_quantity: number | null
	package_quantity: number | null
	nutrition_per_100: { kcal: number; protein: number; carbs: number; fat: number }
	curated_at: string | null
	reports: FoodReportResponse[]
}

export interface MissingBarcodeDetail extends MissingBarcode {
	/** What Open Food Facts already knows, to prefill the form */
	offProduct: Partial<FoodFormValues> | null
}

export interface MissingBarcodeResponse {
	code: string
	lookups: number
	first_searched_at: string
	last_searched_at: string
}

/** OFF also sends kJ, sugars etc.; nibble only reads these */
export interface FoodNutritionResponse {
	kcal: number | null
	fat: number | null
	carbs: number | null
	protein: number | null
}

export interface OffProductResponse {
	name: string | null
	brand: string | null
	base_unit: FoodBaseUnit
	package_quantity: number | null
	serving_quantity: number | null
	countries: FoodCountry[]
	nutrition_per_100: FoodNutritionResponse
}

export interface MissingBarcodeDetailResponse extends MissingBarcodeResponse {
	off_product: OffProductResponse | null
}

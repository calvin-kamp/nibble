import type { BarcodeDetector as BarcodeDetectorPonyfill } from 'barcode-detector/ponyfill'

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

/** off: food from the search, meal: a saved meal, manual: name and values typed in */
type FoodEntrySource = 'off' | 'meal' | 'manual'

export interface FoodEntry {
	id: string
	source: FoodEntrySource
	/** Calendar day in the format YYYY-MM-DD */
	date: string
	meal: MealType
	name: string
	kcal: number
	/** Grams */
	protein: number
	/** Grams */
	carbs: number
	/** Grams */
	fat: number
	brand?: string
	quantity?: FoodQuantity
	productCode?: string
	/**
	 * The food as stored in the entry, for changing the amount later. Only for foods from the
	 * search; saved meals have none. Without package size: the entry does not know it.
	 */
	product?: FoodProduct
}

/** Grams or millilitres: what a product's nutrition values refer to (per 100) */
export type BaseUnit = 'g' | 'ml'

export type FoodUnit = BaseUnit | 'serving' | 'package'

/** Logged amount, e.g. 2 servings that equal 80 g */
export interface FoodQuantity {
	value: number
	unit: FoodUnit
	/** The same amount in grams or millilitres */
	base: number
	baseUnit: BaseUnit
}

export interface NutritionGoals {
	kcal: number
	protein: number
	carbs: number
	fat: number
}

interface MealSummary {
	meal: MealType
	label: string
	kcal: number
	items: string[]
}

export interface DayOverview {
	/** Calendar day in the format YYYY-MM-DD */
	date: string
	kcal: number
	protein: number
	carbs: number
	fat: number
	entryCount: number
}

export interface DaySummary {
	kcal: number
	protein: number
	carbs: number
	fat: number
	/** Only meals that have entries on that day */
	meals: MealSummary[]
}

interface DiaryWeek {
	/** Monday of the week, YYYY-MM-DD */
	start: string
	days: DayOverview[]
	/** Average of the days with entries, null without such days */
	averageKcal: number | null
}

export type Nutrition = Pick<FoodEntry, 'kcal' | 'protein' | 'carbs' | 'fat'>

/** Food from the database (Open Food Facts snapshot), as returned by the search */
/** What a user can report as wrong about a product */
export type FoodReportReason = 'nutrition' | 'unit' | 'quantity' | 'name' | 'other'

export interface FoodProduct {
	code: string
	name: string
	brand?: string
	/** g for solid foods, ml for drinks */
	unit: BaseUnit
	/** Nutrition values per 100 g or 100 ml */
	per100: Nutrition
	/** One serving in g or ml, if Open Food Facts knows it */
	serving?: number
	/** Package contents in g or ml, if known */
	packageSize?: number
}

export interface WeightEntry {
	id: string
	/** Calendar day in the format YYYY-MM-DD */
	date: string
	kg: number
}

export interface WeightPoint extends WeightEntry {
	time: number
	/** Average of all entries in the 7 days up to and including this day */
	weeklyAverage: number
}

export interface WeeklyBalance {
	/** Average of the last 7 days up to the newest entry */
	average: number
	/** Average of the 7 days before, null if there are no entries there */
	previousAverage: number | null
	/** average - previousAverage, negative means weight was lost */
	balance: number | null
}

export interface WeightPeriod {
	/** In the address and the select, e.g. "30" or "gesamt" */
	value: string
	/** Infinity for the whole history */
	days: number
	label: string
	phrase: string
}

export type BarcodeReader = Pick<BarcodeDetectorPonyfill, 'detect'>

export type TrackingEntryKind = 'food' | 'weight'

export interface EntryPreset {
	date?: string
	meal?: MealType
	savedMealId?: string
}

export interface TrackedDay {
	/** YYYY-MM-DD */
	date: string
	/** Targets that applied on that day, null without daily needs */
	goals: NutritionGoals | null
	entries: FoodEntry[]
}

export interface EntryTarget {
	/** YYYY-MM-DD, not in the future */
	date: string
	meal: MealType
}

/**
 * Foods from the backend. It searches the imported Open Food Facts data set
 * (Germany, Austria, Switzerland), where every product has a name and all four nutrition values.
 */
export interface FoodProductResponse {
	code: string
	name: string
	brand: string | null
	base_unit: BaseUnit
	/** Nutrition values per 100 g or 100 ml */
	nutrition_per_100: Nutrition
	/** Serving in g or ml, null means: no servings */
	serving_quantity: number | null
	/** Package contents in g or ml, null if unknown */
	package_quantity: number | null
}

/** Unit in the backend: g, ml or portion. toApiAmount converts packages to g or ml. */
export type FoodUnitResponse = BaseUnit | 'portion'

export interface MacrosResponse {
	kcal: number
	protein: number
	carbs: number
	fat: number
}

export interface TrackingEntryResponse extends MacrosResponse {
	id: number
	source: FoodEntrySource
	food_name: string
	brand: string | null
	off_code: string | null
	nutrition_per_100: MacrosResponse | null
	serving_quantity: number | null
	amount: number
	unit: FoodUnitResponse
	consumed_on: string
	meal_type: MealType
}

export interface DaySummaryResponse {
	date: string
	/** Targets valid on this day, null without daily needs */
	targets: MacrosResponse | null
	intake: MacrosResponse
	entries: TrackingEntryResponse[]
}

export interface WeightEntryResponse {
	id: number
	weight_kg: number
	measured_on: string
}

export type ScannerStatus = 'starting' | 'scanning' | 'denied' | 'unavailable' | 'failed'

export interface WeightChartPoint extends WeightPoint {
	isLast: boolean
	pointSize: number
}

export interface DiaryDay extends DayOverview {
	goalKcal: number | null
}

export interface DiaryDayWeek extends DiaryWeek {
	days: DiaryDay[]
}

/** Name and values of a food the user types in, for the portion eaten */
export interface ManualFood extends Nutrition {
	name: string
}

/** A page of calendar weeks with entries, newest first */
export interface WeekPage<T> {
	weeks: T[]
	/** Cursor for the next older page, null when there is none */
	nextBefore: string | null
	/** All weeks with entries in the range, regardless of the cursor */
	total: number
}

export interface WeekQuery {
	/** ISO week like 2026-W40: only weeks before it */
	before?: string
	/** YYYY-MM-DD: weeks that share a day with the range */
	from?: string
	to?: string
}

export interface FoodWeekSummary {
	/** Monday, YYYY-MM-DD */
	start: string
	daysCount: number
	averageKcal: number
}

export interface WeightWeekSummary {
	/** Monday, YYYY-MM-DD */
	start: string
	average: number
	count: number
}

interface WeekPageResponse<T> {
	results: T[]
	next_before: string | null
	total_weeks: number
}

export type FoodWeeksResponse = WeekPageResponse<{
	week_start: string
	days_count: number
	average_kcal: number
}>

export type WeightWeeksResponse = WeekPageResponse<{
	week_start: string
	average_kg: number
	entries_count: number
}>

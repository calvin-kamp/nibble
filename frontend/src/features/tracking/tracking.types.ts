import type { BarcodeDetector as BarcodeDetectorPonyfill } from 'barcode-detector/ponyfill'

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack'

export interface FoodEntry {
	id: string
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
	/** Brand, if the food comes from the search and has one */
	brand?: string
	/** Amount, if the food comes from the search */
	quantity?: FoodQuantity
	/** Open Food Facts barcode, if the food comes from the search */
	productCode?: string
}

/** Grams or millilitres: what a product's nutrition values refer to (per 100) */
export type BaseUnit = 'g' | 'ml'

/** Units for logging: the base unit, one serving or a whole package */
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

export interface MealSummary {
	meal: MealType
	label: string
	kcal: number
	/** Food names, without duplicates */
	items: string[]
}

/** One day in the diary list */
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

/** Days of a calendar week (Monday to Sunday) in the diary list */
export interface DiaryWeek {
	/** Monday of the week, YYYY-MM-DD */
	start: string
	days: DayOverview[]
	/** Average of the days with entries, null without such days */
	averageKcal: number | null
}

export type Nutrition = Pick<FoodEntry, 'kcal' | 'protein' | 'carbs' | 'fat'>

/** Food from the database (Open Food Facts snapshot), as returned by the search */
export interface FoodProduct {
	/** Barcode, the key at Open Food Facts */
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
	/** In the select, e.g. "Letzte 30 Tage" */
	label: string
	/** In a sentence, e.g. "in den letzten 30 Tagen" */
	phrase: string
}

export type BarcodeReader = Pick<BarcodeDetectorPonyfill, 'detect'>

export type TrackingEntryKind = 'food' | 'weight'

/** Prefill, e.g. from a diary day: date and meal are already in the form */
export interface EntryPreset {
	date?: string
	meal?: MealType
	/** A saved meal; the dialog then starts on the "Mahlzeiten" tab */
	savedMealId?: string
}

export interface TrackedDay {
	/** YYYY-MM-DD */
	date: string
	/** Targets that applied on that day, null without daily needs */
	goals: NutritionGoals | null
	entries: FoodEntry[]
}

/** Where a new entry goes */
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
	/** off: food from the search, meal: from a saved meal */
	source: 'off' | 'meal'
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

/** Camera state of the barcode scanner */
export type ScannerStatus = 'starting' | 'scanning' | 'denied' | 'unavailable' | 'failed'

export interface WeightChartPoint extends WeightPoint {
	isLast: boolean
	pointSize: number
}

/** One day of the diary list with the calorie target that applied that day */
export interface DiaryDay extends DayOverview {
	goalKcal: number | null
}

export interface DiaryDayWeek extends DiaryWeek {
	days: DiaryDay[]
}

import type {
	BaseUnit,
	DaySummaryResponse,
	EntryTarget,
	FoodEntry,
	FoodProduct,
	FoodProductResponse,
	FoodReportReason,
	FoodQuantity,
	FoodUnit,
	FoodUnitResponse,
	FoodWeekSummary,
	FoodWeeksResponse,
	MacrosResponse,
	ManualFood,
	NutritionGoals,
	TrackedDay,
	TrackingEntryResponse,
	WeekPage,
	WeekQuery,
	WeightEntry,
	WeightEntryResponse,
	WeightWeekSummary,
	WeightWeeksResponse,
} from '@features/tracking/tracking.types'

import { notifyTrackingChanged } from '@features/tracking/composables/tracking-changes'

import { isBarcode, normalizeBarcode, toQuantity } from '@features/tracking/tracking.utils'
import { ApiError, apiRequest, toQuery, type Paginated } from '@shared/api/client'
import { addDays, toIsoDate } from '@shared/utils/date'

// Entries, days and weight live in the backend. Everything under /tracking requires consent;
// without it the API responds with 403 consent_required. The functions throw ApiError.
// After every change, pages are notified via notifyTrackingChanged().

function toFoodProduct(product: FoodProductResponse): FoodProduct {
	return {
		code: product.code,
		name: product.name,
		brand: product.brand ?? undefined,
		unit: product.base_unit,
		per100: product.nutrition_per_100,
		serving: product.serving_quantity ?? undefined,
		packageSize: product.package_quantity ?? undefined,
	}
}

/**
 * Amount as the backend expects it. Packages are sent in the base unit, servings are called
 * portion there.
 */
export function toApiAmount(
	product: FoodProduct,
	value: number,
	unit: FoodUnit,
): { amount: number; unit: FoodUnitResponse } {
	if (unit === 'serving') return { amount: value, unit: 'portion' }
	if (unit === 'package')
		return { amount: toQuantity(product, value, unit).base, unit: product.unit }

	return { amount: value, unit }
}

export function fromApiAmount(
	amount: number,
	unit: FoodUnitResponse,
	servingQuantity: number | null,
	baseUnit: BaseUnit,
): FoodQuantity {
	if (unit === 'portion') {
		return {
			value: amount,
			unit: 'serving',
			base: Math.round(amount * (servingQuantity ?? 0) * 10) / 10,
			baseUnit,
		}
	}

	return { value: amount, unit, base: amount, baseUnit: unit }
}

function toFoodEntry(entry: TrackingEntryResponse): FoodEntry {
	// The backend does not return the base unit for entries, so servings fall back to g
	const baseUnit = entry.unit === 'ml' ? 'ml' : 'g'

	return {
		id: String(entry.id),
		source: entry.source,
		date: entry.consumed_on,
		meal: entry.meal_type,
		name: entry.food_name,
		kcal: Math.round(entry.kcal),
		protein: entry.protein,
		carbs: entry.carbs,
		fat: entry.fat,
		brand: entry.brand ?? undefined,
		quantity:
			entry.source === 'off'
				? fromApiAmount(entry.amount, entry.unit, entry.serving_quantity, baseUnit)
				: undefined,
		productCode: entry.off_code ?? undefined,
		product:
			entry.source === 'off' && entry.nutrition_per_100
				? {
						code: entry.off_code ?? '',
						name: entry.food_name,
						brand: entry.brand ?? undefined,
						unit: baseUnit,
						per100: entry.nutrition_per_100,
						serving: entry.serving_quantity ?? undefined,
					}
				: undefined,
	}
}

function toWeightEntry(entry: WeightEntryResponse): WeightEntry {
	return { id: String(entry.id), date: entry.measured_on, kg: entry.weight_kg }
}

function toTrackedDay(day: DaySummaryResponse): TrackedDay {
	return { date: day.date, goals: day.targets, entries: day.entries.map(toFoodEntry) }
}

export async function fetchDay(date: string): Promise<TrackedDay> {
	return toTrackedDay(await apiRequest<DaySummaryResponse>(`/tracking/days/${date}`))
}

/** The backend returns at most this many days per request */
const MAX_DAYS_PER_REQUEST = 92

/**
 * Every day from first to last, newest first, e.g. five weeks of the diary. One request per
 * 92 days instead of one per day, which would soon reach the API's rate limit.
 */
async function fetchDayRange(first: string, last: string): Promise<TrackedDay[]> {
	const chunks: [string, string][] = []

	for (let end = last; end >= first; end = addDays(end, -MAX_DAYS_PER_REQUEST)) {
		const start = addDays(end, -(MAX_DAYS_PER_REQUEST - 1))

		chunks.push([start < first ? first : start, end])
	}

	const pages = await Promise.all(
		chunks.map(([from, to]) =>
			apiRequest<DaySummaryResponse[]>(`/tracking/days${toQuery({ from, to })}`),
		),
	)

	return pages.flat().map(toTrackedDay)
}

/**
 * The days of these weeks, newest first. Weeks that follow each other share a request, so
 * twenty weeks in a row cost two requests, not twenty.
 */
export async function fetchWeekDays(starts: string[]): Promise<TrackedDay[]> {
	const today = toIsoDate()
	const runs: [string, string][] = []

	for (const start of [...new Set(starts)].toSorted().toReversed()) {
		const end = addDays(start, 6) > today ? today : addDays(start, 6)
		const run = runs[runs.length - 1]

		if (run && run[0] === addDays(start, 7)) run[0] = start
		else runs.push([start, end])
	}

	const pages = await Promise.all(runs.map(([from, to]) => fetchDayRange(from, to)))

	return pages.flat()
}

function weekQuery(query: WeekQuery): string {
	return toQuery({ before: query.before, from: query.from, to: query.to })
}

/** Weeks with food entries, five per page */
export async function fetchFoodWeeks(query: WeekQuery = {}): Promise<WeekPage<FoodWeekSummary>> {
	const page = await apiRequest<FoodWeeksResponse>(`/tracking/days/weeks${weekQuery(query)}`)

	return {
		weeks: page.results.map((week) => ({
			start: week.week_start,
			daysCount: week.days_count,
			averageKcal: week.average_kcal,
		})),
		nextBefore: page.next_before,
		total: page.total_weeks,
	}
}

/** Weeks with weight entries, five per page */
export async function fetchWeightWeeks(
	query: WeekQuery = {},
): Promise<WeekPage<WeightWeekSummary>> {
	const page = await apiRequest<WeightWeeksResponse>(`/tracking/weights/weeks${weekQuery(query)}`)

	return {
		weeks: page.results.map((week) => ({
			start: week.week_start,
			average: week.average_kg,
			count: week.entries_count,
		})),
		nextBefore: page.next_before,
		total: page.total_weeks,
	}
}

const RECENT_DAYS = 14

/**
 * Foods from the search logged in the last two weeks, newest first, each product once. For the
 * quick selection in the food dialog; entries without a barcode cannot be looked up again.
 */
export async function fetchRecentFoods(limit: number): Promise<FoodEntry[]> {
	const today = toIsoDate()
	const days = await fetchDayRange(addDays(today, -(RECENT_DAYS - 1)), today)
	const recent = new Map<string, FoodEntry>()

	for (const entry of days.flatMap((day) => [...day.entries].reverse())) {
		if (entry.productCode && !recent.has(entry.productCode)) {
			recent.set(entry.productCode, entry)
		}
	}

	return [...recent.values()].slice(0, limit)
}

/** Daily needs valid today, null while none are set */
export async function fetchCurrentGoals(): Promise<NutritionGoals | null> {
	const { targets } = await apiRequest<{ targets: MacrosResponse | null }>('/tracking/goal')

	return targets
}

/** A food from the search. The backend calculates nutrition values from amount and unit. */
export async function addProductEntry(
	target: EntryTarget & { product: FoodProduct; amount: number; unit: FoodUnit },
): Promise<FoodEntry> {
	const entry = await apiRequest<TrackingEntryResponse>('/tracking/entries', {
		method: 'POST',
		body: {
			off_code: target.product.code,
			...toApiAmount(target.product, target.amount, target.unit),
			consumed_on: target.date,
			meal_type: target.meal,
		},
	})

	notifyTrackingChanged()

	return toFoodEntry(entry)
}

/** A food the search does not know: name and values of the portion, typed in */
export async function addManualEntry(
	target: EntryTarget & { food: ManualFood },
): Promise<FoodEntry> {
	const entry = await apiRequest<TrackingEntryResponse>('/tracking/entries/manual', {
		method: 'POST',
		body: {
			food_name: target.food.name,
			kcal: target.food.kcal,
			protein: target.food.protein,
			carbs: target.food.carbs,
			fat: target.food.fat,
			consumed_on: target.date,
			meal_type: target.meal,
		},
	})

	notifyTrackingChanged()

	return toFoodEntry(entry)
}

export async function addSavedMealEntry(
	target: EntryTarget & { mealId: string },
): Promise<FoodEntry> {
	const entry = await apiRequest<TrackingEntryResponse>('/tracking/entries/from-meal', {
		method: 'POST',
		body: { meal_id: Number(target.mealId), consumed_on: target.date, meal_type: target.meal },
	})

	notifyTrackingChanged()

	return toFoodEntry(entry)
}

/**
 * Changes day, meal and, for foods from the search, the amount. The backend recalculates the
 * nutrition values from the values per 100 stored in the entry. Foods typed in change their
 * name and values instead.
 */
export async function updateFoodEntry(
	entry: FoodEntry,
	changes: EntryTarget & { amount?: number; unit?: FoodUnit; food?: ManualFood },
): Promise<FoodEntry> {
	const amount =
		entry.product && changes.amount !== undefined && changes.unit
			? toApiAmount(entry.product, changes.amount, changes.unit)
			: {}

	const values =
		entry.source === 'manual' && changes.food
			? {
					food_name: changes.food.name,
					kcal: changes.food.kcal,
					protein: changes.food.protein,
					carbs: changes.food.carbs,
					fat: changes.food.fat,
				}
			: {}

	const updated = await apiRequest<TrackingEntryResponse>(`/tracking/entries/${entry.id}`, {
		method: 'PATCH',
		body: { consumed_on: changes.date, meal_type: changes.meal, ...amount, ...values },
	})

	notifyTrackingChanged()

	return toFoodEntry(updated)
}

export async function deleteFoodEntry(id: string): Promise<void> {
	await apiRequest(`/tracking/entries/${id}`, { method: 'DELETE' })
	notifyTrackingChanged()
}

export async function fetchWeightEntries(): Promise<WeightEntry[]> {
	const { results } = await apiRequest<{ results: WeightEntryResponse[] }>(
		'/tracking/weights?range=all',
	)

	return results.map(toWeightEntry)
}

/** One weight per day: an existing one for that day is replaced */
export async function saveWeightEntry(
	entry: Pick<WeightEntry, 'date' | 'kg'>,
): Promise<WeightEntry> {
	const body = { weight_kg: Math.round(entry.kg * 10) / 10, measured_on: entry.date }
	let saved: WeightEntryResponse

	try {
		saved = await apiRequest<WeightEntryResponse>('/tracking/weights', { method: 'POST', body })
	} catch (error) {
		if (!(error instanceof ApiError && error.code === 'weight_entry_exists')) throw error

		const existing = (await fetchWeightEntries()).find((item) => item.date === entry.date)

		if (!existing) throw error

		saved = await apiRequest<WeightEntryResponse>(`/tracking/weights/${existing.id}`, {
			method: 'PATCH',
			body: { weight_kg: body.weight_kg },
		})
	}

	notifyTrackingChanged()

	return toWeightEntry(saved)
}

export async function deleteWeightEntry(id: string): Promise<void> {
	await apiRequest(`/tracking/weights/${id}`, { method: 'DELETE' })
	notifyTrackingChanged()
}

/**
 * Searches foods by name, brand or barcode, first 20 matches. With several words, each one has
 * to appear in the name or brand, e.g. "yfood vanilla". A barcode returns at most one product.
 * Throws ApiError on errors, e.g. 400 for fewer than 2 characters.
 */
export async function searchFoods(query: string): Promise<FoodProduct[]> {
	const term = query.trim()
	const params = isBarcode(term) ? { barcode: normalizeBarcode(term) } : { q: term }
	const { results } = await apiRequest<Paginated<FoodProductResponse>>(
		`/foods/search${toQuery(params)}`,
	)

	return results.map(toFoodProduct)
}

/**
 * The product behind a scanned barcode, or null if the data set does not have it. Open Food
 * Facts keeps some UPC-A codes (12 digits) as EAN-13 with a leading zero, so both are tried.
 */
export async function findByBarcode(barcode: string): Promise<FoodProduct | null> {
	const [product] = await searchFoods(barcode)

	if (product || barcode.length !== 12) return product ?? null

	const [padded] = await searchFoods(`0${barcode}`)

	return padded ?? null
}

/** A product by its code, also generic foods without barcode (e.g. a banana); null if gone */
export async function findByCode(code: string): Promise<FoodProduct | null> {
	if (isBarcode(code)) return findByBarcode(code)

	const { results } = await apiRequest<Paginated<FoodProductResponse>>(
		`/foods/search${toQuery({ code })}`,
	)

	return results[0] ? toFoodProduct(results[0]) : null
}

/** Tells staff that something about a product is wrong. Nothing about the sender is stored. */
export async function reportFood(
	code: string,
	reason: FoodReportReason,
	comment: string,
): Promise<void> {
	await apiRequest(`/foods/${code}/report`, {
		method: 'POST',
		body: { reason, comment: comment.trim() },
	})
}

import type {
	BaseUnit,
	DaySummaryResponse,
	EntryTarget,
	FoodEntry,
	FoodProduct,
	FoodProductResponse,
	FoodQuantity,
	FoodUnit,
	FoodUnitResponse,
	MacrosResponse,
	NutritionGoals,
	TrackedDay,
	TrackingEntryResponse,
	WeightEntry,
	WeightEntryResponse,
} from '@features/tracking/tracking.types'

import { notifyTrackingChanged } from '@features/tracking/composables/tracking-changes'

import { isBarcode, normalizeBarcode, toQuantity } from '@features/tracking/tracking.utils'
import { ApiError, apiRequest, toQuery, type Paginated } from '@shared/api/client'

// Entries, days and weight live in the backend. Everything under /tracking requires consent;
// without it the API responds with 403 consent_required. The functions throw ApiError.
// After every change, pages are notified via notifyTrackingChanged().

export function toFoodProduct(product: FoodProductResponse): FoodProduct {
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

/** Amount from the backend for display, e.g. 2 servings that equal 80 g */
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
	}
}

function toWeightEntry(entry: WeightEntryResponse): WeightEntry {
	return { id: String(entry.id), date: entry.measured_on, kg: entry.weight_kg }
}

export async function fetchDay(date: string): Promise<TrackedDay> {
	const day = await apiRequest<DaySummaryResponse>(`/tracking/days/${date}`)

	return { date: day.date, goals: day.targets, entries: day.entries.map(toFoodEntry) }
}

/** Several days at once, e.g. a week in the diary. One request per day. */
export function fetchDays(dates: string[]): Promise<TrackedDay[]> {
	return Promise.all(dates.map(fetchDay))
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

/** A saved meal as one serving with its stored nutrition values */
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

export async function deleteFoodEntry(id: string): Promise<void> {
	await apiRequest(`/tracking/entries/${id}`, { method: 'DELETE' })
	notifyTrackingChanged()
}

/** The whole history, oldest first */
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

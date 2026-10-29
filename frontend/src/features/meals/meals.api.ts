import type {
	MealFormValues,
	MealItem,
	MealItemResponse,
	MealResponse,
	SavedMeal,
} from '@features/meals/meals.types'
import type { BaseUnit } from '@features/tracking/tracking.types'

import { notifyTrackingChanged } from '@features/tracking/composables/tracking-changes'

import { fromApiAmount, toApiAmount } from '@features/tracking/tracking.api'
import { apiRequest } from '@shared/api/client'

// Saved meals live in the backend under /tracking/meals, notes included, and require consent.
// The backend calculates nutrition values on save. The functions throw ApiError, e.g. 404.

function toMealItem(item: MealItemResponse, index: number): MealItem {
	// The backend does not return the base unit, so servings fall back to g
	const baseUnit: BaseUnit = item.unit === 'ml' ? 'ml' : 'g'

	return {
		id: String(index),
		product: {
			code: item.off_code,
			name: item.food_name,
			brand: item.brand ?? undefined,
			unit: baseUnit,
			per100: item.nutrition_per_100,
			serving: item.serving_quantity ?? undefined,
		},
		quantity: fromApiAmount(item.amount, item.unit, item.serving_quantity, baseUnit),
		kcal: Math.round(item.kcal),
		protein: item.protein,
		carbs: item.carbs,
		fat: item.fat,
	}
}

function toSavedMeal(meal: MealResponse): SavedMeal {
	return {
		id: String(meal.id),
		name: meal.name,
		note: meal.note || undefined,
		items: meal.items.map(toMealItem),
		kcal: Math.round(meal.totals.kcal),
		protein: meal.totals.protein,
		carbs: meal.totals.carbs,
		fat: meal.totals.fat,
	}
}

function toInput(values: MealFormValues) {
	return {
		name: values.name.trim(),
		// Without a note the backend clears an existing one
		note: values.note?.trim() ?? '',
		items: values.items.map((item) => ({
			off_code: item.product.code,
			...toApiAmount(item.product, item.amount!, item.unit!),
		})),
	}
}

/** Alphabetical */
export async function listMeals(): Promise<SavedMeal[]> {
	const meals = await apiRequest<MealResponse[]>('/tracking/meals')

	return meals.map(toSavedMeal)
}

export async function fetchMeal(id: string): Promise<SavedMeal> {
	return toSavedMeal(await apiRequest<MealResponse>(`/tracking/meals/${id}`))
}

export async function createMeal(values: MealFormValues): Promise<SavedMeal> {
	const meal = await apiRequest<MealResponse>('/tracking/meals', {
		method: 'POST',
		body: toInput(values),
	})

	notifyTrackingChanged()

	return toSavedMeal(meal)
}

/** Entries already logged from this meal stay as they are */
export async function updateMeal(id: string, values: MealFormValues): Promise<SavedMeal> {
	const meal = await apiRequest<MealResponse>(`/tracking/meals/${id}`, {
		method: 'PUT',
		body: toInput(values),
	})

	notifyTrackingChanged()

	return toSavedMeal(meal)
}

export async function deleteMeal(id: string): Promise<void> {
	await apiRequest(`/tracking/meals/${id}`, { method: 'DELETE' })
	notifyTrackingChanged()
}

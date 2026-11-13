import type { MealFormValues, MealItemResponse, MealResponse } from '../meals.types'
import type { FoodProduct } from '@features/tracking/tracking.types'

import { afterEach, describe, expect, test, vi } from 'vitest'

import { notifyTrackingChanged } from '@features/tracking/composables/tracking-changes'

import { createMeal, deleteMeal, fetchMeal, listMeals, updateMeal } from '../meals.api'
import { apiRequest } from '@shared/api/client'

vi.mock('@shared/api/client', () => ({ apiRequest: vi.fn() }))
vi.mock('@features/tracking/composables/tracking-changes', () => ({
	notifyTrackingChanged: vi.fn(),
}))

// A product item as the backend returns it: 150 g of a product with 200 kcal per 100 g
function productResponse(overrides: Partial<MealItemResponse> = {}): MealItemResponse {
	return {
		off_code: '4000000000000',
		food_name: 'Haferflocken',
		brand: 'Kölln',
		amount: 150,
		unit: 'g',
		nutrition_per_100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
		serving_quantity: 40,
		kcal: 300,
		protein: 15,
		carbs: 45,
		fat: 7.5,
		...overrides,
	}
}

// An own item has no product code and no values per 100 g
const ownResponse: MealItemResponse = {
	off_code: null,
	food_name: 'Honig',
	brand: null,
	amount: 1,
	unit: 'portion',
	nutrition_per_100: null,
	serving_quantity: null,
	kcal: 60,
	protein: 0,
	carbs: 16,
	fat: 0,
}

function mealResponse(items: MealItemResponse[]): MealResponse {
	return {
		id: 7,
		name: 'Frühstück',
		items,
		totals: { kcal: 360, protein: 15, carbs: 61, fat: 7.5 },
	}
}

const product: FoodProduct = {
	code: '4000000000000',
	name: 'Haferflocken',
	unit: 'g',
	per100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
	serving: 40,
	packageSize: 500,
}

afterEach(() => {
	vi.resetAllMocks()
})

describe('turn a meal from the backend into a saved meal', () => {
	// the mapping is the same for every function, it is tested through fetchMeal
	async function fetchWith(items: MealItemResponse[]) {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse(items))

		return fetchMeal('7')
	}

	test('takes over id, name and totals', async () => {
		const meal = await fetchWith([])

		expect(meal).toEqual({
			id: '7',
			name: 'Frühstück',
			items: [],
			kcal: 360,
			protein: 15,
			carbs: 61,
			fat: 7.5,
		})
	})

	test('rounds the kcal of the meal and of its items to whole numbers', async () => {
		vi.mocked(apiRequest).mockResolvedValue({
			...mealResponse([productResponse({ kcal: 299.6 })]),
			totals: { kcal: 359.4, protein: 15, carbs: 61, fat: 7.5 },
		})

		const meal = await fetchMeal('7')

		expect(meal.kcal).toBe(359)
		expect(meal.items[0]?.kcal).toBe(300)
	})

	test('numbers the items in their order', async () => {
		const meal = await fetchWith([productResponse(), ownResponse])

		expect(meal.items.map((item) => item.id)).toEqual(['0', '1'])
	})

	test('keeps the product of a product item, so the amount can still be changed', async () => {
		const [item] = (await fetchWith([productResponse()])).items

		expect(item?.product).toEqual({
			code: '4000000000000',
			name: 'Haferflocken',
			brand: 'Kölln',
			unit: 'g',
			per100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
			serving: 40,
		})
		expect(item?.quantity).toEqual({ value: 150, unit: 'g', base: 150, baseUnit: 'g' })
	})

	test('converts servings into grams', async () => {
		const [item] = (await fetchWith([productResponse({ amount: 2, unit: 'portion' })])).items

		// 2 servings of 40 g are 80 g
		expect(item?.quantity).toEqual({ value: 2, unit: 'serving', base: 80, baseUnit: 'g' })
	})

	test('keeps millilitres for drinks', async () => {
		const [item] = (await fetchWith([productResponse({ amount: 330, unit: 'ml' })])).items

		expect(item?.product?.unit).toBe('ml')
		expect(item?.quantity?.baseUnit).toBe('ml')
	})

	test('leaves out the brand when the backend has none', async () => {
		const [item] = (await fetchWith([productResponse({ brand: null })])).items

		expect(item?.product?.brand).toBeUndefined()
	})

	test('keeps an own item without product and amount', async () => {
		const [item] = (await fetchWith([ownResponse])).items

		expect(item).toEqual({ id: '0', name: 'Honig', kcal: 60, protein: 0, carbs: 16, fat: 0 })
	})

	// without the values per 100 g the amount could not be recalculated
	test('treats a product without values per 100 g as an own item', async () => {
		const [item] = (await fetchWith([productResponse({ nutrition_per_100: null })])).items

		expect(item?.product).toBeUndefined()
		expect(item?.quantity).toBeUndefined()
	})
})

describe('load the saved meals', () => {
	test('lists all meals', async () => {
		vi.mocked(apiRequest).mockResolvedValue([mealResponse([]), { ...mealResponse([]), id: 8 }])

		const meals = await listMeals()

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals')
		expect(meals.map((meal) => meal.id)).toEqual(['7', '8'])
	})

	test('loads one meal by its id', async () => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		await fetchMeal('7')

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals/7')
	})
})

describe('save a meal', () => {
	const values: MealFormValues = {
		name: '  Frühstück  ',
		items: [
			{ product, amount: 150, unit: 'g' },
			{ own: { name: ' Honig ', kcal: 60, protein: 0, carbs: 16, fat: 0, withMacros: true } },
		],
	}

	// the body the backend gets for these values
	const body = {
		name: 'Frühstück',
		items: [
			{ off_code: '4000000000000', amount: 150, unit: 'g' },
			{ food_name: 'Honig', kcal: 60, protein: 0, carbs: 16, fat: 0 },
		],
	}

	test('creates a new meal', async () => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		await createMeal(values)

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals', { method: 'POST', body })
	})

	test('updates an existing meal', async () => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		await updateMeal('7', values)

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals/7', { method: 'PUT', body })
	})

	test('returns the meal as the backend saved it', async () => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		expect((await createMeal(values)).id).toBe('7')
	})

	// the backend counts in servings or grams, a package is sent as its grams
	test.each<[string, MealFormValues['items'][number], object]>([
		[
			'servings as portions',
			{ product, amount: 2, unit: 'serving' },
			{ amount: 2, unit: 'portion' },
		],
		['a package as grams', { product, amount: 1, unit: 'package' }, { amount: 500, unit: 'g' }],
	])('sends %s', async (_description, item, amount) => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		await createMeal({ name: 'Frühstück', items: [item] })

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals', {
			method: 'POST',
			body: { name: 'Frühstück', items: [{ off_code: '4000000000000', ...amount }] },
		})
	})
})

describe('tell the diary about changes', () => {
	test.each([
		['creating', () => createMeal({ name: 'Frühstück', items: [] })],
		['updating', () => updateMeal('7', { name: 'Frühstück', items: [] })],
		['deleting', () => deleteMeal('7')],
	])('after %s a meal', async (_description, change) => {
		vi.mocked(apiRequest).mockResolvedValue(mealResponse([]))

		await change()

		expect(notifyTrackingChanged).toHaveBeenCalledOnce()
	})

	// nothing changed, so the diary must not reload
	test.each([
		['creating', () => createMeal({ name: 'Frühstück', items: [] })],
		['updating', () => updateMeal('7', { name: 'Frühstück', items: [] })],
		['deleting', () => deleteMeal('7')],
	])('not when %s a meal fails', async (_description, change) => {
		vi.mocked(apiRequest).mockRejectedValue(new Error('network'))

		await expect(change()).rejects.toThrow('network')
		expect(notifyTrackingChanged).not.toHaveBeenCalled()
	})
})

describe('delete a meal', () => {
	test('deletes the meal by its id', async () => {
		vi.mocked(apiRequest).mockResolvedValue(undefined)

		await deleteMeal('7')

		expect(apiRequest).toHaveBeenCalledWith('/tracking/meals/7', { method: 'DELETE' })
	})
})

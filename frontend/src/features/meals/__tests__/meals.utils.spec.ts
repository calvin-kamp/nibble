import type { MealItem, SavedMeal } from '../meals.types'
import type { FoodProduct } from '@features/tracking/tracking.types'

import { describe, expect, test } from 'vitest'

import { draftNutrition, sumNutrition, toFormValues } from '../meals.utils'

describe('sum up the nutrition of a meal', () => {
	test('returns the values of a single item unchanged', () => {
		expect(sumNutrition([{ kcal: 69, protein: 10, carbs: 5, fat: 1 }])).toEqual({
			kcal: 69,
			protein: 10,
			carbs: 5,
			fat: 1,
		})
	})

	test('adds up the values of several items', () => {
		expect(
			sumNutrition([
				{ kcal: 69, protein: 10, carbs: 5, fat: 1 },
				{ kcal: 74, protein: 9.6, carbs: 4.1, fat: 1.6 },
			]),
		).toEqual({
			kcal: 143,
			protein: 19.6,
			carbs: 9.1,
			fat: 2.6,
		})
	})

	test('returns 0 for every value without items', () => {
		expect(sumNutrition([])).toEqual({ kcal: 0, protein: 0, carbs: 0, fat: 0 })
	})

	// in binary floating point 0.1 + 0.2 is 0.30000000000000004, which the meal would show
	test('rounds the macros to one decimal place', () => {
		expect(
			sumNutrition([
				{ kcal: 10, protein: 0.1, carbs: 0.1, fat: 0.1 },
				{ kcal: 20, protein: 0.2, carbs: 0.2, fat: 0.2 },
			]),
		).toEqual({ kcal: 30, protein: 0.3, carbs: 0.3, fat: 0.3 })
	})

	// the error grows with every item: ten times 0.1 is 0.9999999999999999 without rounding
	test('stays exact over many items', () => {
		const items = Array.from({ length: 10 }, () => ({
			kcal: 5,
			protein: 0.1,
			carbs: 0.1,
			fat: 0.1,
		}))

		expect(sumNutrition(items)).toEqual({ kcal: 50, protein: 1, carbs: 1, fat: 1 })
	})
})

// 100 g have 200 kcal, 10 g protein, 30 g carbs and 5 g fat; a serving is 40 g, a package 500 g
const product: FoodProduct = {
	code: '4000000000000',
	name: 'Haferflocken',
	unit: 'g',
	per100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
	serving: 40,
	packageSize: 500,
}

describe('calculate the nutrition of a meal item in the form', () => {
	describe('for a product', () => {
		test('scales the values per 100 g to the amount', () => {
			// 150 g are 1.5 times the values per 100 g
			expect(draftNutrition({ product, amount: 150, unit: 'g' })).toEqual({
				kcal: 300,
				protein: 15,
				carbs: 45,
				fat: 7.5,
			})
		})

		test('converts servings into grams', () => {
			// 2 servings of 40 g are 80 g
			expect(draftNutrition({ product, amount: 2, unit: 'serving' })).toEqual({
				kcal: 160,
				protein: 8,
				carbs: 24,
				fat: 4,
			})
		})

		test('converts a package into grams', () => {
			expect(draftNutrition({ product, amount: 1, unit: 'package' })).toEqual({
				kcal: 1000,
				protein: 50,
				carbs: 150,
				fat: 25,
			})
		})

		// the user has picked a product but not finished the amount yet
		test.each([
			['without an amount', { product, unit: 'g' as const }],
			['with an amount of 0', { product, amount: 0, unit: 'g' as const }],
			['without a unit', { product, amount: 150 }],
		])('returns null %s', (_description, draft) => {
			expect(draftNutrition(draft)).toBeNull()
		})
	})

	describe('for an own item', () => {
		test('takes the kcal as entered', () => {
			expect(draftNutrition({ own: { kcal: 250, protein: 10, carbs: 20, fat: 5 } })).toEqual({
				kcal: 250,
				protein: 10,
				carbs: 20,
				fat: 5,
			})
		})

		test('calculates the kcal from the macros when they are missing', () => {
			// 10 * 4 + 20 * 4 + 5 * 9 = 165
			expect(draftNutrition({ own: { protein: 10, carbs: 20, fat: 5 } })?.kcal).toBe(165)
		})

		// kcal alone is a valid own item, its macros are 0 then
		test('accepts macros of 0', () => {
			expect(draftNutrition({ own: { kcal: 120, protein: 0, carbs: 0, fat: 0 } })).toEqual({
				kcal: 120,
				protein: 0,
				carbs: 0,
				fat: 0,
			})
		})

		test.each(['protein', 'carbs', 'fat'] as const)('returns null without %s', (macro) => {
			const own = { kcal: 250, protein: 10, carbs: 20, fat: 5 }
			delete (own as Partial<typeof own>)[macro]

			expect(draftNutrition({ own })).toBeNull()
		})

		test('returns null for an empty item', () => {
			expect(draftNutrition({})).toBeNull()
		})
	})
})

describe('fill the form with a saved meal', () => {
	// 2 servings of the product, 80 g with 160 kcal
	const productItem: MealItem = {
		id: '1',
		name: 'Haferflocken',
		kcal: 160,
		protein: 8,
		carbs: 24,
		fat: 4,
		product,
		quantity: { value: 2, unit: 'serving', base: 80, baseUnit: 'g' },
	}

	const ownItem: MealItem = {
		id: '2',
		name: 'Honig',
		kcal: 60,
		protein: 0,
		carbs: 16,
		fat: 0,
	}

	function makeMeal(items: MealItem[]): SavedMeal {
		return { id: '10', name: 'Frühstück', kcal: 0, protein: 0, carbs: 0, fat: 0, items }
	}

	test('keeps the name of the meal', () => {
		expect(toFormValues(makeMeal([])).name).toBe('Frühstück')
	})

	// the form asks for the amount in the unit the user chose, not in grams
	test('turns a product into product, amount and unit', () => {
		expect(toFormValues(makeMeal([productItem])).items).toEqual([
			{ product, amount: 2, unit: 'serving' },
		])
	})

	test('turns an own item into its name and values', () => {
		expect(toFormValues(makeMeal([ownItem])).items).toEqual([
			{ own: { name: 'Honig', kcal: 60, protein: 0, carbs: 16, fat: 0 } },
		])
	})

	// without an amount the product could not be recalculated, its saved values are kept instead
	test('keeps a product without amount as an own item', () => {
		const { quantity: _quantity, ...withoutQuantity } = productItem

		expect(toFormValues(makeMeal([withoutQuantity])).items).toEqual([
			{ own: { name: 'Haferflocken', kcal: 160, protein: 8, carbs: 24, fat: 4 } },
		])
	})

	test('keeps the order of the items', () => {
		const { items } = toFormValues(makeMeal([ownItem, productItem]))

		expect(items.map((item) => item.own?.name ?? item.product?.name)).toEqual([
			'Honig',
			'Haferflocken',
		])
	})
})

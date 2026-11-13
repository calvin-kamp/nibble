import type { MealFormValues, MealItemDraft } from '../meals.types'
import type { FoodProduct } from '@features/tracking/tracking.types'

import { describe, expect, test } from 'vitest'

import { mealZodSchema } from '../meals.schema'

const product: FoodProduct = {
	code: '4000000000000',
	name: 'Haferflocken',
	unit: 'g',
	per100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
	serving: 40,
}

const productItem: MealItemDraft = { product, amount: 150, unit: 'g' }

// 10 * 4 + 20 * 4 + 5 * 9 = 165 kcal from the macros, 250 kcal fit that
const ownItem: MealItemDraft = { own: { name: 'Honig', kcal: 250, protein: 10, carbs: 20, fat: 5 } }

// A valid meal with one product. Override only what a test is about.
function makeValues(overrides: Partial<MealFormValues> = {}): MealFormValues {
	return { name: 'Frühstück', items: [productItem], ...overrides }
}

// The fields that have an issue, as dotted paths such as 'items.0.amount'
function invalidFields(values: unknown): string[] {
	const result = mealZodSchema.safeParse(values)

	return result.success ? [] : result.error.issues.map((issue) => issue.path.join('.'))
}

function messagesFor(values: unknown, field: string): string[] {
	const result = mealZodSchema.safeParse(values)

	if (result.success) return []

	return result.error.issues
		.filter((issue) => issue.path.join('.') === field)
		.map((issue) => issue.message)
}

describe('validate a meal', () => {
	test('accepts a meal with a product and an own item', () => {
		expect(invalidFields(makeValues({ items: [productItem, ownItem] }))).toEqual([])
	})

	describe('check the name', () => {
		test('trims the name', () => {
			expect(mealZodSchema.parse(makeValues({ name: '  Frühstück  ' })).name).toBe(
				'Frühstück',
			)
		})

		test.each([
			['an empty name', ''],
			['a name of spaces only', '   '],
		])('rejects %s', (_description, name) => {
			expect(messagesFor(makeValues({ name }), 'name')).toEqual([
				'Wie soll die Mahlzeit heißen?',
			])
		})

		test('accepts 60 characters', () => {
			expect(invalidFields(makeValues({ name: 'a'.repeat(60) }))).toEqual([])
		})

		test('rejects 61 characters', () => {
			expect(messagesFor(makeValues({ name: 'a'.repeat(61) }), 'name')).toEqual([
				'Höchstens 60 Zeichen.',
			])
		})
	})

	test('requires at least one item', () => {
		expect(messagesFor(makeValues({ items: [] }), 'items')).toEqual([
			'Such mindestens ein Lebensmittel aus.',
		])
	})

	// the amount rules themselves are tested with tracking, here only that they apply to meals
	describe('check the amount of a product', () => {
		test('requires an amount', () => {
			expect(
				messagesFor(makeValues({ items: [{ product, unit: 'g' }] }), 'items.0.amount'),
			).toEqual(['Wie viel davon?'])
		})

		test.each([0, -1])('rejects an amount of %i', (amount) => {
			expect(invalidFields(makeValues({ items: [{ product, amount, unit: 'g' }] }))).toEqual([
				'items.0.amount',
			])
		})

		test('rejects an implausible amount', () => {
			const items = [{ product, amount: 51, unit: 'serving' as const }]

			expect(messagesFor(makeValues({ items }), 'items.0.amount')).toEqual([
				'Prüf die Menge noch mal.',
			])
		})
	})

	// the food rules themselves are tested with tracking, here only that they apply to meals
	describe('check an own item', () => {
		test('reports its errors under own', () => {
			const items = [{ own: { ...ownItem.own, name: '' } }]

			expect(invalidFields(makeValues({ items }))).toEqual(['items.0.own.name'])
		})

		test('checks the item at its own position in the list', () => {
			const items = [productItem, { own: { ...ownItem.own, name: '' } }]

			expect(invalidFields(makeValues({ items }))).toEqual(['items.1.own.name'])
		})

		test('requires name and values of an empty item', () => {
			expect(invalidFields(makeValues({ items: [{}] }))).toEqual([
				'items.0.own.name',
				'items.0.own.protein',
				'items.0.own.carbs',
				'items.0.own.fat',
				'items.0.own.kcal',
			])
		})

		// the backend would reject these values, so the form names what the macros give
		test('rejects kcal that do not fit the macros', () => {
			const items = [{ own: { ...ownItem.own, kcal: 50 } }]

			expect(messagesFor(makeValues({ items }), 'items.0.own.kcal')).toEqual([
				'Das passt nicht zu den Makros, daraus ergeben sich etwa 165 kcal.',
			])
		})
	})
})

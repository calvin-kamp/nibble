import type { CalorieCalculatorValues } from '../calorie-calculator.types'

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, test } from 'vitest'

import { usePendingCalculationStore } from '../calorie-calculator.store'

function makeValues(): CalorieCalculatorValues {
	return {
		sex: 'female',
		age: 30,
		height: 170,
		weight: 65,
		steps: 8000,
		goal: 'maintain',
		exercises: [],
	}
}

describe('keep the calculation of a guest through the registration', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
	})

	test('is empty at first', () => {
		expect(usePendingCalculationStore().values).toBeNull()
	})

	test('keeps the saved details', () => {
		const store = usePendingCalculationStore()

		store.save(makeValues())

		expect(store.values).toEqual(makeValues())
	})

	// the form keeps its own object, a later change there must not reach onboarding unnoticed
	test('keeps a copy, not the object of the form', () => {
		const store = usePendingCalculationStore()
		const values = makeValues()

		store.save(values)
		values.weight = 90

		expect(store.values?.weight).toBe(65)
	})

	test('replaces an earlier calculation', () => {
		const store = usePendingCalculationStore()

		store.save(makeValues())
		store.save({ ...makeValues(), goal: 'gain' })

		expect(store.values?.goal).toBe('gain')
	})

	test('forgets the details when cleared', () => {
		const store = usePendingCalculationStore()

		store.save(makeValues())
		store.clear()

		expect(store.values).toBeNull()
	})
})

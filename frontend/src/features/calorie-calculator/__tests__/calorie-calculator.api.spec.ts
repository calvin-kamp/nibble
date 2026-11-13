import type { NutritionSettings } from '@features/account/account.types'
import type { AuthUser, PersonalProfile } from '@features/auth/auth.types'
import type { WeightEntry } from '@features/tracking/tracking.types'

import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'

import { loadCalculatorPrefill } from '../calorie-calculator.api'
import { fetchNutritionSettings } from '@features/account/account.api'
import { fetchWeightEntries } from '@features/tracking/tracking.api'

vi.mock('@features/account/account.api', () => ({ fetchNutritionSettings: vi.fn() }))
vi.mock('@features/tracking/tracking.api', () => ({ fetchWeightEntries: vi.fn() }))

// A user with a complete profile, 30 years old on the pinned day. Override only the profile
// fields a test is about.
function makeUser(profile: Partial<PersonalProfile> = {}): AuthUser {
	return {
		id: 1,
		email: 'test@example.com',
		username: 'test',
		isEmailVerified: true,
		hasCompletedOnboarding: true,
		hasDataConsent: true,
		dataConsentChangedAt: null,
		isStaff: false,
		deletionScheduledFor: null,
		profile: { birthDate: '1996-06-15', heightCm: 180, sex: 'male', ...profile },
	}
}

function weightEntry(date: string, kg: number): WeightEntry {
	return { id: date, date, kg }
}

const settings: NutritionSettings = {
	needs: { kcal: 2000, protein: 150, carbs: 200, fat: 67, source: 'calculated' },
	goal: 'diet',
}

describe('load the account details into the calculator', () => {
	beforeEach(() => {
		vi.useFakeTimers()
		vi.setSystemTime(new Date(2026, 10, 11))

		vi.mocked(fetchWeightEntries).mockResolvedValue([
			weightEntry('2026-11-01', 82),
			weightEntry('2026-11-10', 80),
		])
		vi.mocked(fetchNutritionSettings).mockResolvedValue(settings)
	})

	afterEach(() => {
		vi.useRealTimers()
		vi.resetAllMocks()
	})

	test('fills every field from a complete account', async () => {
		const { values } = await loadCalculatorPrefill(makeUser())

		expect(values).toEqual({ sex: 'male', age: 30, height: 180, weight: 80, goal: 'diet' })
	})

	// the labels are listed to the user in this order, as the fields appear in the form
	test('names the filled fields in the order of the form', async () => {
		const { labels } = await loadCalculatorPrefill(makeUser())

		expect(labels).toEqual(['Geschlecht', 'Alter', 'Größe', 'Gewicht', 'Ziel'])
	})

	// the weights come sorted by day from the oldest to the latest
	test('takes the latest weight entry', async () => {
		const { values } = await loadCalculatorPrefill(makeUser())

		expect(values.weight).toBe(80)
	})

	test('counts the age in full years before the birthday', async () => {
		const { values } = await loadCalculatorPrefill(makeUser({ birthDate: '1996-12-24' }))

		expect(values.age).toBe(29)
	})

	test.each<[string, Partial<PersonalProfile>, string, string]>([
		['the sex', { sex: null }, 'sex', 'Geschlecht'],
		['the birth date', { birthDate: null }, 'age', 'Alter'],
		['a valid birth date', { birthDate: 'not-a-date' }, 'age', 'Alter'],
		['the height', { heightCm: null }, 'height', 'Größe'],
	])('leaves a field empty without %s', async (_description, profile, field, label) => {
		const { values, labels } = await loadCalculatorPrefill(makeUser(profile))

		expect(values).not.toHaveProperty(field)
		expect(labels).not.toContain(label)
	})

	test('leaves the weight empty without weight entries', async () => {
		vi.mocked(fetchWeightEntries).mockResolvedValue([])

		const { values, labels } = await loadCalculatorPrefill(makeUser())

		expect(values).not.toHaveProperty('weight')
		expect(labels).not.toContain('Gewicht')
	})

	test.each<[string, NutritionSettings | null]>([
		['no nutrition settings', null],
		['settings without a goal', { ...settings, goal: null }],
	])('leaves the goal empty with %s', async (_description, nutritionSettings) => {
		vi.mocked(fetchNutritionSettings).mockResolvedValue(nutritionSettings)

		const { values, labels } = await loadCalculatorPrefill(makeUser())

		expect(values).not.toHaveProperty('goal')
		expect(labels).not.toContain('Ziel')
	})

	// the prefill is a convenience, a failed request must not keep the calculator from opening
	test('leaves the weight empty when its request fails', async () => {
		vi.mocked(fetchWeightEntries).mockRejectedValue(new Error('network'))

		const { values } = await loadCalculatorPrefill(makeUser())

		expect(values).toEqual({ sex: 'male', age: 30, height: 180, goal: 'diet' })
	})

	test('leaves the goal empty when its request fails', async () => {
		vi.mocked(fetchNutritionSettings).mockRejectedValue(new Error('network'))

		const { values } = await loadCalculatorPrefill(makeUser())

		expect(values).toEqual({ sex: 'male', age: 30, height: 180, weight: 80 })
	})

	test('returns nothing for an empty account when both requests fail', async () => {
		vi.mocked(fetchWeightEntries).mockRejectedValue(new Error('network'))
		vi.mocked(fetchNutritionSettings).mockRejectedValue(new Error('network'))

		const prefill = await loadCalculatorPrefill(
			makeUser({ birthDate: null, heightCm: null, sex: null }),
		)

		expect(prefill).toEqual({ values: {}, labels: [] })
	})
})

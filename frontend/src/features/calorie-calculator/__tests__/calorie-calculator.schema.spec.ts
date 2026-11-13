import type { CalorieCalculatorValues, Workout } from '../calorie-calculator.types'

import { describe, expect, test } from 'vitest'

import { calorieCalculatorZodSchema } from '../calorie-calculator.schema'

// A valid adult of normal weight: BMI 80 / 1.8² = 24.7. Override only what a test is about.
function makeValues(overrides: Partial<CalorieCalculatorValues> = {}): CalorieCalculatorValues {
	return {
		sex: 'male',
		age: 30,
		height: 180,
		weight: 80,
		steps: 5000,
		goal: 'maintain',
		exercises: [],
		...overrides,
	}
}

// The fields that have an issue, as dotted paths such as 'exercises.0.met'
function invalidFields(values: unknown): string[] {
	const result = calorieCalculatorZodSchema.safeParse(values)

	return result.success ? [] : result.error.issues.map((issue) => issue.path.join('.'))
}

function messagesFor(values: unknown, field: string): string[] {
	const result = calorieCalculatorZodSchema.safeParse(values)

	if (result.success) return []

	return result.error.issues
		.filter((issue) => issue.path.join('.') === field)
		.map((issue) => issue.message)
}

describe('validate the calorie calculator', () => {
	test('accepts complete, plausible details', () => {
		expect(invalidFields(makeValues())).toEqual([])
	})

	describe('check the plausible ranges', () => {
		test.each<[keyof CalorieCalculatorValues, number, number]>([
			['age', 16, 120],
			['height', 120, 250],
			['weight', 25, 400],
			['steps', 0, 50000],
		])('accepts %s from %i to %i', (field, min, max) => {
			expect(invalidFields(makeValues({ [field]: min }))).toEqual([])
			expect(invalidFields(makeValues({ [field]: max }))).toEqual([])
		})

		test.each<[keyof CalorieCalculatorValues, number, number]>([
			['age', 15, 121],
			['height', 119, 251],
			['weight', 24, 401],
			['steps', -1, 50001],
		])('rejects %s of %i and %i', (field, belowMin, aboveMax) => {
			expect(invalidFields(makeValues({ [field]: belowMin }))).toEqual([field])
			expect(invalidFields(makeValues({ [field]: aboveMax }))).toEqual([field])
		})

		test.each(['sex', 'age', 'height', 'weight', 'steps', 'goal'] as const)(
			'requires %s',
			(field) => {
				const values: Partial<CalorieCalculatorValues> = makeValues()
				delete values[field]

				expect(invalidFields(values)).toContain(field)
			},
		)
	})

	describe('refuse a deficit where it is a health risk', () => {
		test('for minors', () => {
			expect(messagesFor(makeValues({ age: 17, goal: 'diet' }), 'goal')).toEqual([
				expect.stringContaining('Unter 18'),
			])
		})

		test('not for adults', () => {
			expect(invalidFields(makeValues({ age: 18, goal: 'diet' }))).toEqual([])
		})

		// at 2 m, a BMI of 18.5 is exactly 74 kg
		test('below a BMI of 18.5', () => {
			expect(
				messagesFor(makeValues({ height: 200, weight: 73.9, goal: 'diet' }), 'goal'),
			).toEqual([expect.stringContaining('vom Abnehmen ab')])
		})

		test('not at a BMI of 18.5', () => {
			expect(invalidFields(makeValues({ height: 200, weight: 74, goal: 'diet' }))).toEqual([])
		})

		test.each(['maintain', 'gain'] as const)(
			'but allows %s for minors and underweight',
			(goal) => {
				expect(
					invalidFields(makeValues({ age: 16, height: 200, weight: 60, goal })),
				).toEqual([])
			},
		)

		// both apply, but one hint about the same field is enough, and the age is the stronger reason
		test('mention only the age for an underweight minor', () => {
			expect(
				messagesFor(makeValues({ age: 16, height: 200, weight: 60, goal: 'diet' }), 'goal'),
			).toEqual([expect.stringContaining('Unter 18')])
		})
	})

	describe('check the workouts', () => {
		const workout: Workout = { met: '0-0-8', duration: 60, frequency: 3 }

		const invalidWorkoutFields = (entry: Partial<Workout>): string[] =>
			invalidFields(makeValues({ exercises: [entry as Workout] }))

		test('accepts a complete workout', () => {
			expect(invalidWorkoutFields(workout)).toEqual([])
		})

		test('accepts an empty workout, training is optional', () => {
			expect(invalidWorkoutFields({ met: '', duration: 0, frequency: 0 })).toEqual([])
		})

		test('fills in an empty workout when fields are missing', () => {
			const result = calorieCalculatorZodSchema.parse(
				makeValues({ exercises: [{} as Workout] }),
			)

			expect(result.exercises).toEqual([{ met: '', duration: 0, frequency: 0 }])
		})

		// otherwise the workout would be skipped silently and the user would believe it counted
		test.each<[string, Partial<Workout>, string]>([
			['no activity, but a duration', { met: '', duration: 60, frequency: 0 }, 'met'],
			['no activity, but a frequency', { met: '', duration: 0, frequency: 3 }, 'met'],
			['an activity without duration', { ...workout, duration: 0 }, 'duration'],
			['an activity without frequency', { ...workout, frequency: 0 }, 'frequency'],
		])('rejects %s', (_description, entry, field) => {
			expect(invalidWorkoutFields(entry)).toEqual([`exercises.0.${field}`])
		})

		test('reports duration and frequency together when both are missing', () => {
			expect(invalidWorkoutFields({ ...workout, duration: 0, frequency: 0 })).toEqual([
				'exercises.0.duration',
				'exercises.0.frequency',
			])
		})

		test.each<[string, Partial<Workout>, string]>([
			['more than 5 hours per session', { ...workout, duration: 301 }, 'duration'],
			['more than 7 sessions per week', { ...workout, frequency: 8 }, 'frequency'],
		])('rejects %s', (_description, entry, field) => {
			expect(invalidWorkoutFields(entry)).toEqual([`exercises.0.${field}`])
		})

		// a typo such as 600 instead of 60 minutes must not inflate the target
		test('accepts up to 20 hours of training per week', () => {
			const exercises = [
				{ ...workout, duration: 300, frequency: 3 },
				{ ...workout, duration: 100, frequency: 3 },
			]

			expect(invalidFields(makeValues({ exercises }))).toEqual([])
		})

		test('rejects more than 20 hours of training per week', () => {
			const exercises = [
				{ ...workout, duration: 300, frequency: 3 },
				{ ...workout, duration: 101, frequency: 3 },
			]

			expect(invalidFields(makeValues({ exercises }))).toEqual(['exercises'])
		})
	})
})

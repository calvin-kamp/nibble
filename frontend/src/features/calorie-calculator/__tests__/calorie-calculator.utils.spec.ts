import type {
	CalorieCalculatorValues,
	CalorieResult,
	Goal,
	Macro,
	Workout,
} from '../calorie-calculator.types'

import { describe, expect, test } from 'vitest'

import { TRAINING_GROUPS } from '../calorie-calculator.constants'
import {
	calculateCalories,
	macroShares,
	macrosToKcal,
	resultToNeeds,
	splitKcal,
	TRAINING_SELECT_GROUPS,
	trainingLabel,
} from '../calorie-calculator.utils'

describe('convert macros to kcal', () => {
	test('converts grams to kcal at 4/4/9 kcal per gram', () => {
		// 10 g protein * 4 + 20 g carbs * 4 + 5 g fat * 9 = 165
		expect(macrosToKcal({ protein: 10, carbs: 20, fat: 5 })).toBe(165)
	})

	test('returns 0 without macros', () => {
		expect(macrosToKcal({ protein: 0, carbs: 0, fat: 0 })).toBe(0)
	})

	test('weights fat higher than protein and carbs', () => {
		// 1 g of fat has 9 kcal, 1 g of protein or carbs only 4 kcal
		expect(macrosToKcal({ protein: 0, carbs: 0, fat: 10 })).toBe(90)
		expect(macrosToKcal({ protein: 10, carbs: 0, fat: 0 })).toBe(40)
		expect(macrosToKcal({ protein: 0, carbs: 10, fat: 0 })).toBe(40)
	})

	test('handles decimal grams', () => {
		// 2.5 * 4 + 1.5 * 4 + 0.5 * 9 = 20.5
		expect(macrosToKcal({ protein: 2.5, carbs: 1.5, fat: 0.5 })).toBeCloseTo(20.5, 5)
	})
})

describe('look up the label of a training option', () => {
	test('returns the label for a valid value', () => {
		// the value is groupIndex-activityIndex, both counted from 0: '3-1' is the second activity
		// of the fourth group (Mobilität), '0-3' the fourth of the first (Krafttraining)
		expect(trainingLabel('0-3')).toBe('Zirkeltraining')
		expect(trainingLabel('1-13')).toBe('Seilspringen')
		expect(trainingLabel('2-12')).toBe('Tischtennis')
		expect(trainingLabel('3-1')).toBe('Pilates')
	})

	test('ignores the MET suffix of the form option value', () => {
		// the select options carry groupIndex-activityIndex-MET, only the first two parts count
		expect(trainingLabel('0-3-7')).toBe('Zirkeltraining')
		expect(trainingLabel('3-1-3')).toBe('Pilates')
	})

	// out of range, incomplete or malformed values must not throw, they just have no label
	test.each([
		['a group that does not exist', '10-3'],
		['an activity that does not exist', '1-100'],
		['a group without an activity', '0'],
		['text instead of numbers', 'wrong-input'],
		['an empty string (unfinished workout)', ''],
	])('returns undefined for %s', (_description, value) => {
		expect(trainingLabel(value)).toBeUndefined()
	})
})

describe('offer the training activities in the form', () => {
	// every option of the training select, with the group it belongs to
	const options = TRAINING_SELECT_GROUPS.flatMap((group) =>
		group.options.map((option) => ({ group: group.label, ...option })),
	)

	// One hour once a week at 70 kg, so a workout counts with (MET - 1) * 70 / 7 = (MET - 1) * 10 kcal
	function trainingConsumptionOf(met: string): number {
		const values: CalorieCalculatorValues = {
			sex: 'male',
			age: 30,
			height: 180,
			weight: 70,
			steps: 0,
			goal: 'maintain',
			exercises: [{ met, duration: 60, frequency: 1 }],
		}

		return calculateCalories(values).trainingConsumption
	}

	test('offers every activity of every group', () => {
		const activities = TRAINING_GROUPS.flatMap((group) => group.activities)

		expect(options).toHaveLength(activities.length)
	})

	test('gives every activity its own value', () => {
		const values = options.map((option) => option.value)

		expect(new Set(values).size).toBe(values.length)
	})

	// the value carries the indices and the MET, so a changed format would turn the label into
	// "Training" in the result and every workout into 0 kcal without any error
	describe.each(options)('$group: $label', ({ value, label }) => {
		test('finds its label again from its value', () => {
			expect(trainingLabel(value)).toBe(label)
		})

		test('is counted with its MET', () => {
			const [groupIndex, activityIndex] = value.split('-').map(Number)
			const met = TRAINING_GROUPS[groupIndex!]!.activities[activityIndex!]!.met

			expect(trainingConsumptionOf(value)).toBeCloseTo((met - 1) * 10, 5)
		})

		// one MET is rest, a lower value would make training burn less than sitting still
		test('burns more than rest', () => {
			expect(trainingConsumptionOf(value)).toBeGreaterThan(0)
		})
	})
})

describe('split kcal into protein, carbs and fat', () => {
	test('splits kcal into 30/40/30 shares of protein, carbs and fat', () => {
		// protein 2400 * 0.3 / 4 = 180 g, carbs 2400 * 0.4 / 4 = 240 g, fat 2400 * 0.3 / 9 = 80 g
		expect(splitKcal(2400)).toEqual({ carbs: 240, fat: 80, protein: 180 })
	})

	test('rounds to whole grams and gives the rounding remainder to carbs', () => {
		// fat: 2000 * 0.3 / 9 = 66.67 -> 67, carbs: (2000 - 150 * 4 - 67 * 9) / 4 = 199.25 -> 199
		expect(splitKcal(2000)).toEqual({ carbs: 199, fat: 67, protein: 150 })
	})

	// whole grams cannot match the total exactly, the promise is a deviation of at most 2 kcal
	test.each([1200, 1500, 1800, 2000, 2500, 3000])('adds up to %i kcal within 2 kcal', (kcal) => {
		expect(Math.abs(macrosToKcal(splitKcal(kcal)) - kcal)).toBeLessThanOrEqual(2)
	})

	// 0, 1 and 10 kcal are so small that every share rounds to 0 g, carbs must not turn negative
	test.each([0, 1, 10, 2000])('returns whole, non-negative grams for %i kcal', (kcal) => {
		const { protein, carbs, fat } = splitKcal(kcal)

		for (const grams of [protein, carbs, fat]) {
			expect(Number.isInteger(grams)).toBe(true)
			expect(grams).toBeGreaterThanOrEqual(0)
		}
	})

	test('returns 0g for 0 kcal', () => {
		expect(splitKcal(0)).toEqual({ carbs: 0, fat: 0, protein: 0 })
	})
})

describe('convert a calculator result into daily needs', () => {
	// resultToNeeds only reads targetCalories and macros, the other fields are filler for the type
	function makeResult(overrides: Partial<CalorieResult> = {}): CalorieResult {
		return {
			basalMetabolicRate: 0,
			stepsConsumption: 0,
			consumptionBeforeTef: 0,
			trainingConsumption: 0,
			maintenanceCalories: 0,
			targetCalories: 2000,
			safetyAdjustment: 0,
			macros: [],
			...overrides,
		}
	}

	// calories are rounded to 10, the middle (x5) goes up: 2005 -> 2010
	test.each([
		[1994, 1990],
		[1996, 2000],
		[2003, 2000],
		[2005, 2010],
	])('rounds %i target kcal to the nearest 10 (%i)', (targetCalories, expected) => {
		expect(resultToNeeds(makeResult({ targetCalories })).kcal).toBe(expected)
	})

	test('rounds the macros to whole grams and finds them by name', () => {
		// 66.7 -> 67, 149.6 -> 150, 200.4 -> 200; the order differs from the result on purpose
		const result = makeResult({
			macros: [
				{ name: 'Fett', amount: 66.7, kcal: 600 },
				{ name: 'Protein', amount: 149.6, kcal: 598 },
				{ name: 'Kohlenhydrate', amount: 200.4, kcal: 802 },
			],
		})

		expect(resultToNeeds(result)).toMatchObject({ protein: 150, carbs: 200, fat: 67 })
	})

	test('uses 0 g for macros that are missing', () => {
		const result = makeResult({ macros: [{ name: 'Protein', amount: 120, kcal: 480 }] })

		expect(resultToNeeds(result)).toMatchObject({ protein: 120, carbs: 0, fat: 0 })
		expect(resultToNeeds(makeResult({ macros: [] }))).toMatchObject({
			protein: 0,
			carbs: 0,
			fat: 0,
		})
	})

	test('marks the needs as calculated', () => {
		expect(resultToNeeds(makeResult()).source).toBe('calculated')
	})
})

describe('calculate the macro shares in percent', () => {
	test('returns 0 % for every macro without calories', () => {
		expect(macroShares({ protein: 0, carbs: 0, fat: 0 })).toEqual({
			protein: 0,
			carbs: 0,
			fat: 0,
		})
	})

	test('returns 0 % when the grams round down to nothing', () => {
		// the grams are rounded first, so 0.4 g counts as 0 g and the total stays 0 kcal
		expect(macroShares({ protein: 0.4, carbs: 0.4, fat: 0.4 })).toEqual({
			protein: 0,
			carbs: 0,
			fat: 0,
		})
	})

	test('calculates the shares of the calories', () => {
		// 40 g protein = 160 kcal, 120 g carbs = 480 kcal, 40 g fat = 360 kcal, total 1000 kcal
		expect(macroShares({ protein: 40, carbs: 120, fat: 40 })).toEqual({
			protein: 16,
			carbs: 48,
			fat: 36,
		})
	})

	// uneven splits, a single macro and equal grams: the rounded shares must still total 100
	test.each([
		[100, 100, 100],
		[33, 33, 33],
		[10, 10, 10],
		[1, 0, 0],
		[0, 0, 1],
		[150, 200, 67],
		[90, 210, 65],
	])(
		'adds up to 100 whole percent for %i g protein, %i g carbs, %i g fat',
		(protein, carbs, fat) => {
			const shares = macroShares({ protein, carbs, fat })

			expect(Number.isInteger(shares.protein)).toBe(true)
			expect(Number.isInteger(shares.carbs)).toBe(true)
			expect(Number.isInteger(shares.fat)).toBe(true)
			expect(shares.protein + shares.carbs + shares.fat).toBe(100)
		},
	)

	test('gives the leftover point to the largest rounding remainder', () => {
		// 90 g / 210 g / 65 g = 20.17 % / 47.06 % / 32.77 %: rounded down 20 + 47 + 32 = 99,
		// the missing point goes to fat (.77 is the largest remainder)
		expect(macroShares({ protein: 90, carbs: 210, fat: 65 })).toEqual({
			protein: 20,
			carbs: 47,
			fat: 33,
		})

		// 110 g / 210 g / 65 g = 23.59 % / 45.04 % / 31.37 %: rounded down 23 + 45 + 31 = 99,
		// here protein has the largest remainder (.59)
		expect(macroShares({ protein: 110, carbs: 210, fat: 65 })).toEqual({
			protein: 24,
			carbs: 45,
			fat: 31,
		})
	})
})

describe('calculate the daily calorie needs', () => {
	// Default case for calculateCalories: a sedentary man, basal metabolic rate by hand:
	// 10 * 80 + 6.25 * 180 - 5 * 30 + 5 = 1780. Override only what a test is about.
	function makeValues(overrides: Partial<CalorieCalculatorValues> = {}): CalorieCalculatorValues {
		return {
			sex: 'male',
			age: 30,
			height: 180,
			weight: 80,
			steps: 0,
			goal: 'maintain',
			exercises: [],
			...overrides,
		}
	}

	// The same man, but active: 6600 steps burn 200 kcal, one hour of MET 8 every day burns 560.
	// Together with the basal metabolic rate that is 1780 + 200 + 560 = 2540 kcal before the TEF.
	const activeValues = makeValues({
		steps: 6600,
		exercises: [{ met: '0-0-8', duration: 60, frequency: 7 }],
	})

	describe('calculate the basal metabolic rate', () => {
		test('is calculated from sex, age, weight and height', () => {
			// Mifflin-St Jeor: 10 * kg + 6.25 * cm - 5 * age, then + 5 for men and - 161 for women,
			// so the woman has 1780 - 166 = 1614 kcal
			expect(calculateCalories(makeValues()).basalMetabolicRate).toBe(1780)
			expect(calculateCalories(makeValues({ sex: 'female' })).basalMetabolicRate).toBe(1614)
		})

		// the coefficients of the formula: each input changes the result by a fixed amount
		test.each([
			['one more year of age', { age: 31 }, -5],
			['one more kg of weight', { weight: 81 }, 10],
			['one more cm of height', { height: 181 }, 6.25],
		])('changes by the right amount for %s', (_description, change, difference) => {
			const base = calculateCalories(makeValues()).basalMetabolicRate
			const changed = calculateCalories(makeValues(change)).basalMetabolicRate

			expect(changed - base).toBe(difference)
		})

		test('does not depend on steps, training or goal', () => {
			const values = makeValues({
				steps: 10000,
				goal: 'diet',
				exercises: [{ met: '0-3-7', duration: 60, frequency: 3 }],
			})

			expect(calculateCalories(values).basalMetabolicRate).toBe(1780)
		})
	})

	describe('calculate the calories burned by steps', () => {
		// walking is priced at MET 3.5 - 1 = 2.5 for 110 steps per minute
		test('is 0 without steps', () => {
			expect(calculateCalories(makeValues()).stepsConsumption).toBe(0)
		})
		test('is calculated from steps and weight', () => {
			// 2.5 * 80 * 5000 / (110 * 60) = 151.52, a value that does not come out even
			expect(calculateCalories(makeValues({ steps: 5000 })).stepsConsumption).toBeCloseTo(
				151.5,
				1,
			)
		})
		test('is exactly 200 kcal for 6600 steps at 80 kg', () => {
			// 6600 steps are exactly one hour of walking: 2.5 * 80 * 1 h = 200
			expect(calculateCalories(makeValues({ steps: 6600 })).stepsConsumption).toBe(200)
		})
	})

	describe('calculate the calories burned by training', () => {
		// MET 12, 60 minutes, 3 times a week, 80 kg: (12 - 1) * 80 * (60 / 60) * (3 / 7) = 377.14
		const workout: Workout = {
			met: '0-0-12',
			duration: 60,
			frequency: 3,
		}

		const consumptionOf = (exercises: Workout[]): number =>
			calculateCalories(makeValues({ exercises })).trainingConsumption

		test('is 0 without workouts', () => {
			expect(consumptionOf([])).toBe(0)
		})

		test('calculates the daily average of one workout', () => {
			expect(consumptionOf([workout])).toBeCloseTo(377.1429, 3)
		})

		test('subtracts the resting MET: one hour of MET 8 every day burns 7 * 80 kcal', () => {
			// (8 - 1) * 80 * (60 / 60) * (7 / 7) = 560
			expect(consumptionOf([{ met: '0-0-8', duration: 60, frequency: 7 }])).toBe(560)
		})

		test('adds up several workouts', () => {
			expect(consumptionOf([workout, workout])).toBeCloseTo(2 * consumptionOf([workout]), 5)
		})

		// training is optional, so a started but unfinished entry must neither count nor fail
		test.each([
			['a duration of 0', { ...workout, duration: 0 }],
			['a frequency of 0', { ...workout, frequency: 0 }],
			['no activity chosen', { ...workout, met: '' }],
			['a value without MET', { ...workout, met: '0-0' }],
			['a MET that is not a number', { ...workout, met: '0-0-abc' }],
		])('ignores a workout with %s', (_description, incomplete) => {
			expect(consumptionOf([incomplete])).toBe(0)
		})

		test('counts only the complete workouts when others are unfinished', () => {
			const incomplete = { ...workout, duration: 0 }

			expect(consumptionOf([workout, incomplete])).toBe(consumptionOf([workout]))
		})
	})

	describe('calculate the maintenance calories', () => {
		test('add the thermic effect of food to a sedentary day', () => {
			// 1780 / (1 - 0.1) = 1977.78
			expect(calculateCalories(makeValues()).maintenanceCalories).toBeCloseTo(1977.7778, 3)
		})

		test('add up basal metabolic rate, steps and training before the thermic effect', () => {
			// 2540 / (1 - 0.1) = 2822.22, not 2540 * 1.1 = 2794: the TEF is a share of the intake
			expect(calculateCalories(activeValues).maintenanceCalories).toBeCloseTo(2822.2222, 3)
		})
	})

	describe('calculate the target calories', () => {
		// maintenance of the sedentary man is 1977.78 kcal; * 0.85 = 1681.11, * 1.1 = 2175.56
		test.each<[string, Goal, number]>([
			['losing weight takes 85 % of maintenance', 'diet', 1681.11],
			['maintaining weight takes 100 % of maintenance', 'maintain', 1977.78],
			['gaining weight takes 110 % of maintenance', 'gain', 2175.56],
		])('when %s', (_description, goal, expected) => {
			expect(calculateCalories(makeValues({ goal })).targetCalories).toBeCloseTo(expected, 1)
		})

		test('are not changed when they are above the intake floor', () => {
			// the sedentary man on a diet gets 1681 kcal, above his floor of 1500 kcal
			const result = calculateCalories(makeValues({ goal: 'diet' }))

			expect(result.safetyAdjustment).toBe(0)
		})

		// a small, light person on a diet gets about 1030 kcal, far below both floors
		// (1300 kcal for women, 1500 kcal for men), so the floor applies
		test.each<[string, CalorieCalculatorValues['sex'], number]>([
			['a woman', 'female', 1300],
			['a man', 'male', 1500],
		])('are raised to the intake floor for %s', (_description, sex, floor) => {
			const result = calculateCalories(
				makeValues({ sex, age: 60, height: 150, weight: 45, goal: 'diet' }),
			)

			expect(result.targetCalories).toBe(floor)
			expect(result.safetyAdjustment).toBeGreaterThan(0)
		})
	})

	describe('calculate the macros', () => {
		// macros are found by their German name, as shown in the result
		const macroOf = (values: CalorieCalculatorValues, name: string): Macro => {
			const macro = calculateCalories(values).macros.find((entry) => entry.name === name)

			if (!macro) throw new Error(`macro ${name} is missing`)

			return macro
		}

		test('are calculated for a man of normal weight who maintains', () => {
			// reference weight 1.8 m * 1.8 m * BMI 25 = 81 kg, so all 80 kg count; target 1977.78
			// protein 1.6 g * 80 kg = 128 g, fat 25 % of 1977.78 kcal / 9 = 54.94 g,
			// carbs are the rest: (1977.78 - 128 * 4 - 494.44) / 4 = 242.83 g
			expect(macroOf(makeValues(), 'Protein').amount).toBeCloseTo(128, 2)
			expect(macroOf(makeValues(), 'Fett').amount).toBeCloseTo(54.94, 2)
			expect(macroOf(makeValues(), 'Kohlenhydrate').amount).toBeCloseTo(242.83, 2)
		})

		test('count only a share of the weight above the reference weight', () => {
			// 150 kg at 1.8 m: nutrient weight 81 + (150 - 81) * 0.25 = 98.25 kg, not 150 kg
			// protein 1.6 g * 98.25 kg = 157.2 g instead of 240 g
			expect(macroOf(makeValues({ weight: 150 }), 'Protein').amount).toBeCloseTo(157.2, 2)
		})

		test('cap protein at 35 % of the target calories', () => {
			// on a diet the man would get 2 g * 80 kg = 160 g, but 35 % of 1681.11 kcal is 147.1 g
			const result = calculateCalories(makeValues({ goal: 'diet' }))
			const protein = macroOf(makeValues({ goal: 'diet' }), 'Protein')

			expect(protein.kcal).toBeCloseTo(result.targetCalories * 0.35, 2)
		})

		test('give more protein per kg when gaining weight', () => {
			// 1.8 g * 80 kg = 144 g, below the ceiling of 35 % of 2175.56 kcal / 4 = 190.4 g
			expect(macroOf(makeValues({ goal: 'gain' }), 'Protein').amount).toBeCloseTo(144, 2)
		})

		describe('size fat by body weight on a diet', () => {
			test('with 0.8 g per kg for a man', () => {
				// 0.8 g * 80 kg = 64 g, below the ceiling of 35 % of 1681.11 kcal / 9 = 65.4 g
				expect(macroOf(makeValues({ goal: 'diet' }), 'Fett').amount).toBeCloseTo(64, 2)
			})

			test('with 1 g per kg for a woman', () => {
				// basal rate 600 + 1031.25 - 150 - 161 = 1320.25, training 7 * 60 = 420,
				// target 1740.25 / 0.9 * 0.85 = 1643.57; 1 g * 60 kg = 60 g, below the ceiling of 63.9 g
				const values = makeValues({
					sex: 'female',
					height: 165,
					weight: 60,
					goal: 'diet',
					exercises: [{ met: '0-0-8', duration: 60, frequency: 7 }],
				})

				expect(macroOf(values, 'Fett').amount).toBeCloseTo(60, 2)
			})
		})

		describe('size fat by a share of the target calories outside a diet', () => {
			test('with 25 % for a man', () => {
				// 25 % of 1977.78 kcal / 9 = 54.94 g
				expect(macroOf(makeValues(), 'Fett').kcal).toBeCloseTo(1977.7778 * 0.25, 2)
			})

			test('with 30 % for a woman', () => {
				// basal rate 800 + 1125 - 150 - 161 = 1614, target 1614 / 0.9 = 1793.33
				const result = calculateCalories(makeValues({ sex: 'female' }))
				const fat = macroOf(makeValues({ sex: 'female' }), 'Fett')

				expect(fat.kcal).toBeCloseTo(result.targetCalories * 0.3, 2)
			})
		})

		test('raise fat to 0.6 g per kg when the share of the target is lower', () => {
			// only reachable with a tall, old woman: reference weight 2.1 m * 2.1 m * 25 = 110.25 kg,
			// so all 110 kg count; target (1100 + 1312.5 - 500 - 161) / 0.9 = 1946.11 kcal,
			// 30 % of that is 64.87 g, the floor 0.6 g * 110 kg = 66 g
			const values = makeValues({ sex: 'female', age: 100, height: 210, weight: 110 })

			expect(macroOf(values, 'Fett').amount).toBeCloseTo(66, 2)
		})

		test('cap fat at 35 % of the target calories', () => {
			// a woman with 80 kg on a diet would get 1 g * 80 kg = 80 g, but 35 % of 1524.33 kcal
			// (basal rate 1614 / 0.9 * 0.85) is 59.28 g
			const values = makeValues({ sex: 'female', goal: 'diet' })
			const result = calculateCalories(values)

			expect(macroOf(values, 'Fett').kcal).toBeCloseTo(result.targetCalories * 0.35, 2)
		})

		// resultToNeeds finds the macros by these names, a renamed macro would turn into 0 g there
		test('are named Fett, Protein and Kohlenhydrate, in this order', () => {
			const names = calculateCalories(makeValues()).macros.map((macro) => macro.name)

			expect(names).toEqual(['Fett', 'Protein', 'Kohlenhydrate'])
		})

		// properties that must hold for every person, whatever the details of the formula are
		describe.each<[string, CalorieCalculatorValues]>([
			['a sedentary man', makeValues()],
			['an active man', activeValues],
			['a man who gains weight', makeValues({ goal: 'gain' })],
			['a heavy man', makeValues({ weight: 150 })],
			['a tall woman on a diet', makeValues({ sex: 'female', weight: 80, goal: 'diet' })],
			[
				'a small woman on a diet',
				makeValues({ sex: 'female', age: 60, height: 150, weight: 45, goal: 'diet' }),
			],
		])('for %s', (_description, values) => {
			test('add up to the target calories', () => {
				const result = calculateCalories(values)
				const total = result.macros.reduce((sum, macro) => sum + macro.kcal, 0)

				expect(total).toBeCloseTo(result.targetCalories, 5)
			})

			test('are never negative', () => {
				for (const macro of calculateCalories(values).macros) {
					expect(macro.amount).toBeGreaterThanOrEqual(0)
				}
			})
		})
	})
})

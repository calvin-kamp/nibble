import type {
	DayOverview,
	FoodEntry,
	FoodProduct,
	WeightEntry,
	WeightPeriod,
} from '../tracking.types'

import { describe, expect, test } from 'vitest'

import {
	averageKcal,
	buildWeightPoints,
	formatAmount,
	formatCalendarWeekTitle,
	formatKgChange,
	formatMacrosShort,
	formatPeriodChange,
	formatQuantity,
	formatUnitOption,
	formatWeeklyBalance,
	getNiceTicks,
	getPeriodChange,
	getWeeklyBalance,
	isBarcode,
	kcalFromMacros,
	minimumKcal,
	normalizeBarcode,
	nutritionFor,
	rangeStartOf,
	summarizeDay,
	toQuantity,
	toTime,
	unitsOf,
	weekSlug,
	weekStart,
	weekStartFromSlug,
} from '../tracking.utils'

const DAY_MS = 24 * 60 * 60 * 1000

// Dates below are around Thursday, 12 November 2026; its week starts on Monday, 9 November.

// 100 g have 200 kcal, 10 g protein, 30 g carbs and 5 g fat; a serving is 40 g, a package 500 g
const product: FoodProduct = {
	code: '4000000000000',
	name: 'Haferflocken',
	unit: 'g',
	per100: { kcal: 200, protein: 10, carbs: 30, fat: 5 },
	serving: 40,
	packageSize: 500,
}

const NBSP = ' '

describe('summarize a day of the diary', () => {
	function entry(overrides: Partial<FoodEntry>): FoodEntry {
		return {
			id: '1',
			source: 'off',
			date: '2026-11-12',
			meal: 'breakfast',
			name: 'Haferflocken',
			kcal: 300,
			protein: 15,
			carbs: 45,
			fat: 7.5,
			...overrides,
		}
	}

	const entries: FoodEntry[] = [
		entry({
			id: '1',
			meal: 'dinner',
			name: 'Nudeln',
			kcal: 500,
			protein: 20,
			carbs: 90,
			fat: 5,
		}),
		entry({ id: '2', meal: 'breakfast' }),
		entry({
			id: '3',
			meal: 'breakfast',
			name: 'Honig',
			kcal: 60,
			protein: 0,
			carbs: 16,
			fat: 0,
		}),
		// the day before, must not count
		entry({ id: '4', date: '2026-11-11', kcal: 1000 }),
	]

	test('adds up the values of the day only', () => {
		const { kcal, protein, carbs, fat } = summarizeDay(entries, '2026-11-12')

		expect({ kcal, protein, carbs, fat }).toEqual({
			kcal: 860,
			protein: 35,
			carbs: 151,
			fat: 12.5,
		})
	})

	test('lists the meals in the order of the day, not of the entries', () => {
		const { meals } = summarizeDay(entries, '2026-11-12')

		expect(meals.map((meal) => meal.meal)).toEqual(['breakfast', 'dinner'])
	})

	test('leaves out the meals without entries', () => {
		const { meals } = summarizeDay(entries, '2026-11-12')

		expect(meals.map((meal) => meal.label)).toEqual(['Frühstück', 'Abendessen'])
	})

	test('adds up the kcal and lists the names of each meal', () => {
		const [breakfast] = summarizeDay(entries, '2026-11-12').meals

		expect(breakfast).toEqual({
			meal: 'breakfast',
			label: 'Frühstück',
			kcal: 360,
			items: ['Haferflocken', 'Honig'],
		})
	})

	test('names a food eaten twice only once', () => {
		const twice = [entry({ id: '1' }), entry({ id: '2' })]

		expect(summarizeDay(twice, '2026-11-12').meals[0]?.items).toEqual(['Haferflocken'])
	})

	test('returns 0 and no meals for a day without entries', () => {
		expect(summarizeDay(entries, '2026-11-13')).toEqual({
			kcal: 0,
			protein: 0,
			carbs: 0,
			fat: 0,
			meals: [],
		})
	})
})

describe('average the calories of a week', () => {
	function day(kcal: number, entryCount: number): DayOverview {
		return { date: '2026-11-12', kcal, protein: 0, carbs: 0, fat: 0, entryCount }
	}

	// a day without entries is a day not tracked, not a day without food
	test('counts only the days with entries', () => {
		expect(averageKcal([day(2000, 3), day(0, 0), day(1600, 2)])).toBe(1800)
	})

	test('returns null without days with entries', () => {
		expect(averageKcal([day(0, 0), day(0, 0)])).toBeNull()
	})

	test('returns null without days', () => {
		expect(averageKcal([])).toBeNull()
	})
})

describe('format the macros short', () => {
	test('names protein, carbs and fat in whole grams', () => {
		expect(formatMacrosShort({ protein: 15.4, carbs: 45.5, fat: 7.5 })).toBe(
			`P${NBSP}15${NBSP}g, K${NBSP}46${NBSP}g, F${NBSP}8${NBSP}g`,
		)
	})

	// a line may break between the macros, never inside one
	test('keeps letter, number and unit of a macro together', () => {
		expect(formatMacrosShort({ protein: 1, carbs: 2, fat: 3 })).not.toMatch(/[PKF] /)
	})

	test('uses the given separator', () => {
		expect(formatMacrosShort({ protein: 1, carbs: 2, fat: 3 }, ' · ')).toBe(
			`P${NBSP}1${NBSP}g · K${NBSP}2${NBSP}g · F${NBSP}3${NBSP}g`,
		)
	})
})

describe('format an amount', () => {
	test.each([
		[150, '150'],
		[1.26, '1,3'],
		[0.5, '0,5'],
		[2500, '2.500'],
	])('formats %d as %s', (value, expected) => {
		expect(formatAmount(value)).toBe(expected)
	})
})

describe('name the units of a product in the select', () => {
	test.each([
		['g', 'Gramm'],
		['ml', 'Milliliter'],
		['serving', 'Portion (40 g)'],
		['package', 'Packung (500 g)'],
	] as const)('names %s as %s', (unit, expected) => {
		expect(formatUnitOption(product, unit)).toBe(expected)
	})

	test('uses millilitres for a drink', () => {
		expect(formatUnitOption({ ...product, unit: 'ml', serving: 330 }, 'serving')).toBe(
			'Portion (330 ml)',
		)
	})
})

describe('format a logged amount', () => {
	test('shows grams alone', () => {
		expect(formatQuantity({ value: 150, unit: 'g', base: 150, baseUnit: 'g' })).toBe('150 g')
	})

	test('shows millilitres alone', () => {
		expect(formatQuantity({ value: 330, unit: 'ml', base: 330, baseUnit: 'ml' })).toBe('330 ml')
	})

	test.each([
		[{ value: 1, unit: 'serving', base: 40 }, '1 Portion (40 g)'],
		[{ value: 2, unit: 'serving', base: 80 }, '2 Portionen (80 g)'],
		[{ value: 0.5, unit: 'serving', base: 20 }, '0,5 Portionen (20 g)'],
		[{ value: 1, unit: 'package', base: 500 }, '1 Packung (500 g)'],
		[{ value: 2, unit: 'package', base: 1000 }, '2 Packungen (1.000 g)'],
	] as const)('shows servings and packages with their grams: %o', (quantity, expected) => {
		expect(formatQuantity({ ...quantity, baseUnit: 'g' })).toBe(expected)
	})
})

describe('find the Monday of a week', () => {
	test.each([
		['a Monday', '2026-11-09'],
		['a Thursday', '2026-11-12'],
		['a Sunday', '2026-11-15'],
	])('returns the same Monday for %s', (_description, date) => {
		expect(weekStart(date)).toBe('2026-11-09')
	})

	test('goes back into the month before', () => {
		expect(weekStart('2026-10-01')).toBe('2026-09-28')
	})

	test('goes back into the year before', () => {
		expect(weekStart('2026-01-01')).toBe('2025-12-29')
	})
})

describe('name a week in the address', () => {
	test('uses year and calendar week', () => {
		expect(weekSlug('2026-11-09')).toBe('2026-kw-46')
	})

	// the calendar week belongs to the year of its Thursday, not of its Monday
	test('names a week that starts in December after the next year', () => {
		expect(weekSlug('2025-12-29')).toBe('2026-kw-1')
	})
})

describe('find the week of an address', () => {
	test('returns the Monday of the week', () => {
		expect(weekStartFromSlug('2026-kw-46')).toBe('2026-11-09')
	})

	test('finds week 1 even when it starts in the year before', () => {
		expect(weekStartFromSlug('2026-kw-1')).toBe('2025-12-29')
	})

	test('reverses weekSlug for every week of a year', () => {
		const mondays = Array.from({ length: 53 }, (_, index) =>
			new Date(Date.UTC(2025, 11, 29 + index * 7)).toISOString().slice(0, 10),
		)

		for (const monday of mondays) {
			expect(weekStartFromSlug(weekSlug(monday))).toBe(monday)
		}
	})

	// 2026 starts on a Thursday and has 53 weeks, 2025 only 52
	test('accepts week 53 only in a year that has it', () => {
		expect(weekStartFromSlug('2026-kw-53')).toBe('2026-12-28')
		expect(weekStartFromSlug('2025-kw-53')).toBeNull()
	})

	test.each([
		['week 0', '2026-kw-0'],
		['week 54', '2026-kw-54'],
		['a leading zero', '2026-kw-01'],
		['no year', 'kw-46'],
		['no "kw"', '2026-46'],
		['a date', '2026-11-09'],
		['an empty string', ''],
	])('returns null for %s', (_description, slug) => {
		expect(weekStartFromSlug(slug)).toBeNull()
	})
})

describe('title a calendar week', () => {
	const today = '2026-11-12'

	test('calls the current week "Diese Woche"', () => {
		expect(formatCalendarWeekTitle('2026-11-09', today)).toBe('Diese Woche')
	})

	test('calls the week before "Letzte Woche"', () => {
		expect(formatCalendarWeekTitle('2026-11-02', today)).toBe('Letzte Woche')
	})

	test('names older weeks of this year by their number', () => {
		expect(formatCalendarWeekTitle('2026-10-26', today)).toBe('KW 44')
	})

	test('adds the year to weeks of another year', () => {
		expect(formatCalendarWeekTitle('2025-11-10', today)).toBe('KW 46 2025')
	})

	// the week of 29 December 2025 is week 1 of 2026, so it needs no year in 2026
	test('takes the year of the calendar week, not of its Monday', () => {
		expect(formatCalendarWeekTitle('2025-12-29', today)).toBe('KW 1')
	})
})

describe('recognize a barcode in the search', () => {
	test('removes spaces and hyphens', () => {
		expect(normalizeBarcode(' 4 000-417 025 005 ')).toBe('4000417025005')
	})

	test.each([
		['an EAN-8 with 8 digits', '12345678'],
		['an EAN-13 with 13 digits', '4000417025005'],
		['a GTIN-14 with 14 digits', '12345678901234'],
		['digits with spaces', '4 000417 025005'],
	])('accepts %s', (_description, query) => {
		expect(isBarcode(query)).toBe(true)
	})

	test.each([
		['7 digits', '1234567'],
		['15 digits', '123456789012345'],
		['a name', 'Haferflocken'],
		['digits with letters', '4000417A25005'],
		['an empty search', ''],
	])('rejects %s', (_description, query) => {
		expect(isBarcode(query)).toBe(false)
	})
})

describe('offer the units of a product', () => {
	test('offers grams, servings and packages when they are known', () => {
		expect(unitsOf(product)).toEqual(['g', 'serving', 'package'])
	})

	test('offers only the base unit without serving and package', () => {
		const { serving: _serving, packageSize: _packageSize, ...plain } = product

		expect(unitsOf({ ...plain, unit: 'ml' })).toEqual(['ml'])
	})
})

describe('convert an amount into grams', () => {
	test('keeps grams as they are', () => {
		expect(toQuantity(product, 150, 'g')).toEqual({
			value: 150,
			unit: 'g',
			base: 150,
			baseUnit: 'g',
		})
	})

	test('multiplies servings with the serving size', () => {
		expect(toQuantity(product, 1.5, 'serving').base).toBe(60)
	})

	test('multiplies packages with the package size', () => {
		expect(toQuantity(product, 2, 'package').base).toBe(1000)
	})

	test('rounds the grams to one decimal place', () => {
		// a third of a serving of 40 g is 13.333 g
		expect(toQuantity(product, 1 / 3, 'serving').base).toBe(13.3)
	})
})

describe('calculate the nutrition of an amount', () => {
	test('scales the values per 100 g to the amount', () => {
		expect(nutritionFor(product, 150)).toEqual({ kcal: 300, protein: 15, carbs: 45, fat: 7.5 })
	})

	test('rounds kcal to whole numbers and macros to one decimal place', () => {
		// 33 g: 66 kcal, 3.3 g protein, 9.9 g carbs, 1.65 g fat
		expect(nutritionFor(product, 33)).toEqual({ kcal: 66, protein: 3.3, carbs: 9.9, fat: 1.7 })
	})

	test('returns 0 for 0 g', () => {
		expect(nutritionFor(product, 0)).toEqual({ kcal: 0, protein: 0, carbs: 0, fat: 0 })
	})
})

describe('calculate the energy of the macros', () => {
	test('counts 4 kcal per gram of protein and carbs, 9 per gram of fat', () => {
		// 10 * 4 + 20 * 4 + 5 * 9 = 165
		expect(kcalFromMacros({ protein: 10, carbs: 20, fat: 5 })).toBe(165)
	})

	test('rounds to whole kcal', () => {
		// 1.1 * 4 = 4.4
		expect(kcalFromMacros({ protein: 1.1, carbs: 0, fat: 0 })).toBe(4)
	})

	// labels round and fiber adds energy, so only clearly too few kcal count as a typo
	test('allows 20 % and 10 kcal fewer than the macros give', () => {
		// 165 * 0.8 - 10 = 122
		expect(minimumKcal({ protein: 10, carbs: 20, fat: 5 })).toBe(122)
	})
})

describe('turn a date into a time', () => {
	test('counts the date from midnight UTC', () => {
		expect(toTime('2026-11-12')).toBe(Date.UTC(2026, 10, 12))
	})

	// summer time ends on 25 October 2026, a local day there has 25 hours
	test('keeps exactly one day between two dates around a change of summer time', () => {
		expect(toTime('2026-10-26') - toTime('2026-10-25')).toBe(DAY_MS)
	})
})

describe('track the weight', () => {
	function weight(date: string, kg: number): WeightEntry {
		return { id: date, date, kg }
	}

	// two weeks with two entries each, the newest one on 10 November
	const entries: WeightEntry[] = [
		weight('2026-11-10', 79),
		weight('2026-11-01', 82),
		weight('2026-11-08', 80),
		weight('2026-11-03', 81),
	]

	describe('find the start of a range', () => {
		test('counts the days back from the newest entry, including it', () => {
			// 7 days up to 10 November start on 4 November
			expect(rangeStartOf(entries, 7)).toBe(toTime('2026-11-04'))
		})

		test('has no start for the whole history', () => {
			expect(rangeStartOf(entries, Infinity)).toBe(-Infinity)
		})

		test('has no start without entries', () => {
			expect(rangeStartOf([], 7)).toBe(-Infinity)
		})
	})

	describe('build the points of the curve', () => {
		test('sorts the entries by date', () => {
			const dates = buildWeightPoints(entries).map((point) => point.date)

			expect(dates).toEqual(['2026-11-01', '2026-11-03', '2026-11-08', '2026-11-10'])
		})

		test('averages the 7 days up to and including each entry', () => {
			const averages = buildWeightPoints(entries).map((point) => point.weeklyAverage)

			// 1 Nov: 82; 3 Nov: 82 and 81; 8 Nov: 81 and 80 (1 Nov is 7 days before, it is out);
			// 10 Nov: 80 and 79
			expect(averages).toEqual([82, 81.5, 80.5, 79.5])
		})

		test('leaves out the entries before the range', () => {
			const dates = buildWeightPoints(entries, toTime('2026-11-04')).map(
				(point) => point.date,
			)

			expect(dates).toEqual(['2026-11-08', '2026-11-10'])
		})

		// otherwise the curve would start pulled by a weight that cannot be seen
		test('averages only the entries within the range', () => {
			const [first] = buildWeightPoints(entries, toTime('2026-11-02'))

			expect(first?.date).toBe('2026-11-03')
			expect(first?.weeklyAverage).toBe(81)
		})

		test('returns no points without entries', () => {
			expect(buildWeightPoints([])).toEqual([])
		})
	})

	describe('compare the last 7 days with the 7 days before', () => {
		test('compares the averages of both weeks', () => {
			// last 7 days: 80 and 79, the 7 days before: 82 and 81
			expect(getWeeklyBalance(buildWeightPoints(entries))).toEqual({
				average: 79.5,
				previousAverage: 81.5,
				balance: -2,
			})
		})

		test('has no balance without entries in the 7 days before', () => {
			const points = buildWeightPoints([weight('2026-11-08', 80), weight('2026-11-10', 79)])

			expect(getWeeklyBalance(points)).toEqual({
				average: 79.5,
				previousAverage: null,
				balance: null,
			})
		})

		test('returns null without entries', () => {
			expect(getWeeklyBalance([])).toBeNull()
		})
	})

	describe('calculate the change in a period', () => {
		const points = buildWeightPoints(entries)

		test('subtracts the first from the last entry of the period', () => {
			// within 7 days up to 10 November: 80 on 8 November, 79 on 10 November
			expect(getPeriodChange(points, 7)).toBe(-1)
		})

		test('covers the whole history', () => {
			expect(getPeriodChange(points, Infinity)).toBe(-3)
		})

		test('returns null with a single entry in the period', () => {
			expect(getPeriodChange(points, 1)).toBeNull()
		})

		test('returns null without entries', () => {
			expect(getPeriodChange([], 7)).toBeNull()
		})
	})
})

describe('find the ticks of the weight axis', () => {
	test('returns no ticks without values', () => {
		expect(getNiceTicks([])).toEqual([])
	})

	test('picks a step that covers the values with at most 4 ticks', () => {
		expect(getNiceTicks([80, 82])).toEqual([80, 81, 82])
	})

	test('picks a larger step for a larger span', () => {
		expect(getNiceTicks([60, 100])).toEqual([60, 80, 100])
	})

	test('picks a smaller step when more ticks are allowed', () => {
		expect(getNiceTicks([80, 82], 6)).toEqual([80, 80.5, 81, 81.5, 82])
	})

	// otherwise the axis would be 120,0 to 120,1 with the point on the bottom line
	test('spans at least 1 kg around a single weight and keeps it in the middle', () => {
		expect(getNiceTicks([120])).toEqual([119.5, 120, 120.5])
	})

	test('covers all values', () => {
		const values = [78.3, 81.7, 79.9]
		const ticks = getNiceTicks(values)

		expect(ticks[0]).toBeLessThanOrEqual(Math.min(...values))
		expect(ticks.at(-1)).toBeGreaterThanOrEqual(Math.max(...values))
	})
})

describe('format the weekly balance', () => {
	test.each([
		[-2, 'Minus 2,0 kg zu den 7 Tagen davor'],
		[0.35, 'Plus 0,4 kg zu den 7 Tagen davor'],
		[1.5, 'Plus 1,5 kg zu den 7 Tagen davor'],
	])('formats %d kg as "%s"', (balance, expected) => {
		expect(formatWeeklyBalance(balance)).toBe(expected)
	})

	// a change that is shown as 0,0 kg is no change for the user
	test.each([0, 0.04, -0.04])('calls %d kg unchanged', (balance) => {
		expect(formatWeeklyBalance(balance)).toBe('Unverändert zu den 7 Tagen davor')
	})
})

describe('format a weight change', () => {
	test.each([
		[1.5, '+1,5 kg'],
		[-1.5, '−1,5 kg'],
		[0, '0,0 kg'],
		[0.04, '0,0 kg'],
		[2, '+2,0 kg'],
	])('formats %d as %s', (change, expected) => {
		expect(formatKgChange(change)).toBe(expected)
	})

	// a typographic minus, not a hyphen
	test('uses a real minus sign', () => {
		expect(formatKgChange(-1)).toBe('−1,0 kg')
	})
})

describe('format the change in a period', () => {
	const period: WeightPeriod = {
		value: '7',
		days: 7,
		label: 'Letzte 7 Tage',
		phrase: 'in den letzten 7 Tagen',
	}

	test('names the change and the period', () => {
		expect(formatPeriodChange(-1, period)).toBe('−1,0 kg in den letzten 7 Tagen')
	})

	test('calls a change below 0,05 kg unchanged', () => {
		expect(formatPeriodChange(0.04, period)).toBe('Unverändert in den letzten 7 Tagen')
	})
})

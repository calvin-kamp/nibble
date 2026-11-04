import type {
	DayOverview,
	DaySummary,
	FoodEntry,
	FoodProduct,
	FoodQuantity,
	FoodUnit,
	Nutrition,
	WeeklyBalance,
	WeightEntry,
	WeightPeriod,
	WeightPoint,
} from '@features/tracking/tracking.types'

import { MEAL_LABELS, MEAL_ORDER } from '@features/tracking/tracking.constants'
import { addDays, calendarWeek, parseIsoDate, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

function sum(entries: FoodEntry[], key: 'kcal' | 'protein' | 'carbs' | 'fat'): number {
	return entries.reduce((total, entry) => total + entry[key], 0)
}

export function summarizeDay(entries: FoodEntry[], date: string): DaySummary {
	const dayEntries = entries.filter((entry) => entry.date === date)

	const meals = MEAL_ORDER.map((meal) => ({
		meal,
		mealEntries: dayEntries.filter((entry) => entry.meal === meal),
	}))
		.filter(({ mealEntries }) => mealEntries.length > 0)
		.map(({ meal, mealEntries }) => ({
			meal,
			label: MEAL_LABELS[meal],
			kcal: sum(mealEntries, 'kcal'),
			items: [...new Set(mealEntries.map((entry) => entry.name))],
		}))

	return {
		kcal: sum(dayEntries, 'kcal'),
		protein: sum(dayEntries, 'protein'),
		carbs: sum(dayEntries, 'carbs'),
		fat: sum(dayEntries, 'fat'),
		meals,
	}
}

/** Average calories over the days with entries, null without such days */
export function averageKcal(days: DayOverview[]): number | null {
	const tracked = days.filter((day) => day.entryCount > 0)

	if (!tracked.length) return null

	return tracked.reduce((total, day) => total + day.kcal, 0) / tracked.length
}

export function formatMacrosShort(
	macros: Pick<FoodEntry, 'protein' | 'carbs' | 'fat'>,
	separator = ', ',
): string {
	// Non-breaking spaces: a line may break between the macros, never inside one
	const part = (letter: string, grams: number) => `${letter}\u00a0${Math.round(grams)}\u00a0g`

	return [part('P', macros.protein), part('K', macros.carbs), part('F', macros.fat)].join(
		separator,
	)
}

export function formatAmount(value: number): string {
	return value.toLocaleString('de-DE', { maximumFractionDigits: 1 })
}

const COUNTED_UNITS = {
	serving: ['Portion', 'Portionen'],
	package: ['Packung', 'Packungen'],
} as const

export function formatUnitOption(product: FoodProduct, unit: FoodUnit): string {
	if (unit === 'serving') return `Portion (${formatNumber(product.serving!)} ${product.unit})`
	if (unit === 'package') return `Packung (${formatNumber(product.packageSize!)} ${product.unit})`

	return unit === 'g' ? 'Gramm' : 'Milliliter'
}

export function formatQuantity(quantity: FoodQuantity): string {
	const base = `${formatAmount(quantity.base)} ${quantity.baseUnit}`

	if (quantity.unit === 'g' || quantity.unit === 'ml') return base

	const [one, many] = COUNTED_UNITS[quantity.unit]

	return `${formatAmount(quantity.value)} ${quantity.value === 1 ? one : many} (${base})`
}

export function weekStart(iso: string): string {
	const weekday = ((parseIsoDate(iso)?.getDay() ?? 1) + 6) % 7

	return addDays(iso, -weekday)
}

/** Path segment of a week page, e.g. "2026-kw-1" for the week starting 29 December 2025 */
export function weekSlug(start: string): string {
	const { week, year } = calendarWeek(start)

	return `${year}-kw-${week}`
}

/** Monday of the week named by weekSlug, null for a week that does not exist */
export function weekStartFromSlug(slug: string): string | null {
	const match = /^(\d{4})-kw-(\d{1,2})$/.exec(slug)

	if (!match) return null

	// 4 January always lies in calendar week 1
	const start = addDays(weekStart(`${match[1]}-01-04`), (Number(match[2]) - 1) * 7)

	return weekSlug(start) === slug ? start : null
}

export function formatCalendarWeekTitle(start: string, today: string = toIsoDate()): string {
	const thisWeek = weekStart(today)

	if (start === thisWeek) return 'Diese Woche'
	if (start === addDays(thisWeek, -7)) return 'Letzte Woche'

	const { week, year } = calendarWeek(start)

	return year === calendarWeek(today).year ? `KW ${week}` : `KW ${week} ${year}`
}

export function normalizeBarcode(query: string): string {
	return query.replace(/[\s-]/g, '')
}

/** Barcodes are EAN-8 to GTIN-14, i.e. 8 to 14 digits, often with spaces in between */
export function isBarcode(query: string): boolean {
	return /^\d{8,14}$/.test(normalizeBarcode(query))
}

export function unitsOf(product: FoodProduct): FoodUnit[] {
	return [
		product.unit,
		...(product.serving ? (['serving'] as const) : []),
		...(product.packageSize ? (['package'] as const) : []),
	]
}

export function toQuantity(product: FoodProduct, value: number, unit: FoodUnit): FoodQuantity {
	const factor =
		unit === 'serving' ? product.serving! : unit === 'package' ? product.packageSize! : 1

	return { value, unit, base: Math.round(value * factor * 10) / 10, baseUnit: product.unit }
}

/** Nutrition values for an amount in g or ml, rounded to one decimal place, kcal to whole numbers */
export function nutritionFor(product: FoodProduct, base: number): Nutrition {
	const scale = (value: number) => Math.round(((value * base) / 100) * 10) / 10

	return {
		kcal: Math.round((product.per100.kcal * base) / 100),
		protein: scale(product.per100.protein),
		carbs: scale(product.per100.carbs),
		fat: scale(product.per100.fat),
	}
}

const DAY_MS = 24 * 60 * 60 * 1000
const WEEK_MS = 7 * DAY_MS

export function toTime(date: string): number {
	return Date.parse(`${date}T00:00:00Z`)
}

function average(values: number[]): number {
	return values.reduce((total, value) => total + value, 0) / values.length
}

function inWeekEndingAt<T extends { time: number }>(points: T[], endTime: number): T[] {
	return points.filter((point) => point.time > endTime - WEEK_MS && point.time <= endTime)
}

export function buildWeightPoints(entries: WeightEntry[]): WeightPoint[] {
	const sorted = entries
		.map((entry) => ({
			id: entry.id,
			date: entry.date,
			kg: entry.kg,
			time: toTime(entry.date),
		}))
		.toSorted((a, b) => a.time - b.time)

	return sorted.map((point) =>
		Object.assign(point, {
			weeklyAverage: average(inWeekEndingAt(sorted, point.time).map((entry) => entry.kg)),
		}),
	)
}

export function limitToDays(points: WeightPoint[], days: number): WeightPoint[] {
	const last = points[points.length - 1]

	if (!last) return []

	return points.filter((point) => point.time > last.time - days * DAY_MS)
}

export function getWeeklyBalance(points: WeightPoint[]): WeeklyBalance | null {
	const last = points[points.length - 1]

	if (!last) return null

	const currentWeek = inWeekEndingAt(points, last.time)
	const previousWeek = inWeekEndingAt(points, last.time - WEEK_MS)

	const currentAverage = average(currentWeek.map((point) => point.kg))
	const previousAverage = previousWeek.length
		? average(previousWeek.map((point) => point.kg))
		: null

	return {
		average: currentAverage,
		previousAverage,
		balance: previousAverage === null ? null : currentAverage - previousAverage,
	}
}

const TICK_STEPS = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20]

// A single weight or an unchanged one would otherwise get an axis of 120,0 to 120,1 with the
// point on the bottom line. At least one kilogram around the middle keeps it centered.
const MIN_TICK_SPAN = 1

export function getNiceTicks(values: number[], maxTicks = 4): number[] {
	if (!values.length) return []

	const middle = (Math.min(...values) + Math.max(...values)) / 2
	const min = Math.min(...values, middle - MIN_TICK_SPAN / 2)
	const max = Math.max(...values, middle + MIN_TICK_SPAN / 2)
	const step =
		TICK_STEPS.find((candidate) => (max - min) / candidate <= maxTicks - 1) ??
		TICK_STEPS[TICK_STEPS.length - 1]!

	const start = Math.floor(min / step) * step
	const end = Math.max(Math.ceil(max / step) * step, start + step)
	const count = Math.round((end - start) / step)

	return Array.from(
		{ length: count + 1 },
		(_, index) => Math.round((start + index * step) * 10) / 10,
	)
}

export function formatWeeklyBalance(balance: number): string {
	const rounded = Math.round(balance * 10) / 10

	if (rounded === 0) return 'Unverändert zu den 7 Tagen davor'

	const amount = Math.abs(rounded).toLocaleString('de-DE', {
		minimumFractionDigits: 1,
		maximumFractionDigits: 1,
	})

	return `${rounded < 0 ? 'Minus' : 'Plus'} ${amount} kg zu den 7 Tagen davor`
}

/** Change from the first to the last entry in the range, null with fewer than two entries */
export function getPeriodChange(points: WeightPoint[], days: number): number | null {
	const visible = limitToDays(points, days)
	const first = visible[0]
	const last = visible[visible.length - 1]

	if (!first || !last || first === last) return null

	return last.kg - first.kg
}

export function formatKgChange(change: number): string {
	const rounded = Math.round(change * 10) / 10
	const amount = Math.abs(rounded).toLocaleString('de-DE', {
		minimumFractionDigits: 1,
		maximumFractionDigits: 1,
	})

	if (rounded === 0) return `${amount} kg`

	return `${rounded < 0 ? '−' : '+'}${amount} kg`
}

export function formatPeriodChange(change: number, period: WeightPeriod): string {
	if (Math.round(change * 10) === 0) return `Unverändert ${period.phrase}`

	return `${formatKgChange(change)} ${period.phrase}`
}

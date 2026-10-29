import type { MealType, WeightPeriod } from '@features/tracking/tracking.types'

export const MEAL_LABELS: Record<MealType, string> = {
	breakfast: 'Frühstück',
	lunch: 'Mittagessen',
	dinner: 'Abendessen',
	snack: 'Snacks',
}

export const MEAL_ORDER: MealType[] = ['breakfast', 'lunch', 'dinner', 'snack']

export const WEIGHT_PERIODS: WeightPeriod[] = [
	{ value: '7', days: 7, label: 'Letzte 7 Tage', phrase: 'in den letzten 7 Tagen' },
	{ value: '30', days: 30, label: 'Letzte 30 Tage', phrase: 'in den letzten 30 Tagen' },
	{ value: '90', days: 90, label: 'Letzte 90 Tage', phrase: 'in den letzten 90 Tagen' },
	{ value: '365', days: 365, label: 'Letztes Jahr', phrase: 'im letzten Jahr' },
	{ value: 'gesamt', days: Infinity, label: 'Gesamt', phrase: 'seit deinem ersten Eintrag' },
]

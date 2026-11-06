import type { FoodReportReason, MealType, WeightPeriod } from '@features/tracking/tracking.types'

/** Same order as in the report form; staff see the same labels */
export const FOOD_REPORT_REASON_LABELS: Record<FoodReportReason, string> = {
	nutrition: 'Nährwerte falsch',
	unit: 'Gramm und Milliliter vertauscht',
	quantity: 'Portion oder Packung falsch',
	name: 'Name oder Marke falsch',
	other: 'Etwas anderes',
}

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

import type { AuthUser } from '@features/auth/auth.types'
import type {
	CalculatorPrefill,
	CalorieCalculatorValues,
} from '@features/calorie-calculator/calorie-calculator.types'

import { fetchNutritionSettings } from '@features/account/account.api'
import { fetchWeightEntries } from '@features/tracking/tracking.api'
import { ageOn } from '@shared/utils/date'

/**
 * Account details for the calculator: sex, age and height from "Persönliches", weight from the
 * latest diary entry and the goal from the nutrition settings. Missing details leave the field
 * empty. Only with tracking consent.
 */
export async function loadCalculatorPrefill(user: AuthUser): Promise<CalculatorPrefill> {
	const values: Partial<CalorieCalculatorValues> = {}
	const labels: string[] = []
	const { birthDate, heightCm, sex } = user.profile

	if (sex) {
		values.sex = sex
		labels.push('Geschlecht')
	}

	const age = birthDate ? ageOn(birthDate) : null

	if (age !== null) {
		values.age = age
		labels.push('Alter')
	}

	if (heightCm) {
		values.height = heightCm
		labels.push('Größe')
	}

	const [weights, settings] = await Promise.all([
		fetchWeightEntries().catch(() => []),
		fetchNutritionSettings().catch(() => null),
	])
	const latest = weights.at(-1)

	if (latest) {
		values.weight = latest.kg
		labels.push('Gewicht')
	}

	// Without a saved goal, the calculator's preselection stays
	if (settings?.goal) {
		values.goal = settings.goal
		labels.push('Ziel')
	}

	return { values, labels }
}

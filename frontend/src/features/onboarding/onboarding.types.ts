import type {
	CalorieCalculatorValues,
	Goal,
	Sex,
} from '@features/calorie-calculator/calorie-calculator.types'

export type NeedsMethod = 'calculate' | 'manual' | 'later'

export interface DailyNeeds {
	kcal: number
	/** Grams */
	protein: number
	/** Grams */
	carbs: number
	/** Grams */
	fat: number
	/** How the value came about. Not stored by the backend, so it is missing on loaded values. */
	source?: 'calculated' | 'manual'
}

export interface BodyData {
	/** YYYY-MM-DD */
	birthDate?: string
	sex?: Sex
	heightCm?: number
	weightKg?: number
}

export interface OnboardingData {
	username: string
	consent: boolean
	/** Undefined while the step was skipped */
	body?: BodyData
	goal?: Goal
	method?: NeedsMethod
	needs?: DailyNeeds
	calculatorValues?: Partial<CalorieCalculatorValues>
}

export interface OnboardingProgress {
	step: string
	consentAnswered: boolean
	data: OnboardingData
}

export type OnboardingStep = 'username' | 'consent' | 'goal' | 'targets' | 'summary'

export interface OnboardingStateResponse {
	completed: boolean
	current_step: OnboardingStep
}

export type OnboardingStepId =
	'username' | 'consent' | 'body' | 'goal' | 'method' | 'calculator' | 'manual' | 'done'

export interface OnboardingStepItem {
	id: OnboardingStepId
	part?: number
	result?: boolean
}

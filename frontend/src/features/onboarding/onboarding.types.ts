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

/** Body data from onboarding. Each detail is optional; saved to the account on completion. */
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
	/** Calculator inputs, kept between steps or carried over from the guest calculator */
	calculatorValues?: Partial<CalorieCalculatorValues>
}

/** Where the user is in onboarding. Kept in memory (onboarding store), never in the browser. */
export interface OnboardingProgress {
	/** Step key as it appears in the address, e.g. "ziel" */
	step: string
	consentAnswered: boolean
	data: OnboardingData
}

/** Coarse step as the backend knows it */
export type OnboardingStep = 'username' | 'consent' | 'goal' | 'targets' | 'summary'

export interface OnboardingStateResponse {
	completed: boolean
	current_step: OnboardingStep
}

export type OnboardingStepId =
	'username' | 'consent' | 'body' | 'goal' | 'method' | 'calculator' | 'manual' | 'done'

export interface OnboardingStepItem {
	id: OnboardingStepId
	/** Calculator section, phones only */
	part?: number
	/** Calculator result */
	result?: boolean
}

import type { Goal } from '@features/calorie-calculator/calorie-calculator.types'
import type { DailyNeeds } from '@features/onboarding/onboarding.types'
import type { Component } from 'vue'

export interface NutritionSettings {
	needs: DailyNeeds
	/** null when only target values but no goal have been saved */
	goal: Goal | null
}

export type GoalResponse = 'lose' | 'maintain' | 'gain'

export interface Targets {
	kcal: number
	protein: number
	carbs: number
	fat: number
}

export interface GoalStateResponse {
	goal: GoalResponse | null
	targets: Targets | null
	valid_from: string | null
}

export interface AccountZone {
	routeName: string
	title: string
	icon: Component
	danger?: boolean
}

export type EmailChangeState = 'pending' | 'changed' | 'taken' | 'failed'

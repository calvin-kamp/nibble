import type {
	CalculatorSection,
	Goal,
	Sex,
	TrainingGroup,
	Workout,
} from '@features/calorie-calculator/calorie-calculator.types'
import type { FieldOption, FieldOptionGroup } from '@shared/forms/types'

/** Walking MET, Compendium of Physical Activities code 17190 */
export const WALKING_MET = 3.5

/** Assumed cadence, used to derive walking minutes from step count */
export const STEPS_PER_MINUTE = 110

/** Thermic effect of food, share of intake (mixed diet) */
export const TEF_SHARE = 0.1

/** Atwater factors — must match the values on food labels */
export const KCAL_PER_GRAM = { protein: 4, carbs: 4, fat: 9 } as const

/** Target calories relative to maintenance */
export const GOAL_FACTOR: Record<Goal, number> = {
	diet: 0.85,
	maintain: 1,
	gain: 1.1,
}

/** Absolute intake floors — below this, micronutrient needs are hard to meet */
export const MIN_INTAKE: Record<Sex, number> = {
	male: 1500,
	female: 1300,
}

/** BMI used to derive the reference weight for nutrient needs */
export const REFERENCE_BMI = 25

/** Share of the excess above reference weight that still counts */
export const EXCESS_WEIGHT_SHARE = 0.25

/** Protein in g per kg of nutrient weight */
export const PROTEIN_PER_KG: Record<Goal, number> = {
	diet: 2,
	maintain: 1.6,
	gain: 1.8,
}

/** Fat in g per kg of nutrient weight — diet only */
export const FAT_PER_KG_IN_DIET: Record<Sex, number> = {
	male: 0.8,
	female: 1,
}

/** Fat as share of target calories — maintain and gain */
export const FAT_SHARE_OUTSIDE_DIET: Record<Sex, number> = {
	male: 0.25,
	female: 0.3,
}

/** Fat floor in g per kg — protects fat-soluble vitamins and essential fatty acids */
export const FAT_MINIMUM_PER_KG = 0.6

/** Fat ceiling as share of target calories — keeps carbs from being squeezed out */
export const FAT_MAX_SHARE = 0.35

/**
 * Protein ceiling as share of target calories, the upper end of the usual range (10–35 %).
 * Without it, a low target and a high reference weight push protein past half of all calories.
 */
export const PROTEIN_MAX_SHARE = 0.35

/** Below this BMI no deficit is calculated */
export const UNDERWEIGHT_BMI = 18.5

/** Below this age no deficit is calculated — Mifflin-St Jeor is validated for adults only */
export const ADULT_AGE = 18

/** Upper limit for training per session, in minutes */
export const MAX_WORKOUT_MINUTES = 300

/** Upper limit for all training combined, in minutes per week (20 hours) */
export const MAX_WEEKLY_TRAINING_MINUTES = 1200

/** Calculator sections in order. On phones, each one is a separate step. */
export const CALCULATOR_SECTIONS: readonly CalculatorSection[] = [
	'basal',
	'steps',
	'training',
	'goal',
]

export const GOAL_LABELS: Record<Goal, string> = {
	diet: 'Abnehmen',
	maintain: 'Gewicht halten',
	gain: 'Zunehmen',
}

export const GOAL_OPTIONS: FieldOption[] = [
	{ value: 'diet', label: GOAL_LABELS.diet, description: '15 % unter deinem Erhaltungsbedarf' },
	{ value: 'maintain', label: GOAL_LABELS.maintain, description: 'Genau dein Erhaltungsbedarf' },
	{ value: 'gain', label: GOAL_LABELS.gain, description: '10 % über deinem Erhaltungsbedarf' },
]

export const SEX_LABELS: Record<Sex, string> = {
	male: 'Männlich',
	female: 'Weiblich',
}

export const SEX_OPTIONS: FieldOption[] = [
	{ value: 'male', label: SEX_LABELS.male },
	{ value: 'female', label: SEX_LABELS.female },
]

/**
 * Walking is deliberately missing: it is already covered by the step count.
 * For running and hiking the phone often counts steps as well, which the hint in the form
 * points out.
 */
export const TRAINING_GROUPS: TrainingGroup[] = [
	{
		label: 'Ausdauer',
		activities: [
			{ label: 'Laufen, locker (8 km/h)', met: 8.3 },
			{ label: 'Laufen, zügig (10 km/h)', met: 9.8 },
			{ label: 'Radfahren, gemütlich', met: 4 },
			{ label: 'Radfahren, zügig', met: 8 },
			{ label: 'Schwimmen, gemütlich', met: 6 },
			{ label: 'Schwimmen, Bahnen zügig', met: 9.8 },
			{ label: 'Rudergerät, moderat', met: 7 },
			{ label: 'Crosstrainer, moderat', met: 5 },
			{ label: 'Wandern', met: 6 },
		],
	},
	{
		label: 'Kraft und Fitness',
		activities: [
			{ label: 'Krafttraining, moderat', met: 3.5 },
			{ label: 'Krafttraining, intensiv', met: 6 },
			{ label: 'Zirkeltraining oder HIIT', met: 8 },
			{ label: 'Yoga', met: 2.5 },
			{ label: 'Pilates', met: 3 },
		],
	},
	{
		label: 'Ballsport',
		activities: [
			{ label: 'Fußball', met: 7 },
			{ label: 'Basketball', met: 6.5 },
			{ label: 'Tennis', met: 7.3 },
			{ label: 'Tischtennis', met: 4 },
			{ label: 'Volleyball', met: 4 },
		],
	},
	{
		label: 'Weitere',
		activities: [
			{ label: 'Tanzen', met: 4.5 },
			{ label: 'Klettern oder Bouldern', met: 5.8 },
			{ label: 'Kampfsport', met: 5.3 },
		],
	},
]

/** Option value in the format groupIndex-optionIndex-MET, as read by calculateCalories */
function optionValue(groupIndex: number, activityIndex: number, met: number): string {
	return `${groupIndex}-${activityIndex}-${met}`
}

export const TRAINING_SELECT_GROUPS: FieldOptionGroup[] = TRAINING_GROUPS.map(
	(group, groupIndex) => ({
		label: group.label,
		options: group.activities.map((activity, activityIndex) => ({
			value: optionValue(groupIndex, activityIndex, activity.met),
			label: activity.label,
		})),
	}),
)

export const EMPTY_WORKOUT: Workout = { met: '', duration: 0, frequency: 0 }

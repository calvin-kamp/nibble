import type {
	CalculatorSection,
	Goal,
	Sex,
	TrainingGroup,
	Workout,
} from '@features/calorie-calculator/calorie-calculator.types'
import type { FieldOption } from '@shared/forms/types'

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
		label: 'Krafttraining',
		activities: [
			{ label: 'Krafttraining, hart', met: 6 },
			{ label: 'Krafttraining, mittel', met: 4.5 },
			{ label: 'Krafttraining, leicht', met: 3 },
			{ label: 'Zirkeltraining', met: 7 },
			{ label: 'Calisthenics, intensiv', met: 8 },
			{ label: 'Calisthenics, moderat', met: 3.8 },
		],
	},
	{
		label: 'Ausdauer',
		activities: [
			{ label: 'Joggen, langsam (~8 km/h)', met: 8 },
			{ label: 'Joggen, moderat (~10 km/h)', met: 10 },
			{ label: 'Laufen, zügig (~12 km/h)', met: 12.5 },
			{ label: 'Laufen, schnell (~16 km/h)', met: 16 },
			{ label: 'Radfahren, leicht (~15 km/h)', met: 6 },
			{ label: 'Radfahren, moderat (~20 km/h)', met: 8 },
			{ label: 'Radfahren, schnell (~25 km/h)', met: 10 },
			{ label: 'Schwimmen, locker', met: 6 },
			{ label: 'Schwimmen, moderat (Bahnen)', met: 8 },
			{ label: 'Schwimmen, intensiv (Kraul)', met: 10 },
			{ label: 'Rudergerät, moderat', met: 7 },
			{ label: 'Rudergerät, intensiv', met: 8.5 },
			{ label: 'Crosstrainer', met: 5 },
			{ label: 'Seilspringen', met: 12 },
			{ label: 'HIIT / Intervalltraining', met: 8 },
		],
	},
	{
		label: 'Spielsport',
		activities: [
			{ label: 'Fußball (locker)', met: 7 },
			{ label: 'Fußball (Wettkampf)', met: 10 },
			{ label: 'Handball (locker)', met: 8 },
			{ label: 'Handball (Wettkampf)', met: 12 },
			{ label: 'Basketball (locker)', met: 6 },
			{ label: 'Basketball (Wettkampf)', met: 8 },
			{ label: 'Badminton (Freizeit)', met: 4.5 },
			{ label: 'Badminton (Wettkampf)', met: 7 },
			{ label: 'Tennis (Doppel)', met: 6 },
			{ label: 'Tennis (Einzel)', met: 8 },
			{ label: 'Volleyball (Freizeit)', met: 4 },
			{ label: 'Volleyball (Wettkampf)', met: 6 },
			{ label: 'Tischtennis', met: 4 },
		],
	},
	{
		label: 'Mobilität',
		activities: [
			{ label: 'Yoga', met: 2.5 },
			{ label: 'Pilates', met: 3 },
			{ label: 'Dehnen / Mobility', met: 2.3 },
		],
	},
]

export const EMPTY_WORKOUT: Workout = { met: '', duration: 0, frequency: 0 }

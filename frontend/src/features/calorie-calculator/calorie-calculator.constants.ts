import type { Goal, Sex } from './calorie-calculator.types'

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

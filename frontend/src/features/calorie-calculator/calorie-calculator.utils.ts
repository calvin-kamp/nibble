import type {
	CalorieCalculatorValues,
	CalorieResult,
	Macro,
	MacroGrams,
	MacroInput,
	Workout,
} from '@features/calorie-calculator/calorie-calculator.types'
import type { DailyNeeds } from '@features/onboarding/onboarding.types'

import {
	EXCESS_WEIGHT_SHARE,
	FAT_MAX_SHARE,
	FAT_MINIMUM_PER_KG,
	FAT_PER_KG_IN_DIET,
	FAT_SHARE_OUTSIDE_DIET,
	GOAL_FACTOR,
	KCAL_PER_GRAM,
	MIN_INTAKE,
	PROTEIN_MAX_SHARE,
	PROTEIN_PER_KG,
	REFERENCE_BMI,
	STEPS_PER_MINUTE,
	TEF_SHARE,
	TRAINING_GROUPS,
	WALKING_MET,
} from '@features/calorie-calculator/calorie-calculator.constants'

/**
 * Reads the MET out of a compound option value (`groupIndex-optionIndex-MET`).
 *
 * Returns null instead of NaN. Training is optional, so an unfinished entry carries an
 * empty string, and a silent NaN here would propagate through every figure in the result.
 */
function metFromValue(value: string): number | null {
	const met: number = Number(value.split('-')[2])

	return Number.isFinite(met) ? met : null
}

/**
 * Daily energy needs from an additive net-MET model.
 *
 * Expenditure is assembled from three parts rather than a single activity multiplier:
 *
 * 1. Basal metabolic rate via Mifflin-St Jeor (1990) — resting expenditure predicted from
 *    weight, height, age and sex. The most accurate of the widely used predictive equations
 *    for a general population; it underestimates at very low body weight and for people
 *    carrying unusual muscle mass.
 * 2. Everyday movement — step count converted to walking minutes at a fixed cadence, priced
 *    with the walking MET from the Compendium of Physical Activities.
 * 3. Training — the same arithmetic per session, averaged from a weekly schedule down to a
 *    daily figure.
 *
 * Parts 2 and 3 use MET − 1, not MET. One MET is resting expenditure, which the basal rate
 * already accounts for; without the subtraction every active minute is counted twice.
 *
 * The thermic effect of food is a share of what is eaten, not of what is burned, so
 * maintenance is the sum divided by (1 − TEF_SHARE), not multiplied by (1 + TEF_SHARE).
 *
 * The goal factor is relative rather than a fixed offset: 500 kcal is a third of a 1500 kcal
 * budget and a sixth of a 3000 kcal one.
 *
 * One floor then applies: the absolute intake minimum. Whenever it binds,
 * `safetyAdjustment` is non-zero and the UI has to explain it; otherwise the target stops
 * responding to input for no visible reason.
 *
 * There is deliberately no second floor at the basal rate. Without activity, maintenance is
 * the basal rate divided by 0.9, so a diet target lands at 0.944 of the basal rate by
 * construction — such a floor would bind for every sedentary user and make weight loss
 * unreachable. What matters is absolute intake and the size of the deficit, not the ratio to
 * resting expenditure.
 *
 * Incomplete workouts are skipped, not rejected. Training is optional, so a started but
 * unfinished entry must neither contribute nor fail.
 */
export function calculateCalories(values: CalorieCalculatorValues): CalorieResult {
	const basalMetabolicRate: number =
		10 * values.weight +
		6.25 * values.height -
		5 * values.age +
		(values.sex === 'male' ? 5 : -161)

	const stepsConsumption: number =
		((WALKING_MET - 1) * values.weight * values.steps) / (STEPS_PER_MINUTE * 60)

	const trainingConsumption: number = values.exercises.reduce(
		(total: number, workout: Workout) => {
			const met: number | null = metFromValue(workout.met)

			if (met === null || workout.duration <= 0 || workout.frequency <= 0) {
				return total
			}

			return (
				total +
				(met - 1) * values.weight * (workout.duration / 60) * (workout.frequency / 7)
			)
		},
		0,
	)

	const consumptionBeforeTef: number = basalMetabolicRate + stepsConsumption + trainingConsumption

	const maintenanceCalories: number = consumptionBeforeTef / (1 - TEF_SHARE)

	const rawTargetCalories: number = maintenanceCalories * GOAL_FACTOR[values.goal]

	const targetCalories: number = Math.max(rawTargetCalories, MIN_INTAKE[values.sex])

	const safetyAdjustment: number = targetCalories - rawTargetCalories

	const macros = calculateMacros({
		weight: values.weight,
		height: values.height,
		sex: values.sex,
		goal: values.goal,
		targetCalories,
	})

	return {
		basalMetabolicRate,
		stepsConsumption,
		trainingConsumption,
		consumptionBeforeTef,
		maintenanceCalories,
		targetCalories,
		safetyAdjustment,
		macros,
	}
}

/**
 * Macro split for an already capped calorie target.
 *
 * Protein and fat are set first and carbohydrates take the remainder, because protein and
 * fat have established minimum requirements and carbohydrates do not.
 *
 * Both are sized from a reference weight rather than actual weight. Nutrient needs scale
 * with metabolically active mass while energy needs scale with total mass, and the two
 * diverge as body fat rises. The reference is the weight at the top of the normal BMI range;
 * above it only a share of the excess counts, so a very heavy person is not prescribed
 * protein for tissue that makes no such demand.
 *
 * Protein per kilogram is highest while dieting. A deficit costs lean mass, and a raised
 * intake both limits that loss and helps with satiety.
 *
 * Fat is derived from body weight while dieting and from a share of the target otherwise.
 * A share of a shrinking budget would collapse fat at low targets; a per-kilogram figure
 * would push it too high at large ones. A floor protects absorption of fat-soluble vitamins
 * and the supply of essential fatty acids; a ceiling keeps carbohydrates from being squeezed
 * out when the target is small.
 *
 * Protein has a ceiling as well. A low target combined with a high reference weight would
 * otherwise put protein above half of all calories and carbohydrates under 60 g.
 *
 * The carbohydrate remainder cannot turn negative: the fat and protein ceilings together
 * stay below the target.
 */
export function calculateMacros(data: MacroInput): Macro[] {
	const referenceWeight: number = (data.height / 100) ** 2 * REFERENCE_BMI

	const nutrientWeight: number =
		data.weight > referenceWeight
			? referenceWeight + (data.weight - referenceWeight) * EXCESS_WEIGHT_SHARE
			: data.weight

	const proteinInG: number = Math.min(
		PROTEIN_PER_KG[data.goal] * nutrientWeight,
		(data.targetCalories * PROTEIN_MAX_SHARE) / KCAL_PER_GRAM.protein,
	)

	const fatBase: number =
		data.goal === 'diet'
			? FAT_PER_KG_IN_DIET[data.sex] * nutrientWeight
			: (FAT_SHARE_OUTSIDE_DIET[data.sex] * data.targetCalories) / KCAL_PER_GRAM.fat

	const fatWithMinimum: number = Math.max(fatBase, FAT_MINIMUM_PER_KG * nutrientWeight)

	const fatInG: number = Math.min(
		fatWithMinimum,
		(data.targetCalories * FAT_MAX_SHARE) / KCAL_PER_GRAM.fat,
	)

	const carbsInKcal: number =
		data.targetCalories - proteinInG * KCAL_PER_GRAM.protein - fatInG * KCAL_PER_GRAM.fat

	return [
		{
			name: 'Fett',
			amount: fatInG,
			kcal: fatInG * KCAL_PER_GRAM.fat,
		},
		{
			name: 'Protein',
			amount: proteinInG,
			kcal: proteinInG * KCAL_PER_GRAM.protein,
		},
		{
			name: 'Kohlenhydrate',
			amount: carbsInKcal / KCAL_PER_GRAM.carbs,
			kcal: carbsInKcal,
		},
	]
}

export function macrosToKcal(macros: MacroGrams): number {
	return (
		macros.protein * KCAL_PER_GRAM.protein +
		macros.carbs * KCAL_PER_GRAM.carbs +
		macros.fat * KCAL_PER_GRAM.fat
	)
}

/** Calculator result as daily needs, calories rounded to 10, macros to whole grams */
export function resultToNeeds(result: CalorieResult): DailyNeeds {
	const grams = (name: string): number =>
		Math.round(result.macros.find((macro) => macro.name === name)?.amount ?? 0)

	return {
		kcal: Math.round(result.targetCalories / 10) * 10,
		protein: grams('Protein'),
		carbs: grams('Kohlenhydrate'),
		fat: grams('Fett'),
		source: 'calculated',
	}
}

export function trainingLabel(value: string): string | undefined {
	const [groupIndex, activityIndex] = value.split('-').map(Number)

	return TRAINING_GROUPS[groupIndex ?? -1]?.activities[activityIndex ?? -1]?.label
}

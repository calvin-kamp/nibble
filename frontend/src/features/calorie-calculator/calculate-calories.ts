import { calculateMacros } from './calculate-macros'
import {
  GOAL_FACTOR,
  MIN_INTAKE,
  STEPS_PER_MINUTE,
  TEF_SHARE,
  WALKING_MET,
} from './calorie-calculator.constants'
import type { CalorieCalculatorValues, CalorieResult, Workout } from './calorie-calculator.types'

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
    10 * values.weight + 6.25 * values.height - 5 * values.age + (values.sex === 'male' ? 5 : -161)

  const stepsConsumption: number =
    ((WALKING_MET - 1) * values.weight * values.steps) / (STEPS_PER_MINUTE * 60)

  const trainingConsumption: number = values.exercises.reduce((total: number, workout: Workout) => {
    const met: number | null = metFromValue(workout.met)

    if (met === null || workout.duration <= 0 || workout.frequency <= 0) {
      return total
    }

    return total + (met - 1) * values.weight * (workout.duration / 60) * (workout.frequency / 7)
  }, 0)

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

import {
  EXCESS_WEIGHT_SHARE,
  FAT_MAX_SHARE,
  FAT_MINIMUM_PER_KG,
  FAT_PER_KG_IN_DIET,
  FAT_SHARE_OUTSIDE_DIET,
  KCAL_PER_GRAM,
  PROTEIN_PER_KG,
  REFERENCE_BMI,
} from './calorie-calculator.constants'
import type { Macro, MacroInput } from './calorie-calculator.types'

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
 * The carbohydrate remainder cannot turn negative: the fat ceiling and the protein amount
 * are each bounded well below the target.
 */
export function calculateMacros(data: MacroInput): Macro[] {
  const referenceWeight: number = (data.height / 100) ** 2 * REFERENCE_BMI

  const nutrientWeight: number =
    data.weight > referenceWeight
      ? referenceWeight + (data.weight - referenceWeight) * EXCESS_WEIGHT_SHARE
      : data.weight

  const proteinInG: number = PROTEIN_PER_KG[data.goal] * nutrientWeight

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

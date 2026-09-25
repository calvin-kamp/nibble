import type {
  RecipeBadge,
  RecipeBadgeSummary,
  RecipeFormValues,
  RecipeListItem,
  RecipeIngredient,
  RecipePayload,
  RecipeUnit,
} from './recipes.types'

import { ATTRIBUTE_BADGE_ORDER, DIET_BADGE_ORDER, MACRO_MAX_GRAMS } from './recipes.data'

export function toSlug(value: string): string {
  return value
    .toLowerCase()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export function getRecipeBadgeSummary(recipe: RecipeListItem): RecipeBadgeSummary {
  const badges: RecipeBadge[] = []

  const diet = DIET_BADGE_ORDER.find((diet) => recipe.diets.includes(diet))
  if (diet) badges.push({ label: diet, variant: 'default' })

  const attribute = ATTRIBUTE_BADGE_ORDER.find((attribute) => recipe.attributes.includes(attribute))
  if (attribute) badges.push({ label: attribute, variant: 'secondary' })

  return {
    badges,
    hiddenCount: recipe.diets.length + recipe.attributes.length - badges.length,
  }
}

const PLURAL_UNITS: Partial<Record<RecipeUnit, string>> = {
  Zehe: 'Zehen',
  Dose: 'Dosen',
  Scheibe: 'Scheiben',
  Packung: 'Packungen',
  Prise: 'Prisen',
}

const WHOLE_NUMBER_UNITS: RecipeUnit[] = ['g', 'ml']
const DECIMAL_UNITS: RecipeUnit[] = ['kg', 'l']

function toHalves(amount: number): string {
  const rounded = Math.max(0.5, Math.round(amount * 2) / 2)
  const whole = Math.floor(rounded)

  if (rounded % 1 === 0) return String(whole)

  return whole === 0 ? '½' : `${whole}½`
}

export function formatIngredientAmount(
  ingredient: RecipeIngredient,
  baseServings: number,
  servings: number,
): string {
  const scaled =
    ingredient.unit === 'Prise' ? ingredient.amount : (ingredient.amount / baseServings) * servings

  let value: number
  let amount: string

  if (WHOLE_NUMBER_UNITS.includes(ingredient.unit)) {
    value = Math.round(scaled)
    amount = String(value)
  } else if (DECIMAL_UNITS.includes(ingredient.unit)) {
    value = Math.round(scaled * 10) / 10
    amount = value.toLocaleString('de-DE')
  } else {
    value = Math.max(0.5, Math.round(scaled * 2) / 2)
    amount = toHalves(scaled)
  }

  if (ingredient.unit === 'Stück') return amount

  const unit = value > 1 ? (PLURAL_UNITS[ingredient.unit] ?? ingredient.unit) : ingredient.unit

  return `${amount} ${unit}`
}

export function isMacroValue(value: unknown): value is number {
  return (
    typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= MACRO_MAX_GRAMS
  )
}

/** Atwater factors — must match the backend, which stores the result */
export function calculateKcal(protein: number, carbs: number, fat: number): number {
  return Math.round(protein * 4 + carbs * 4 + fat * 9)
}

export function toRecipePayload(values: RecipeFormValues): RecipePayload {
  const { image: _image, ...payload } = values

  return payload
}

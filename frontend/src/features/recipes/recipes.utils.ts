import { DIET_BADGE_ORDER, PROPERTY_BADGE_ORDER } from './recipes.data'
import type { Recipe, RecipeBadge, RecipeBadgeSummary } from './recipes.types'

export function getRecipeBadgeSummary(recipe: Recipe): RecipeBadgeSummary {
  const badges: RecipeBadge[] = []

  const diet = DIET_BADGE_ORDER.find((diet) => recipe.diets.includes(diet))
  if (diet) badges.push({ label: diet, variant: 'default' })

  const property = PROPERTY_BADGE_ORDER.find((property) => recipe.properties.includes(property))
  if (property) badges.push({ label: property, variant: 'secondary' })

  return {
    badges,
    hiddenCount: recipe.diets.length + recipe.properties.length - badges.length,
  }
}

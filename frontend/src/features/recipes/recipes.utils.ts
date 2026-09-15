import type { Recipe, RecipeBadge, RecipeBadgeSummary } from './recipes.types'

import { DIET_BADGE_ORDER, PROPERTY_BADGE_ORDER } from './recipes.data'

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

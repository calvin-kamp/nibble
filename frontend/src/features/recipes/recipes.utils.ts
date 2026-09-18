import type { RecipeBadge, RecipeBadgeSummary, RecipeListItem } from './recipes.types'

import { ATTRIBUTE_BADGE_ORDER, DIET_BADGE_ORDER } from './recipes.data'

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

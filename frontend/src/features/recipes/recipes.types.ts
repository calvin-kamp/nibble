import type { SelectOption } from '@interfaces/form.types'
import type { BadgeVariants } from '@components/ui/variants'

// Labels, not slugs: the API returns the display value for every choice field.
export type Diet = 'Vegan' | 'Vegetarisch' | 'Pescetarisch'

export type Intolerance = 'Glutenfrei' | 'Laktosefrei'

export type MealType = 'Frühstück' | 'Mittagessen' | 'Abendessen' | 'Snack' | 'Dessert'

export type Equipment = 'Herd' | 'Backofen' | 'Mixer' | 'Airfryer' | 'Ohne Kochen'

export type Attribute =
  'Proteinreich' | 'Kalorienarm' | 'Meal Prep' | 'Unter 30 Min' | 'Wenig Zutaten'

export type RecipeUnit =
  | 'g'
  | 'kg'
  | 'ml'
  | 'l'
  | 'TL'
  | 'EL'
  | 'Prise'
  | 'Stück'
  | 'Zehe'
  | 'Bund'
  | 'Scheibe'
  | 'Dose'
  | 'Packung'

export interface RecipeIngredient {
  ingredient: string
  amount: number
  unit: RecipeUnit
}

export interface CookingStep {
  step: number
  text: string
}

export interface RecipeListItem {
  id: number
  slug: string
  name: string
  image: string | null
  durationMinutes: number
  kcalPerServing: number
  diets: Diet[]
  intolerances: Intolerance[]
  mealTypes: MealType[]
  equipment: Equipment[]
  attributes: Attribute[]
  // ISO string, JSON has no Date type.
  createdAt: string
}

export interface RecipeDetail extends RecipeListItem {
  description: string
  servings: number
  proteinPerServing: number
  carbsPerServing: number
  fatPerServing: number
  ingredients: RecipeIngredient[]
  cookingSteps: CookingStep[]
}

// Filter keys are the recipe fields they filter, so the filter can read the field directly.
export type RecipeFilterKey = 'diets' | 'intolerances' | 'mealTypes' | 'equipment' | 'attributes'

/** any: at least one selected value · all: every selected value · subset: recipe needs nothing unselected */
export type RecipeFilterMode = 'any' | 'all' | 'subset'

export interface RecipeFilterGroup {
  key: RecipeFilterKey
  /** URL query parameter, e.g. 'ernaehrung'. */
  param: string
  mode: RecipeFilterMode
  triggerLabel: string
  filterDescription?: string
  options: SelectOption[]
}

export type RecipeFilterState = Record<RecipeFilterKey, string[]>

export interface RecipeBadge {
  label: string
  variant: BadgeVariants['variant']
}

export interface RecipeBadgeSummary {
  badges: RecipeBadge[]
  hiddenCount: number
}

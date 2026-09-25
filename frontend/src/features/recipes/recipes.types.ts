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
  name: string
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
  /** Only the owner may edit or delete */
  isOwner: boolean
  updatedAt: string
}

// Filter keys are the recipe fields they filter, so the filter can read the field directly.
export type RecipeFilterKey = 'diets' | 'intolerances' | 'mealTypes' | 'equipment' | 'attributes'

export interface RecipeFilterGroup {
  key: RecipeFilterKey
  /** URL query parameter, e.g. 'ernaehrung'. */
  param: string
  triggerLabel: string
  filterDescription?: string
  options: SelectOption[]
}

export type RecipeFilterState = Record<RecipeFilterKey, string[]>

/** Query parameters of the list endpoint, same names as in the page URL */
export type RecipeListQuery = Record<string, string>

export interface RecipeBadge {
  label: string
  variant: BadgeVariants['variant']
}

export interface RecipeBadgeSummary {
  badges: RecipeBadge[]
  hiddenCount: number
}

/** Form input — matches recipeSchema */
export interface RecipeFormValues {
  /** File: new upload · string: URL of the saved image · null: no image */
  image: File | string | null
  name: string
  description: string
  servings: number
  durationMinutes: number
  mealTypes: MealType[]
  equipment: Equipment[]
  diets: Diet[]
  intolerances: Intolerance[]
  attributes: Attribute[]
  ingredients: RecipeIngredient[]
  /** Numbered by the backend in list order */
  cookingSteps: Pick<CookingStep, 'text'>[]
  proteinPerServing: number
  carbsPerServing: number
  fatPerServing: number
}

/** Body for create and update — the image has its own endpoint, kcal is calculated by the backend */
export type RecipePayload = Omit<RecipeFormValues, 'image'>

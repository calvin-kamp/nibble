import type { Option } from '@/types/form.types'

export type Diet = 'Vegetarisch' | 'Vegan' | 'Pescetarisch'
export type Intolerance = 'Glutenfrei' | 'Laktosefrei'
export type MealType = 'Frühstück' | 'Mittagessen' | 'Abendessen' | 'Snack' | 'Dessert'
export type Equipment = 'Backofen' | 'Herd' | 'Mixer' | 'Airfryer' | 'Ohne Kochen'
export type Property =
  'Proteinreich' | 'Kalorienarm' | 'Meal Prep' | 'Unter 30 Min' | 'Wenig Zutaten'

export type RecipeFilterKey = 'diets' | 'intolerances' | 'mealType' | 'properties' | 'equipment'
export type RecipeFilterMode = 'any' | 'all' | 'subset'

export interface RecipeImage {
  src: string
  alt: string
}

export interface RecipeBadge {
  label: Diet | Property
  variant: 'default' | 'secondary'
}

export interface RecipeBadgeSummary {
  badges: RecipeBadge[]
  hiddenCount: number
}

export interface Recipe {
  id: number
  image: RecipeImage | null
  name: string
  durationMinutes: number
  diets: Diet[]
  intolerances: Intolerance[]
  mealType: MealType
  equipment: Equipment[]
  properties: Property[]
  kcalPerServing: number
  createdAt: Date
}

export interface RecipeFilterGroup {
  key: RecipeFilterKey
  param: string
  mode: RecipeFilterMode
  triggerLabel: string
  filterDescription?: string
  options: Option[]
}

export type RecipeFilterState = Record<RecipeFilterKey, string[]>

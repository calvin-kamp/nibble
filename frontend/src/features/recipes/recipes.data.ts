import type { RecipeFilterGroup } from './recipes.types'

export const DIET_BADGE_ORDER = ['Vegan', 'Vegetarisch', 'Pescetarisch'] as const
export const PROPERTY_BADGE_ORDER = [
  'Proteinreich',
  'Kalorienarm',
  'Unter 30 Min',
  'Meal Prep',
  'Wenig Zutaten',
] as const

export const filterOptions: RecipeFilterGroup[] = [
  {
    key: 'diets',
    param: 'ernaehrung',
    mode: 'any',
    triggerLabel: 'Ernährung',
    filterDescription: 'Mehrfachauswahl zeigt Rezepte, die mindestens eine Form erfüllen.',
    options: [
      { value: 'Vegan', label: 'Vegan' },
      { value: 'Vegetarisch', label: 'Vegetarisch' },
      { value: 'Pescetarisch', label: 'Pescetarisch' },
    ],
  },
  {
    key: 'intolerances',
    param: 'unvertraeglichkeit',
    mode: 'all',
    triggerLabel: 'Unverträglichkeit',
    filterDescription: 'Alle gewählten Angaben müssen zutreffen.',
    options: [
      { value: 'Glutenfrei', label: 'Glutenfrei' },
      { value: 'Laktosefrei', label: 'Laktosefrei' },
    ],
  },
  {
    key: 'mealType',
    param: 'mahlzeit',
    mode: 'any',
    triggerLabel: 'Mahlzeit',
    options: [
      { value: 'Frühstück', label: 'Frühstück' },
      { value: 'Mittagessen', label: 'Mittagessen' },
      { value: 'Abendessen', label: 'Abendessen' },
      { value: 'Snack', label: 'Snack' },
      { value: 'Dessert', label: 'Dessert' },
    ],
  },
  {
    key: 'properties',
    param: 'eigenschaften',
    mode: 'all',
    triggerLabel: 'Eigenschaften',
    filterDescription: 'Alle gewählten Eigenschaften müssen zutreffen.',
    options: [
      { value: 'Proteinreich', label: 'Proteinreich' },
      { value: 'Kalorienarm', label: 'Kalorienarm' },
      { value: 'Meal Prep', label: 'Meal Prep' },
      { value: 'Unter 30 Min', label: 'Unter 30 Min' },
      { value: 'Wenig Zutaten', label: 'Wenig Zutaten' },
    ],
  },
  {
    key: 'equipment',
    param: 'ausstattung',
    mode: 'subset',
    triggerLabel: 'Ausstattung',
    filterDescription: 'Wähle, was du hast. Es werden nur Rezepte gezeigt, die damit auskommen.',
    options: [
      { value: 'Backofen', label: 'Backofen' },
      { value: 'Herd', label: 'Herd' },
      { value: 'Mixer', label: 'Mixer' },
      { value: 'Airfryer', label: 'Airfryer' },
      { value: 'Ohne Kochen', label: 'Ohne Kochen' },
    ],
  },
]

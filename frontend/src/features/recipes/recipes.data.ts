import type { SelectOption } from '@interfaces/form.types'
import type { Attribute, Diet, RecipeFilterGroup } from './recipes.types'

export const DIET_BADGE_ORDER: readonly Diet[] = ['Vegan', 'Vegetarisch', 'Pescetarisch']
export const ATTRIBUTE_BADGE_ORDER: readonly Attribute[] = [
  'Proteinreich',
  'Kalorienarm',
  'Unter 30 Min',
  'Meal Prep',
  'Wenig Zutaten',
]

/** Both the drawer trigger and the panel trigger carry it, so the chips can return the focus */
export const FILTER_TRIGGER_ID = 'rezept-filter'

/** Page size of the list — must match RecipePagination in the backend */
export const RECIPES_PER_PAGE = 12

/** Upper limits — must match the backend models */
export const MACRO_MAX_GRAMS = 500
export const INGREDIENT_NAME_MAX_LENGTH = 60
export const DESCRIPTION_MAX_LENGTH = 500
export const COOKING_STEP_MAX_LENGTH = 500
export const AMOUNT_MAX = 9999.9

/** Accepted image uploads — must match the backend check */
export const IMAGE_TYPES: readonly string[] = ['image/jpeg', 'image/png', 'image/webp']
export const IMAGE_MAX_BYTES = 5 * 1024 * 1024

export const dietOptions: SelectOption[] = [
  { value: 'Vegan', label: 'Vegan' },
  { value: 'Vegetarisch', label: 'Vegetarisch' },
  { value: 'Pescetarisch', label: 'Pescetarisch' },
]

export const intoleranceOptions: SelectOption[] = [
  { value: 'Glutenfrei', label: 'Glutenfrei' },
  { value: 'Laktosefrei', label: 'Laktosefrei' },
]

export const mealTypeOptions: SelectOption[] = [
  { value: 'Frühstück', label: 'Frühstück' },
  { value: 'Mittagessen', label: 'Mittagessen' },
  { value: 'Abendessen', label: 'Abendessen' },
  { value: 'Snack', label: 'Snack' },
  { value: 'Dessert', label: 'Dessert' },
]

export const attributeOptions: SelectOption[] = [
  { value: 'Proteinreich', label: 'Proteinreich' },
  { value: 'Kalorienarm', label: 'Kalorienarm' },
  { value: 'Meal Prep', label: 'Meal Prep' },
  { value: 'Unter 30 Min', label: 'Unter 30 Min' },
  { value: 'Wenig Zutaten', label: 'Wenig Zutaten' },
]

export const equipmentOptions: SelectOption[] = [
  { value: 'Backofen', label: 'Backofen' },
  { value: 'Herd', label: 'Herd' },
  { value: 'Mixer', label: 'Mixer' },
  { value: 'Airfryer', label: 'Airfryer' },
  { value: 'Ohne Kochen', label: 'Ohne Kochen' },
]

export const unitOptions: SelectOption[] = [
  { value: 'g', label: 'g' },
  { value: 'kg', label: 'kg' },
  { value: 'ml', label: 'ml' },
  { value: 'l', label: 'l' },
  { value: 'TL', label: 'TL' },
  { value: 'EL', label: 'EL' },
  { value: 'Prise', label: 'Prise' },
  { value: 'Stück', label: 'Stück' },
  { value: 'Zehe', label: 'Zehe' },
  { value: 'Bund', label: 'Bund' },
  { value: 'Scheibe', label: 'Scheibe' },
  { value: 'Dose', label: 'Dose' },
  { value: 'Packung', label: 'Packung' },
]

export const filterOptions: RecipeFilterGroup[] = [
  {
    key: 'diets',
    param: 'ernaehrung',
    triggerLabel: 'Ernährung',
    filterDescription: 'Mehrfachauswahl zeigt Rezepte, die mindestens eine Form erfüllen.',
    options: dietOptions,
  },
  {
    key: 'intolerances',
    param: 'unvertraeglichkeit',
    triggerLabel: 'Unverträglichkeit',
    filterDescription: 'Alle gewählten Angaben müssen zutreffen.',
    options: intoleranceOptions,
  },
  {
    key: 'mealTypes',
    param: 'mahlzeit',
    triggerLabel: 'Mahlzeit',
    options: mealTypeOptions,
  },
  {
    key: 'attributes',
    param: 'eigenschaften',
    triggerLabel: 'Eigenschaften',
    filterDescription: 'Alle gewählten Eigenschaften müssen zutreffen.',
    options: attributeOptions,
  },
  {
    key: 'equipment',
    param: 'ausstattung',
    triggerLabel: 'Ausstattung',
    filterDescription: 'Wähle, was du hast. Es werden nur Rezepte gezeigt, die damit auskommen.',
    options: equipmentOptions,
  },
]

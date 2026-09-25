import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import {
  AMOUNT_MAX,
  COOKING_STEP_MAX_LENGTH,
  DESCRIPTION_MAX_LENGTH,
  IMAGE_MAX_BYTES,
  IMAGE_TYPES,
  INGREDIENT_NAME_MAX_LENGTH,
  MACRO_MAX_GRAMS,
} from './recipes.data'

function requiredNumber(message: string) {
  return z.number({ required_error: message, invalid_type_error: message })
}

const macroMessage = `Gib eine Zahl von 0 bis ${MACRO_MAX_GRAMS} ein, zum Beispiel 12,5.`

const macroSchema = requiredNumber(macroMessage)
  .min(0, macroMessage)
  .max(MACRO_MAX_GRAMS, macroMessage)

const ingredientSchema = z.object({
  name: z
    .string({ required_error: 'Gib einen Namen für die Zutat ein.' })
    .trim()
    .min(1, 'Gib einen Namen für die Zutat ein.')
    .max(
      INGREDIENT_NAME_MAX_LENGTH,
      `Der Name darf höchstens ${INGREDIENT_NAME_MAX_LENGTH} Zeichen lang sein.`,
    ),
  amount: requiredNumber('Gib eine Menge ein.')
    .positive('Gib eine Menge größer als 0 ein.')
    .max(AMOUNT_MAX, 'Die Menge darf höchstens 9.999,9 betragen.'),
  unit: z.string({ required_error: 'Wähle eine Einheit.' }).min(1, 'Wähle eine Einheit.'),
})

const cookingStepSchema = z.object({
  text: z
    .string({ required_error: 'Beschreibe diesen Schritt oder entferne ihn.' })
    .trim()
    .min(1, 'Beschreibe diesen Schritt oder entferne ihn.')
    .max(
      COOKING_STEP_MAX_LENGTH,
      `Der Schritt darf höchstens ${COOKING_STEP_MAX_LENGTH} Zeichen lang sein.`,
    ),
})

/** A string is the URL of the already saved image and needs no check */
const imageSchema = z
  .union([z.instanceof(File), z.string()])
  .nullable()
  .refine(
    (image) => !(image instanceof File) || IMAGE_TYPES.includes(image.type),
    'Dieses Format wird nicht unterstützt. Verwende JPG, PNG oder WebP.',
  )
  .refine(
    (image) => !(image instanceof File) || image.size <= IMAGE_MAX_BYTES,
    'Das Bild ist größer als 5 MB. Wähle eine kleinere Datei.',
  )

export const recipeSchema = toTypedSchema(
  z.object({
    image: imageSchema,

    name: z
      .string({ required_error: 'Gib dem Rezept einen Namen.' })
      .trim()
      .min(1, 'Gib dem Rezept einen Namen.')
      .max(80, 'Der Name darf höchstens 80 Zeichen lang sein.'),

    description: z
      .string()
      .trim()
      .max(
        DESCRIPTION_MAX_LENGTH,
        `Die Beschreibung darf höchstens ${DESCRIPTION_MAX_LENGTH} Zeichen lang sein.`,
      )
      .default(''),

    servings: requiredNumber('Gib eine ganze Zahl von 1 bis 12 ein.')
      .int('Gib eine ganze Zahl von 1 bis 12 ein.')
      .min(1, 'Gib eine ganze Zahl von 1 bis 12 ein.')
      .max(12, 'Gib eine ganze Zahl von 1 bis 12 ein.'),

    durationMinutes: requiredNumber('Gib die Dauer in ganzen Minuten ein, zum Beispiel 45.')
      .int('Gib die Dauer in ganzen Minuten ein, zum Beispiel 45.')
      .min(1, 'Gib die Dauer in ganzen Minuten ein, zum Beispiel 45.')
      .max(600, 'Die Dauer darf höchstens 600 Minuten betragen.'),

    mealTypes: z.array(z.string()).min(1, 'Wähle mindestens eine Mahlzeit.'),
    equipment: z.array(z.string()),
    diets: z.array(z.string()),
    intolerances: z.array(z.string()),
    attributes: z.array(z.string()),

    ingredients: z.array(ingredientSchema).min(1, 'Füge mindestens eine Zutat hinzu.'),
    cookingSteps: z.array(cookingStepSchema).min(1, 'Beschreibe mindestens einen Schritt.'),

    proteinPerServing: macroSchema,
    carbsPerServing: macroSchema,
    fatPerServing: macroSchema,
  }),
)

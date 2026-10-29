import type { IngredientDraft } from '@features/recipes/recipes.types'

import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { INGREDIENT_UNITS, MAX_SERVINGS, MIN_SERVINGS } from '@features/recipes/recipes.constants'
import { isEmptyIngredient, kcalOf } from '@features/recipes/recipes.utils'

const MAX_IMAGE_BYTES = 5 * 1024 * 1024

export const NO_NUTRIENTS_MESSAGE = 'Mindestens ein Nährwert muss größer als 0 sein.'

function macroGrams(label: string) {
	return z
		.number({ message: `${label} fehlt noch. Trag 0 ein, wenn es keins gibt.` })
		.min(0, { message: `${label} kann nicht negativ sein.` })
		.max(500, { message: `Prüf den Wert für ${label} noch mal.` })
}

/** Completely empty rows are allowed and dropped on save. Half-filled ones are not. */
const ingredientSchema = z
	.object({
		name: z.string().max(100, { message: 'Höchstens 100 Zeichen.' }).default(''),
		amount: z.number().optional(),
		unit: z.enum(INGREDIENT_UNITS as [IngredientDraft['unit'], ...IngredientDraft['unit'][]]),
	})
	.superRefine((ingredient, context) => {
		if (isEmptyIngredient(ingredient)) return

		if (!ingredient.name.trim()) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['name'],
				message: 'Wie heißt die Zutat?',
			})
		}

		if (ingredient.amount === undefined) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['amount'],
				message: 'Wie viel brauchst du?',
			})
		} else if (ingredient.amount <= 0 || ingredient.amount > 100000) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['amount'],
				message: 'Gib eine Menge über 0 ein.',
			})
		}
	})

export const recipeSchema = toTypedSchema(
	z
		.object({
			title: z
				.string({ message: 'Gib deinem Rezept einen Titel.' })
				.trim()
				.min(1, { message: 'Gib deinem Rezept einen Titel.' })
				.min(3, { message: 'Der Titel braucht mindestens 3 Zeichen.' })
				.max(80, { message: 'Der Titel darf höchstens 80 Zeichen haben.' }),

			description: z
				.string({ message: 'Beschreib dein Rezept in ein, zwei Sätzen.' })
				.trim()
				.min(1, { message: 'Beschreib dein Rezept in ein, zwei Sätzen.' })
				.max(280, { message: 'Die Beschreibung darf höchstens 280 Zeichen haben.' }),

			image: z
				.union([z.instanceof(File), z.string(), z.null()])
				.default(null)
				.refine(
					(image) =>
						!(image instanceof File) ||
						(image.type.startsWith('image/') && image.size <= MAX_IMAGE_BYTES),
					{ message: 'Wähl ein Bild im Format JPG, PNG oder WebP mit höchstens 5 MB.' },
				),

			servings: z
				.number({ message: 'Für wie viele Portionen ist das Rezept?' })
				.int({ message: 'Gib eine ganze Zahl ein.' })
				.min(MIN_SERVINGS, { message: 'Mindestens 1 Portion.' })
				.max(MAX_SERVINGS, { message: 'Höchstens 12 Portionen.' }),

			durationMinutes: z
				.number({ message: 'Wie lange dauert die Zubereitung?' })
				.int({ message: 'Gib ganze Minuten ein.' })
				.min(1, { message: 'Mindestens 1 Minute.' })
				.max(1440, { message: 'Höchstens 1.440 Minuten, also ein Tag.' }),

			protein: macroGrams('Protein'),
			carbs: macroGrams('Kohlenhydrate'),
			fat: macroGrams('Fett'),

			diet: z.enum(['omnivore', 'pescetarian', 'vegetarian', 'vegan']).default('omnivore'),
			freeFrom: z.array(z.enum(['gluten_free', 'lactose_free'])).default([]),
			equipment: z.array(z.enum(['stove', 'oven', 'mixer', 'airfryer'])).default([]),
			mealTypes: z
				.array(z.enum(['breakfast', 'lunch', 'dinner', 'snack', 'dessert']))
				.min(1, { message: 'Wähl mindestens eine Mahlzeit aus.' }),

			ingredients: z
				.array(ingredientSchema)
				.refine(
					(ingredients) =>
						ingredients.some((ingredient) => !isEmptyIngredient(ingredient)),
					{
						message: 'Füge mindestens eine Zutat hinzu.',
					},
				),

			steps: z
				.array(
					z
						.string()
						.trim()
						.max(1000, { message: 'Höchstens 1.000 Zeichen pro Schritt.' }),
				)
				.refine((steps) => steps.some(Boolean), {
					message: 'Beschreib mindestens einen Schritt.',
				}),
		})
		// Only runs once every field is individually valid
		.superRefine((values, context) => {
			if (kcalOf(values) < 1) {
				context.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['kcal'],
					message: NO_NUTRIENTS_MESSAGE,
				})
			}
		}),
)

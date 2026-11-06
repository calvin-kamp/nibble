import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { kcalFromMacros, minimumKcal } from '@features/tracking/tracking.utils'
import { toIsoDate } from '@shared/utils/date'

function entryDate() {
	return z
		.string({ message: 'Wähl ein Datum aus.' })
		.refine((date) => date <= toIsoDate(), { message: 'Das Datum liegt in der Zukunft.' })
}

export const weightEntrySchema = toTypedSchema(
	z.object({
		date: entryDate(),
		kg: z
			.number({ message: 'Gib dein Gewicht ein.' })
			.min(25, { message: 'Prüf dein Gewicht noch mal.' })
			.max(400, { message: 'Prüf dein Gewicht noch mal.' }),
	}),
)

function grams(message: string) {
	return z
		.number({ message })
		.min(0, { message: 'Der Wert kann nicht negativ sein.' })
		.max(1000, { message: 'Prüf den Wert noch mal.' })
}

/** A food typed in by hand: name and the values of the portion eaten */
const manualFoodSchema = z
	.object({
		name: z
			.string({ message: 'Wie heißt das Lebensmittel?' })
			.trim()
			.min(1, { message: 'Wie heißt das Lebensmittel?' })
			.max(255, { message: 'Höchstens 255 Zeichen.' }),
		protein: grams('Wie viel Eiweiß? Bei keinem trägst du 0 ein.'),
		carbs: grams('Wie viele Kohlenhydrate? Bei keinen trägst du 0 ein.'),
		fat: grams('Wie viel Fett? Bei keinem trägst du 0 ein.'),
		kcal: z
			.number({ message: 'Wie viele Kalorien?' })
			.min(0, { message: 'Der Wert kann nicht negativ sein.' })
			.max(10000, { message: 'Prüf den Wert noch mal.' }),
	})
	.refine((food) => food.kcal >= minimumKcal(food), {
		path: ['kcal'],
		message: 'Das passt nicht zu den Makros. Prüf die Werte noch mal.',
	})

export type ManualFoodValues = z.infer<typeof manualFoodSchema>

/**
 * Checks a hand-typed food inside a larger form and reports its errors under prefix, e.g.
 * "manual.kcal". The kcal message names what the macros give.
 */
export function manualFoodIssues(
	value: unknown,
	prefix: (string | number)[],
	context: z.RefinementCtx,
): void {
	const result = manualFoodSchema.safeParse(value ?? {})

	if (result.success) return

	for (const issue of result.error.issues) {
		const food = (value ?? {}) as Partial<ManualFoodValues>
		const isFit = issue.path[0] === 'kcal' && issue.code === z.ZodIssueCode.custom

		context.addIssue({
			code: z.ZodIssueCode.custom,
			path: [...prefix, ...issue.path],
			message: isFit
				? `Das passt nicht zu den Makros, daraus ergeben sich etwa ${kcalFromMacros({
						protein: food.protein ?? 0,
						carbs: food.carbs ?? 0,
						fat: food.fat ?? 0,
					})} kcal.`
				: issue.message,
		})
	}
}

export type FoodEntrySource = 'product' | 'saved'

// One form for both tabs. Each field is optional on its own; which ones are required depends
// on the tab (source) and is only checked in superRefine.
export const foodEntrySchema = toTypedSchema(
	z
		.object({
			date: entryDate(),
			meal: z.enum(['breakfast', 'lunch', 'dinner', 'snack'], {
				message: 'Wähl eine Mahlzeit aus.',
			}),
			source: z.enum(['product', 'saved']),
			productCode: z.string().optional(),
			amount: z.number().positive({ message: 'Wie viel hast du gegessen?' }).optional(),
			unit: z.enum(['g', 'ml', 'serving', 'package']).optional(),
			savedMealId: z.string().optional(),
			// "Selbst eintragen" in the food tab: name and values instead of a product
			isManual: z.boolean().optional(),
			manual: z.any().optional(),
		})
		// Only runs once every field is individually valid
		.superRefine((values, context) => {
			const issue = (path: string, message: string) =>
				context.addIssue({ code: z.ZodIssueCode.custom, path: [path], message })

			if (values.source === 'saved') {
				if (!values.savedMealId) issue('savedMealId', 'Wähl eine Mahlzeit aus.')

				return
			}

			if (values.isManual) return manualFoodIssues(values.manual, ['manual'], context)

			if (!values.productCode)
				return issue('productCode', 'Such ein Lebensmittel und wähl es aus der Liste.')

			amountIssue(values.amount, values.unit, issue)
		}),
)

// Changing an entry. Amount and unit only exist for foods from the search (hasAmount), name
// and values only for foods typed in (isManual).
export const foodEntryEditSchema = toTypedSchema(
	z
		.object({
			date: entryDate(),
			meal: z.enum(['breakfast', 'lunch', 'dinner', 'snack'], {
				message: 'Wähl eine Mahlzeit aus.',
			}),
			hasAmount: z.boolean(),
			amount: z.number().positive({ message: 'Wie viel hast du gegessen?' }).optional(),
			unit: z.enum(['g', 'ml', 'serving', 'package']).optional(),
			isManual: z.boolean().optional(),
			manual: z.any().optional(),
		})
		.superRefine((values, context) => {
			if (values.isManual) return manualFoodIssues(values.manual, ['manual'], context)
			if (!values.hasAmount) return

			amountIssue(values.amount, values.unit, (path, message) =>
				context.addIssue({ code: z.ZodIssueCode.custom, path: [path], message }),
			)
		}),
)

/** Amount of a food: required and plausible, at most 50 for servings and packages */
export function amountIssue(
	amount: number | undefined,
	unit: string | undefined,
	issue: (path: string, message: string) => void,
): void {
	if (amount === undefined) return issue('amount', 'Wie viel davon?')

	const isCounted = unit === 'serving' || unit === 'package'

	if (amount > (isCounted ? 50 : 5000)) issue('amount', 'Prüf die Menge noch mal.')
}

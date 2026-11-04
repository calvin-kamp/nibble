import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

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
		})
		// Only runs once every field is individually valid
		.superRefine((values, context) => {
			const issue = (path: string, message: string) =>
				context.addIssue({ code: z.ZodIssueCode.custom, path: [path], message })

			if (values.source === 'saved') {
				if (!values.savedMealId) issue('savedMealId', 'Wähl eine Mahlzeit aus.')

				return
			}

			if (!values.productCode)
				return issue('productCode', 'Such ein Lebensmittel und wähl es aus der Liste.')

			amountIssue(values.amount, values.unit, issue)
		}),
)

// Changing an entry. Amount and unit only exist for foods from the search (hasAmount).
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
		})
		.superRefine((values, context) => {
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

import type { FoodProduct } from '@features/tracking/tracking.types'

import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { amountIssue, manualFoodIssues } from '@features/tracking/tracking.schema'

// A product with amount, or an own item: then name and values are checked under "own"
const itemSchema = z
	.object({
		product: z.custom<FoodProduct>().optional(),
		amount: z.number().positive({ message: 'Wie viel davon?' }).optional(),
		unit: z.enum(['g', 'ml', 'serving', 'package']).optional(),
		own: z.any().optional(),
	})
	.superRefine((item, context) => {
		if (!item.product) return manualFoodIssues(item.own, ['own'], context)

		amountIssue(item.amount, item.unit, (path, message) =>
			context.addIssue({ code: z.ZodIssueCode.custom, path: [path], message }),
		)
	})

export const mealSchema = toTypedSchema(
	z.object({
		name: z
			.string({ message: 'Wie soll die Mahlzeit heißen?' })
			.trim()
			.min(1, { message: 'Wie soll die Mahlzeit heißen?' })
			.max(60, { message: 'Höchstens 60 Zeichen.' }),
		items: z.array(itemSchema).min(1, { message: 'Such mindestens ein Lebensmittel aus.' }),
	}),
)

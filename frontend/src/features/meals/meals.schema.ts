import type { FoodProduct } from '@features/tracking/tracking.types'

import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { amountIssue } from '@features/tracking/tracking.schema'

// One item: food from the database with amount and unit
const itemSchema = z
	.object({
		product: z.custom<FoodProduct>(),
		amount: z.number().positive({ message: 'Wie viel davon?' }).optional(),
		unit: z.enum(['g', 'ml', 'serving', 'package']).optional(),
	})
	.superRefine((item, context) =>
		amountIssue(item.amount, item.unit, (path, message) =>
			context.addIssue({ code: z.ZodIssueCode.custom, path: [path], message }),
		),
	)

export const mealSchema = toTypedSchema(
	z.object({
		name: z
			.string({ message: 'Wie soll die Mahlzeit heißen?' })
			.trim()
			.min(1, { message: 'Wie soll die Mahlzeit heißen?' })
			.max(60, { message: 'Höchstens 60 Zeichen.' }),
		note: z.string().trim().max(300, { message: 'Höchstens 300 Zeichen.' }).optional(),
		items: z.array(itemSchema).min(1, { message: 'Such mindestens ein Lebensmittel aus.' }),
	}),
)

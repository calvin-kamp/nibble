import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import {
	MAX_GRAMS_PER_100,
	MAX_KCAL_PER_100,
	MAX_PACKAGE_QUANTITY,
	MAX_REJECTION_REASON_LENGTH,
	MAX_SERVING_QUANTITY,
} from '@features/admin/admin.constants'

export const rejectSchema = toTypedSchema(
	z.object({
		reason: z
			.string({ message: 'Schreib dem Autor, warum das Rezept nicht freigegeben wird.' })
			.trim()
			.min(1, { message: 'Schreib dem Autor, warum das Rezept nicht freigegeben wird.' })
			.max(MAX_REJECTION_REASON_LENGTH, {
				message: `Höchstens ${MAX_REJECTION_REASON_LENGTH} Zeichen.`,
			}),
	}),
)

function requiredAmount(message: string, max: number, unit = 'g') {
	return z
		.number({ message })
		.min(0, { message: 'Der Wert darf nicht negativ sein.' })
		.max(max, { message: `Höchstens ${max.toLocaleString('de-DE')} ${unit}.` })
}

function quantity(max: number) {
	return z
		.number({ message: 'Gib eine Zahl ein.' })
		.positive({ message: 'Die Menge muss größer als 0 sein.' })
		.max(max, { message: `Höchstens ${max.toLocaleString('de-DE')}.` })
		.optional()
}

/** nibble needs energy and the three macros; Open Food Facts accepts a product without the rest */
const nutritionSchema = z
	.object({
		kcal: requiredAmount('Wie viele kcal hat es?', MAX_KCAL_PER_100, 'kcal'),
		fat: requiredAmount('Wie viel Fett?', MAX_GRAMS_PER_100),
		carbs: requiredAmount('Wie viele Kohlenhydrate?', MAX_GRAMS_PER_100),
		protein: requiredAmount('Wie viel Eiweiß?', MAX_GRAMS_PER_100),
	})
	.superRefine((values, context) => {
		// A little slack for rounding on the packaging, as in the backend
		if (values.fat + values.carbs + values.protein > MAX_GRAMS_PER_100 + 5) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['carbs'],
				message: 'Fett, Kohlenhydrate und Eiweiß ergeben mehr als 100 g.',
			})
		}
	})

const countriesSchema = z
	.array(z.enum(['en:germany', 'en:austria', 'en:switzerland']), {
		message: 'Wähl mindestens ein Land.',
	})
	.min(1, { message: 'Wähl mindestens ein Land.' })

/** Countries only for new products with barcode, Open Food Facts needs them there */
export function foodSchema(withCountries: boolean) {
	return toTypedSchema(
		z.object({
			name: z
				.string({ message: 'Wie heißt das Lebensmittel?' })
				.trim()
				.min(1, { message: 'Wie heißt das Lebensmittel?' })
				.max(255, { message: 'Höchstens 255 Zeichen.' }),
			brand: z.string().trim().max(255, { message: 'Höchstens 255 Zeichen.' }).optional(),
			baseUnit: z.enum(['g', 'ml'], { message: 'Gramm oder Milliliter?' }),
			packageQuantity: quantity(MAX_PACKAGE_QUANTITY),
			servingQuantity: quantity(MAX_SERVING_QUANTITY),
			countries: withCountries ? countriesSchema : countriesSchema.optional(),
			nutrition: nutritionSchema,
		}),
	)
}

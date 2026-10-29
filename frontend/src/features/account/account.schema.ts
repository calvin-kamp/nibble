import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { macrosToKcal } from '@features/calorie-calculator/calorie-calculator.utils'
import { MIN_AGE } from '@features/legal/legal.constants'
import { ageOn, toIsoDate } from '@shared/utils/date'

const MIN_MANUAL_KCAL = 1200
const MAX_MANUAL_KCAL = 6000

function macroGrams(label: string) {
	return z
		.number({ message: `${label} fehlt noch.` })
		.min(0, { message: `${label} kann nicht negativ sein.` })
		.max(1000, { message: `Prüf den Wert für ${label} noch mal.` })
}

/**
 * Calories are derived from the macros. Below 1,200 kcal it gets hard to get enough vitamins
 * and minerals, so onboarding does not let that through without a warning.
 * Exported as a raw schema so onboarding uses the same rules as the settings.
 */
export const manualNeedsRules = z
	.object({
		protein: macroGrams('Protein'),
		carbs: macroGrams('Kohlenhydrate'),
		fat: macroGrams('Fett'),
	})
	.superRefine((macros, context) => {
		const kcal: number = macrosToKcal(macros)

		if (kcal < MIN_MANUAL_KCAL) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['kcal'],
				message:
					'Das sind weniger als 1.200 kcal am Tag. So wenig solltest du nur mit ärztlicher ' +
					'Begleitung essen. Prüf deine Werte oder nutz den Rechner.',
			})
		}

		if (kcal > MAX_MANUAL_KCAL) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['kcal'],
				message: 'Das sind mehr als 6.000 kcal am Tag. Prüf deine Werte noch mal.',
			})
		}
	})

const MIN_PASSWORD_LENGTH = 8

const currentPassword = z
	.string({ message: 'Gib dein Passwort ein.' })
	.min(1, { message: 'Gib dein Passwort ein.' })

export const emailChangeSchema = toTypedSchema(
	z.object({
		email: z
			.string({ message: 'Gib die neue E-Mail-Adresse ein.' })
			.trim()
			.min(1, { message: 'Gib die neue E-Mail-Adresse ein.' })
			.email({ message: 'Gib eine E-Mail-Adresse ein, zum Beispiel name@example.com.' }),
		password: currentPassword,
	}),
)

export const passwordChangeSchema = toTypedSchema(
	z
		.object({
			currentPassword,
			newPassword: z
				.string({ message: 'Lege ein neues Passwort fest.' })
				.min(MIN_PASSWORD_LENGTH, {
					message: `Dein Passwort braucht mindestens ${MIN_PASSWORD_LENGTH} Zeichen.`,
				})
				.max(128, { message: 'Dein Passwort darf höchstens 128 Zeichen haben.' }),
			newPasswordConfirmation: z
				.string({ message: 'Wiederhole das neue Passwort.' })
				.min(1, { message: 'Wiederhole das neue Passwort.' }),
		})
		.refine((values) => values.newPassword === values.newPasswordConfirmation, {
			path: ['newPasswordConfirmation'],
			message: 'Die Passwörter stimmen nicht überein.',
		}),
)

/** Same rules as in onboarding, plus the goal */
export const nutritionSchema = toTypedSchema(
	z.intersection(
		manualNeedsRules,
		z.object({
			goal: z.enum(['diet', 'maintain', 'gain'], { message: 'Bitte wähl dein Ziel aus.' }),
		}),
	),
)

export const deleteAccountSchema = toTypedSchema(
	z.object({
		password: currentPassword,
	}),
)

export const consentSchema = toTypedSchema(
	z.object({
		consent: z.literal(true, {
			errorMap: () => ({ message: 'Setz den Haken, um einzuwilligen.' }),
		}),
	}),
)

// All details in one form; each one is optional, so a single one can be saved on its own. The
// limits match the calorie calculator, otherwise it could not calculate with these details.
// Also the base of the body data step in onboarding.
export const personalFields = z.object({
	birthDate: z
		.string()
		.refine((date) => date <= toIsoDate(), { message: 'Das Datum liegt in der Zukunft.' })
		.refine((date) => (ageOn(date) ?? 0) >= MIN_AGE, {
			message: `Du musst mindestens ${MIN_AGE} Jahre alt sein.`,
		})
		.refine((date) => (ageOn(date) ?? 0) <= 120, { message: 'Prüf das Datum noch mal.' })
		.optional(),
	heightCm: z
		.number()
		.min(120, { message: 'Prüf deine Größe noch mal.' })
		.max(250, { message: 'Prüf deine Größe noch mal.' })
		.optional(),
	sex: z.enum(['male', 'female']).optional(),
})

export const personalSchema = toTypedSchema(personalFields)

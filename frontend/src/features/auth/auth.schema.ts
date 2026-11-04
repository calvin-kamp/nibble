import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { MIN_AGE } from '@features/legal/legal.constants'

const MIN_PASSWORD_LENGTH = 8

const email = z
	.string({ message: 'Gib deine E-Mail-Adresse ein.' })
	.trim()
	.min(1, { message: 'Gib deine E-Mail-Adresse ein.' })
	.email({ message: 'Gib eine E-Mail-Adresse ein, zum Beispiel name@example.com.' })

export const loginSchema = toTypedSchema(
	z.object({
		email,
		password: z
			.string({ message: 'Gib dein Passwort ein.' })
			.min(1, { message: 'Gib dein Passwort ein.' }),
	}),
)

const newPasswordFields = {
	password: z
		.string({ message: 'Lege ein Passwort fest.' })
		.min(MIN_PASSWORD_LENGTH, {
			message: `Dein Passwort braucht mindestens ${MIN_PASSWORD_LENGTH} Zeichen.`,
		})
		.max(128, { message: 'Dein Passwort darf höchstens 128 Zeichen haben.' }),
	passwordConfirmation: z
		.string({ message: 'Wiederhole dein Passwort.' })
		.min(1, { message: 'Wiederhole dein Passwort.' }),
}

const passwordsMatch = {
	check: (values: { password: string; passwordConfirmation: string }) =>
		values.password === values.passwordConfirmation,
	issue: { path: ['passwordConfirmation'], message: 'Die Passwörter stimmen nicht überein.' },
}

export const registerSchema = toTypedSchema(
	z
		.object({
			email,
			...newPasswordFields,
			terms: z.literal(true, {
				errorMap: () => ({
					message: `Setz den Haken, wenn du mindestens ${MIN_AGE} Jahre alt bist und die AGB akzeptierst.`,
				}),
			}),
		})
		.refine(passwordsMatch.check, passwordsMatch.issue),
)

export const passwordForgotSchema = toTypedSchema(z.object({ email }))

export const passwordResetSchema = toTypedSchema(
	z.object(newPasswordFields).refine(passwordsMatch.check, passwordsMatch.issue),
)

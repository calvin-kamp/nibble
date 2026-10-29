import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { manualNeedsRules, personalFields } from '@features/account/account.schema'
import { USERNAME_PATTERN } from '@features/onboarding/onboarding.constants'

export const usernameSchema = toTypedSchema(
	z.object({
		username: z
			.string({ message: 'Benutzername fehlt noch.' })
			.trim()
			.min(1, { message: 'Benutzername fehlt noch.' })
			.regex(USERNAME_PATTERN, {
				message:
					'Der Benutzername darf 3 bis 20 Zeichen haben: Buchstaben, Zahlen und Unterstrich.',
			}),
		// UsernameStep checks via the API on submit whether the name is still available
	}),
)

// Everything optional: the step can be left half filled or skipped. Weight has the
// calculator's limits.
export const bodyDataSchema = toTypedSchema(
	personalFields.extend({
		weightKg: z
			.number()
			.min(25, { message: 'Prüf dein Gewicht noch mal.' })
			.max(400, { message: 'Prüf dein Gewicht noch mal.' })
			.optional(),
	}),
)

// Declining is fine. The age confirmation is part of the consent text.
export const consentSchema = toTypedSchema(
	z.object({
		consent: z.boolean().default(false),
	}),
)

// Optional like the body data: without a choice the goal stays open for the settings
export const goalSchema = toTypedSchema(
	z.object({
		goal: z.enum(['diet', 'maintain', 'gain']).optional(),
	}),
)

// Without a choice, the daily needs are set later
export const needsMethodSchema = toTypedSchema(
	z.object({
		method: z.enum(['calculate', 'manual', 'later']).optional(),
	}),
)

export const manualNeedsSchema = toTypedSchema(manualNeedsRules)

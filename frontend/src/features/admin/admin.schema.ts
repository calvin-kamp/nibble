import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import { MAX_REJECTION_REASON_LENGTH } from '@features/admin/admin.constants'

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

import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

const emailSchema = z
  .string({ required_error: 'E-Mail-Adresse eingeben' })
  .trim()
  .min(1, 'E-Mail-Adresse eingeben')
  .email('Gültige E-Mail-Adresse eingeben, z. B. name@beispiel.de')

export const passwordSchema = z
  .string({ required_error: 'Passwort eingeben' })
  .min(1, 'Passwort eingeben')
  .min(8, 'Passwort mit mindestens 8 Zeichen wählen')

export const loginSchema = toTypedSchema(
  z.object({
    email: emailSchema,
    password: z.string({ required_error: 'Passwort eingeben' }).min(1, 'Passwort eingeben'),
  }),
)

export const registerSchema = toTypedSchema(
  z
    .object({
      email: emailSchema,
      password: passwordSchema,
      passwordConfirm: z
        .string({ required_error: 'Passwort wiederholen' })
        .min(1, 'Passwort wiederholen'),
      tosAccepted: z
        .boolean()
        .refine((value) => value, 'AGB akzeptieren, um das Konto zu erstellen'),
    })

    .refine((values) => values.password === values.passwordConfirm, {
      message: 'Gleiches Passwort wie oben eingeben',
      path: ['passwordConfirm'],
    }),
)

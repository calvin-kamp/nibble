import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

const workoutSchema = z.object({
  met: z.string().default(''),
  duration: z.number().min(0).max(600).default(0),
  frequency: z.number().min(0).max(7).default(0),
})

export const calorieCalculatorSchema = toTypedSchema(
  z.object({
    sex: z.enum(['male', 'female']),

    age: z
      .number({ message: 'Bitte gib dein Alter an.' })
      .min(14, { message: 'Der Rechner gilt ab 14 Jahren.' })
      .max(120, { message: 'Prüf dein Alter noch mal.' }),

    height: z
      .number({ message: 'Bitte gib deine Größe an.' })
      .min(120, { message: 'Prüf deine Größe noch mal.' })
      .max(250, { message: 'Prüf deine Größe noch mal.' }),

    weight: z
      .number({ message: 'Bitte gib dein Gewicht an.' })
      .min(25, { message: 'Prüf dein Gewicht noch mal.' })
      .max(400, { message: 'Prüf dein Gewicht noch mal.' }),

    steps: z
      .number({ message: 'Bitte gib deine Schritte an.' })
      .min(0)
      .max(50000, { message: 'Höchstens 50.000 Schritte pro Tag.' }),

    exercises: z.array(workoutSchema).default([]),

    goal: z.enum(['diet', 'maintain', 'gain']),
  }),
)

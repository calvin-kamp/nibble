import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

import {
	ADULT_AGE,
	MAX_WEEKLY_TRAINING_MINUTES,
	MAX_WORKOUT_MINUTES,
	UNDERWEIGHT_BMI,
} from './calorie-calculator.constants'
import { MIN_AGE } from '@features/legal/legal.constants'

/**
 * A workout is either empty or complete. A chosen sport without duration or frequency would
 * otherwise be skipped silently, and the user would believe it had been counted.
 */
const workoutSchema = z
	.object({
		met: z.string().default(''),
		duration: z
			.number()
			.min(0)
			.max(MAX_WORKOUT_MINUTES, { message: 'Höchstens 5 Stunden pro Einheit.' })
			.default(0),
		frequency: z.number().min(0).max(7, { message: 'Höchstens 7 Mal pro Woche.' }).default(0),
	})
	.superRefine((workout, context) => {
		const hasSport: boolean = workout.met !== ''

		if (!hasSport && (workout.duration > 0 || workout.frequency > 0)) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['met'],
				message: 'Wähl eine Sportart aus oder entferne das Training.',
			})
		}

		if (hasSport && workout.duration <= 0) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['duration'],
				message: 'Wie lange dauert eine Einheit?',
			})
		}

		if (hasSport && workout.frequency <= 0) {
			context.addIssue({
				code: z.ZodIssueCode.custom,
				path: ['frequency'],
				message: 'Wie oft trainierst du pro Woche?',
			})
		}
	})

/**
 * Safety rules on top of the plausibility ranges:
 *
 * - No deficit below a BMI of 18.5. Losing weight from there is a health risk, and a
 *   calculator that hands out a diet target anyway can reinforce an eating disorder.
 * - No deficit for minors. Growth raises energy needs, and the equation is not validated
 *   for them.
 * - A cap on weekly training, so a typo such as 600 instead of 60 minutes cannot inflate the
 *   target to several thousand calories.
 *
 * These checks run once all fields are individually valid.
 */
export const calorieCalculatorSchema = toTypedSchema(
	z
		.object({
			sex: z.enum(['male', 'female'], { message: 'Bitte wähl dein Geschlecht aus.' }),

			age: z
				.number({ message: 'Bitte gib dein Alter an.' })
				.min(MIN_AGE, { message: `Der Rechner gilt ab ${MIN_AGE} Jahren.` })
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

			exercises: z.array(workoutSchema),

			goal: z.enum(['diet', 'maintain', 'gain'], { message: 'Bitte wähl dein Ziel aus.' }),
		})
		.superRefine((values, context) => {
			const bmi: number = values.weight / (values.height / 100) ** 2

			if (values.goal === 'diet' && values.age < ADULT_AGE) {
				context.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['goal'],
					message:
						'Unter 18 rechnen wir kein Defizit aus, weil dein Körper noch wächst. ' +
						'Wenn du abnehmen möchtest, sprich bitte mit deiner Kinder- oder Hausarztpraxis.',
				})
			} else if (values.goal === 'diet' && bmi < UNDERWEIGHT_BMI) {
				context.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['goal'],
					message:
						'Bei deiner Größe und deinem Gewicht raten wir vom Abnehmen ab. ' +
						'Wenn du trotzdem abnehmen möchtest, sprich bitte vorher mit einer Ärztin oder einem Arzt.',
				})
			}

			const weeklyMinutes: number = values.exercises.reduce(
				(total, workout) => total + workout.duration * workout.frequency,
				0,
			)

			if (weeklyMinutes > MAX_WEEKLY_TRAINING_MINUTES) {
				context.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['exercises'],
					message: 'Mehr als 20 Stunden Training pro Woche? Prüf deine Angaben noch mal.',
				})
			}
		}),
)

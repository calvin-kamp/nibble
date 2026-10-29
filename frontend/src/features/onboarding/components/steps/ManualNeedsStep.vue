<script setup lang="ts">
import type { DailyNeeds } from '@features/onboarding/onboarding.types'

import { useForm } from 'vee-validate'
import { computed } from 'vue'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'

import { KCAL_PER_GRAM } from '@features/calorie-calculator/calorie-calculator.constants'
import { macrosToKcal } from '@features/calorie-calculator/calorie-calculator.utils'
import { manualNeedsSchema } from '@features/onboarding/onboarding.schema'
import { focusFirstError, NumberField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

interface Props {
	needs?: DailyNeeds
}

const props = withDefaults(defineProps<Props>(), {
	needs: undefined,
})

const emit = defineEmits<{
	next: [needs: DailyNeeds]
	back: []
}>()

const { handleSubmit, values, errors } = useForm({
	validationSchema: manualNeedsSchema,
	initialValues: {
		protein: props.needs?.protein,
		carbs: props.needs?.carbs,
		fat: props.needs?.fat,
	},
})

// Read-only: derived from the three macros
const kcal = computed<number | null>(() => {
	const { protein, carbs, fat } = values

	if (protein === undefined || carbs === undefined || fat === undefined) return null

	const total = macrosToKcal({ protein, carbs, fat })

	return total > 0 ? total : null
})

const distribution = computed<string>(() => {
	if (!kcal.value) return 'Trag Protein, Kohlenhydrate und Fett ein.'

	const share = (grams: number, kcalPerGram: number) =>
		Math.round(((grams * kcalPerGram) / kcal.value!) * 100)

	return (
		`Verteilung: Protein ${share(values.protein!, KCAL_PER_GRAM.protein)} %, ` +
		`Kohlenhydrate ${share(values.carbs!, KCAL_PER_GRAM.carbs)} %, ` +
		`Fett ${share(values.fat!, KCAL_PER_GRAM.fat)} %.`
	)
})

// The calorie total error is not attached to an input but to the "kcal" path
const kcalError = computed<string | undefined>(
	() => (errors.value as Record<string, string | undefined>).kcal,
)

const onSubmit = handleSubmit(
	(macros) =>
		emit('next', {
			kcal: Math.round(macrosToKcal(macros)),
			protein: Math.round(macros.protein),
			carbs: Math.round(macros.carbs),
			fat: Math.round(macros.fat),
			source: 'manual',
		}),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Trag deine Werte ein"
		lead="Die Kalorien ergeben sich aus den Makros: Protein und Kohlenhydrate haben 4 kcal pro Gramm, Fett 9 kcal pro Gramm."
		@submit="onSubmit"
	>
		<!-- Total above the macros, as in the settings. output: screen readers announce the new
         value whenever a macro changes. -->
		<div class="flex flex-col gap-1">
			<p class="flex flex-wrap items-baseline gap-x-2">
				<output
					aria-label="Kalorien pro Tag"
					class="font-display text-4xl font-extrabold tracking-tighter tabular-nums"
				>
					{{ kcal ? formatNumber(Math.round(kcal)) : '–' }}
				</output>

				<span class="font-semibold text-ink-soft">kcal pro Tag</span>
			</p>

			<p class="text-sm text-muted">{{ distribution }}</p>

			<p
				v-if="kcalError"
				class="text-sm font-semibold text-danger"
				role="alert"
			>
				{{ kcalError }}
			</p>
		</div>

		<div class="grid grid-cols-12 gap-5">
			<NumberField
				class="col-span-12 md:col-span-4"
				name="protein"
				label="Protein"
				unit="g"
				:min="0"
			/>

			<NumberField
				class="col-span-12 md:col-span-4"
				name="carbs"
				label="Kohlenhydrate"
				unit="g"
				:min="0"
			/>

			<NumberField
				class="col-span-12 md:col-span-4"
				name="fat"
				label="Fett"
				unit="g"
				:min="0"
			/>
		</div>

		<OnboardingNav @back="emit('back')" />
	</OnboardingStep>
</template>

<script setup lang="ts">
import type { NutritionSettings } from '@features/account/account.types'

import { useForm } from 'vee-validate'
import { computed, onMounted, ref } from 'vue'

import { BaseActions, BaseButton } from '@shared/ui'

import { nutritionSchema } from '@features/account/account.schema'
import { GOAL_OPTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { macrosToKcal } from '@features/calorie-calculator/calorie-calculator.utils'
import { focusFirstError, NumberField, RadioField } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

// Set daily needs manually. Calories are derived from the macros, as in onboarding.
interface Props {
	/** null until daily needs have been saved */
	settings?: NutritionSettings | null
	submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	settings: null,
	submitting: false,
})

const emit = defineEmits<{
	save: [settings: NutritionSettings]
	cancel: []
}>()

const { handleSubmit, values, errors } = useForm({
	validationSchema: nutritionSchema,
	initialValues: {
		protein: props.settings?.needs.protein,
		carbs: props.settings?.needs.carbs,
		fat: props.settings?.needs.fat,
		goal: props.settings?.goal ?? undefined,
	},
})

const kcal = computed<number>(() =>
	Math.round(
		macrosToKcal({
			protein: values.protein ?? 0,
			carbs: values.carbs ?? 0,
			fat: values.fat ?? 0,
		}),
	),
)

// The calorie error is not attached to an input but to the "kcal" path
const kcalError = computed<string | undefined>(
	() => (errors.value as Record<string, string | undefined>).kcal,
)

// The form replaces the button, so focus moves to the first field
const form = ref<HTMLFormElement | null>(null)

onMounted(() => form.value?.querySelector<HTMLElement>('input')?.focus())

const onSubmit = handleSubmit(
	({ protein, carbs, fat, goal }) =>
		emit('save', {
			goal,
			needs: {
				kcal: Math.round(macrosToKcal({ protein, carbs, fat })),
				protein,
				carbs,
				fat,
				source: 'manual',
			},
		}),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<form
		ref="form"
		class="flex flex-col gap-5"
		novalidate
		@submit="onSubmit"
	>
		<p class="text-muted">
			Protein und Kohlenhydrate haben 4 kcal pro Gramm, Fett 9 kcal pro Gramm. Das ersetzt den
			Wert aus dem Rechner.
		</p>

		<div class="flex flex-col gap-2">
			<!-- output: screen readers announce the new value whenever a macro changes -->
			<p class="flex flex-wrap items-baseline gap-x-2">
				<output
					aria-label="Kalorien pro Tag"
					class="font-display text-4xl font-extrabold tracking-tighter tabular-nums"
				>
					{{ kcal ? formatNumber(kcal) : '–' }}
				</output>

				<span class="font-semibold text-ink-soft">kcal pro Tag</span>
			</p>

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
				class="col-span-12 sm:col-span-4"
				name="protein"
				label="Protein"
				unit="g"
				:min="0"
			/>

			<NumberField
				class="col-span-12 sm:col-span-4"
				name="carbs"
				label="Kohlenhydrate"
				unit="g"
				:min="0"
			/>

			<NumberField
				class="col-span-12 sm:col-span-4"
				name="fat"
				label="Fett"
				unit="g"
				:min="0"
			/>
		</div>

		<RadioField
			name="goal"
			label="Dein Ziel"
			orientation="horizontal"
			:options="GOAL_OPTIONS"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="props.submitting"
				>Speichern</BaseButton
			>

			<BaseButton
				variant="ghost"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>

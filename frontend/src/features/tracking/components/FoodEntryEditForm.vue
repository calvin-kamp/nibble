<script setup lang="ts">
import type { FoodEntry, FoodUnit, Nutrition } from '@features/tracking/tracking.types'
import type { FieldOption } from '@shared/forms/types'

import { useForm } from 'vee-validate'
import { computed, ref, watch } from 'vue'

import NutritionFacts from '@features/tracking/components/NutritionFacts.vue'
import { BaseActions, BaseButton } from '@shared/ui'

import { updateFoodEntry } from '@features/tracking/tracking.api'
import { MEAL_LABELS, MEAL_ORDER } from '@features/tracking/tracking.constants'
import { foodEntryEditSchema } from '@features/tracking/tracking.schema'
import {
	formatUnitOption,
	nutritionFor,
	toQuantity,
	unitsOf,
} from '@features/tracking/tracking.utils'
import { DateField, focusFirstError, NumberField, SelectField } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

interface Props {
	entry: FoodEntry
}

const props = defineProps<Props>()

const emit = defineEmits<{
	saved: [entry: FoodEntry]
	cancel: []
}>()

const MEAL_OPTIONS: FieldOption[] = MEAL_ORDER.map((meal) => ({
	value: meal,
	label: MEAL_LABELS[meal],
}))

const today = toIsoDate()

// Saved meals are stored as one portion with fixed totals: only day and meal can change.
const product = props.entry.product

const { handleSubmit, isSubmitting, values, setFieldValue } = useForm({
	validationSchema: foodEntryEditSchema,
	initialValues: {
		date: props.entry.date,
		meal: props.entry.meal,
		hasAmount: Boolean(product && props.entry.quantity),
		amount: props.entry.quantity?.value,
		unit: props.entry.quantity?.unit,
	},
})

const unitOptions = computed<FieldOption[]>(() =>
	product
		? unitsOf(product).map((value) => ({ value, label: formatUnitOption(product, value) }))
		: [],
)

// A different unit starts with its own suggestion, otherwise 80 g would become 80 servings
watch(
	() => values.unit,
	(next, previous) => {
		if (next && previous && next !== previous)
			setFieldValue('amount', next === 'serving' || next === 'package' ? 1 : 100)
	},
)

const nutrition = computed<Nutrition | null>(() => {
	if (!product || !values.amount || !values.unit) return null

	return nutritionFor(product, toQuantity(product, values.amount, values.unit as FoodUnit).base)
})

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async (formValues) => {
		submitError.value = null

		try {
			emit(
				'saved',
				await updateFoodEntry(props.entry, {
					date: formValues.date,
					meal: formValues.meal,
					...(formValues.hasAmount
						? { amount: formValues.amount, unit: formValues.unit }
						: {}),
				}),
			)
		} catch {
			submitError.value =
				'Der Eintrag konnte nicht gespeichert werden. Versuch es bitte noch einmal.'
		}
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<form
		class="flex flex-col gap-7"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-5">
			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<div class="grid grid-cols-12 gap-4">
				<SelectField
					class="col-span-12 sm:col-span-6"
					name="meal"
					label="Mahlzeit"
					:options="MEAL_OPTIONS"
				/>

				<DateField
					class="col-span-12 sm:col-span-6"
					name="date"
					label="Datum"
					:max="today"
				/>
			</div>

			<template v-if="values.hasAmount">
				<div class="grid grid-cols-12 gap-4">
					<NumberField
						class="col-span-5"
						name="amount"
						label="Menge"
						:min="0"
						:step="0.1"
					/>

					<SelectField
						class="col-span-7"
						name="unit"
						label="Einheit"
						:options="unitOptions"
					/>
				</div>

				<NutritionFacts
					class="py-4 border-y border-divider"
					:nutrition="nutrition"
					aria-live="polite"
				/>
			</template>

			<p
				v-else
				class="text-md text-muted-foreground"
			>
				Eine gespeicherte Mahlzeit zählt als Ganzes. Andere Mengen trägst du über die
				Lebensmittel ein.
			</p>
		</div>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
			>
				Speichern
			</BaseButton>

			<BaseButton
				variant="outline"
				@click="emit('cancel')"
			>
				Abbrechen
			</BaseButton>
		</BaseActions>
	</form>
</template>

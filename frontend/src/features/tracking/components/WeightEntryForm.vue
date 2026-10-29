<script setup lang="ts">
import type { WeightEntry } from '@features/tracking/tracking.types'

import { useForm } from 'vee-validate'
import { ref } from 'vue'

import { BaseActions, BaseButton } from '@shared/ui'

import { saveWeightEntry } from '@features/tracking/tracking.api'
import { weightEntrySchema } from '@features/tracking/tracking.schema'
import { DateField, focusFirstError, NumberField } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

interface Props {
	/** Prefill, defaults to today */
	date?: string
}

const props = withDefaults(defineProps<Props>(), {
	date: undefined,
})

const emit = defineEmits<{
	saved: [entry: WeightEntry]
	cancel: []
}>()

const today = toIsoDate()

const { handleSubmit, isSubmitting } = useForm({
	validationSchema: weightEntrySchema,
	initialValues: { date: props.date ?? today },
})

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async (values) => {
		submitError.value = null

		try {
			emit('saved', await saveWeightEntry(values))
		} catch {
			submitError.value =
				'Das Gewicht konnte nicht gespeichert werden. Versuch es bitte noch einmal.'
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

			<NumberField
				name="kg"
				label="Gewicht"
				unit="kg"
				:step="0.1"
				:format-options="{ minimumFractionDigits: 1, maximumFractionDigits: 1 }"
			/>

			<DateField
				name="date"
				label="Datum"
				hint="Gibt es für den Tag schon einen Wert, wird er ersetzt."
				:max="today"
			/>
		</div>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Speichern</BaseButton
			>

			<BaseButton
				variant="outline"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>

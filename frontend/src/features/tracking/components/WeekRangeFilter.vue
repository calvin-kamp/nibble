<script setup lang="ts">
import type { WeekRange } from '@features/tracking/composables/week-history'

import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import { z } from 'zod'

import { BaseActions, BaseButton } from '@shared/ui'

import { DateField, focusFirstError } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

interface Props {
	range: WeekRange | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
	change: [range: WeekRange | null]
}>()

const today = toIsoDate()

function day(message: string) {
	return z
		.string({ message })
		.refine((date) => date <= today, { message: 'Das Datum liegt in der Zukunft.' })
}

const schema = toTypedSchema(
	z
		.object({ from: day('Wähl den ersten Tag aus.'), to: day('Wähl den letzten Tag aus.') })
		.refine((values) => values.to >= values.from, {
			path: ['to'],
			message: 'Der letzte Tag liegt vor dem ersten.',
		}),
)

const { handleSubmit } = useForm({
	validationSchema: schema,
	initialValues: { from: props.range?.from, to: props.range?.to },
})

const onSubmit = handleSubmit(
	(values) => emit('change', { from: values.from, to: values.to }),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<!-- Phones: one field per row and full-width buttons. From tablet on the fields side by side.
		One button stays in their row, level with the inputs even when an error shows below them.
		Two buttons go below as actions like everywhere else, so the dates keep room. -->
	<form
		class="flex flex-col gap-4 md:flex-row md:flex-wrap md:items-start"
		novalidate
		aria-label="Zeitraum wählen"
		@submit="onSubmit"
	>
		<DateField
			class="md:flex-1 md:min-w-0"
			name="from"
			label="Von"
			:max="today"
		/>

		<DateField
			class="md:flex-1 md:min-w-0"
			name="to"
			label="Bis"
			:max="today"
		/>

		<BaseActions
			v-if="props.range"
			class="md:basis-full"
		>
			<BaseButton type="submit">
				Zeitraum anzeigen
			</BaseButton>

			<BaseButton
				variant="outline"
				@click="emit('change', null)"
			>
				Zeitraum aufheben
			</BaseButton>
		</BaseActions>

		<div
			v-else
			class="flex flex-col md:gap-2 md:shrink-0"
		>
			<!-- Takes the place of a label, so the button starts where the inputs do -->
			<span
				class="hidden md:block field__label invisible"
				aria-hidden="true"
			>
				Zeitraum
			</span>

			<BaseButton
				class="md:min-h-12"
				type="submit"
			>
				Zeitraum anzeigen
			</BaseButton>
		</div>
	</form>
</template>

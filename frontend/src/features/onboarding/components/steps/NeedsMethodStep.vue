<script setup lang="ts">
import type { NeedsMethod } from '@features/onboarding/onboarding.types'
import type { FieldOption } from '@shared/forms/types'

import { useForm } from 'vee-validate'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'

import { needsMethodSchema } from '@features/onboarding/onboarding.schema'
import { focusFirstError, RadioField } from '@shared/forms'

interface Props {
	method?: NeedsMethod
}

const props = withDefaults(defineProps<Props>(), {
	method: undefined,
})

const emit = defineEmits<{
	next: [method: NeedsMethod]
	back: []
}>()

const METHOD_OPTIONS: FieldOption[] = [
	{
		value: 'calculate',
		label: 'Für mich berechnen',
		description: 'Wir fragen nach deiner Bewegung und, falls noch nicht angegeben, nach Größe und Gewicht.',
	},
	{
		value: 'manual',
		label: 'Ich kenne meine Werte',
		description:
			'Du trägst Protein, Kohlenhydrate und Fett ein oder nur deine Kalorien, wir teilen sie auf.',
	},
	{
		value: 'later',
		label: 'Später festlegen',
		description:
			'Geht jederzeit in den Einstellungen. Bis dahin zeigt deine Übersicht keinen Tagesbedarf.',
	},
]

const { handleSubmit } = useForm({
	validationSchema: needsMethodSchema,
	initialValues: { method: props.method },
})

const onSubmit = handleSubmit(
	(values) => emit('next', values.method ?? 'later'),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Wie legen wir deinen Tagesbedarf fest?"
		lead="Daraus berechnet deine Übersicht, wie viel du heute noch essen kannst."
		@submit="onSubmit"
	>
		<RadioField
			name="method"
			label="So legen wir deinen Tagesbedarf fest"
			label-hidden
			:options="METHOD_OPTIONS"
		/>

		<OnboardingNav @back="emit('back')" />
	</OnboardingStep>
</template>

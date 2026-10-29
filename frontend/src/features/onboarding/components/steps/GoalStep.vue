<script setup lang="ts">
import type { Goal } from '@features/calorie-calculator/calorie-calculator.types'

import { useForm } from 'vee-validate'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'

import { GOAL_OPTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { goalSchema } from '@features/onboarding/onboarding.schema'
import { focusFirstError, RadioField } from '@shared/forms'

interface Props {
	goal?: Goal
}

const props = withDefaults(defineProps<Props>(), {
	goal: undefined,
})

const emit = defineEmits<{
	/** undefined without a choice: the goal is set later in the settings */
	next: [goal: Goal | undefined]
	back: []
}>()

const { handleSubmit } = useForm({
	validationSchema: goalSchema,
	initialValues: { goal: props.goal },
})

const onSubmit = handleSubmit(
	(values) => emit('next', values.goal),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Was ist dein Ziel?"
		lead="Das ist nur die Richtung. Wenn du dich noch nicht festlegen möchtest, geh einfach weiter: Du kannst es jederzeit in den Einstellungen ändern."
		optional
		@submit="onSubmit"
	>
		<RadioField
			name="goal"
			label="Dein Ziel"
			label-hidden
			:options="GOAL_OPTIONS"
		/>

		<OnboardingNav @back="emit('back')" />
	</OnboardingStep>
</template>

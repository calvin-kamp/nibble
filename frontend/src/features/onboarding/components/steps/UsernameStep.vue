<script setup lang="ts">
import { useForm } from 'vee-validate'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'

import { usernameSchema } from '@features/onboarding/onboarding.schema'
import { focusFirstError, TextField } from '@shared/forms'

interface Props {
	username: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
	next: [username: string]
}>()

const { handleSubmit } = useForm({
	validationSchema: usernameSchema,
	initialValues: { username: props.username },
})

const onSubmit = handleSubmit(
	(values) => emit('next', values.username),
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<OnboardingStep
		title="Wie sollen wir dich nennen?"
		lead="So sprechen wir dich in nibble an. Andere Nutzer sehen deinen Benutzernamen nicht, nur die Moderation, wenn du ein Rezept einreichst. Du kannst ihn später in den Einstellungen ändern."
		@submit="onSubmit"
	>
		<TextField
			name="username"
			label="Benutzername"
			hint="3 bis 20 Zeichen: Buchstaben (auch Umlaute und ß), Zahlen und Unterstrich."
			autocomplete="username"
		/>

		<OnboardingNav :show-back="false" />
	</OnboardingStep>
</template>

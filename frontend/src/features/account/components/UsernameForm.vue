<script setup lang="ts">
import { useForm } from 'vee-validate'

import { BaseActions, BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { updateUsername } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import { usernameSchema } from '@features/onboarding/onboarding.schema'
import { ApiError } from '@shared/api/client'
import { focusFirstError, TextField } from '@shared/forms'

const emit = defineEmits<{
	done: []
	cancel: []
}>()

const auth = useAuthStore()
const toast = useToast()

const { handleSubmit, isSubmitting, setFieldError } = useForm({
	validationSchema: usernameSchema,
	initialValues: { username: auth.user?.username ?? '' },
})

const onSubmit = handleSubmit(
	async ({ username }, { evt }) => {
		try {
			auth.setUser(await updateUsername(username))
			toast.show('Benutzername gespeichert')
			emit('done')
		} catch (error) {
			if (error instanceof ApiError && error.code === 'username_taken') {
				setFieldError('username', 'Dieser Benutzername ist schon vergeben.')
				focusFirstError(evt)
			} else {
				toast.show('Der Benutzername konnte nicht gespeichert werden.', 'danger')
			}
		}
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<form
		class="flex flex-col gap-5"
		novalidate
		@submit="onSubmit"
	>
		<TextField
			name="username"
			label="Benutzername"
			hint="3 bis 20 Zeichen: Buchstaben, Zahlen und Unterstrich. Andere Nutzer sehen ihn nicht, nur die Moderation bei eingereichten Rezepten."
			autocomplete="username"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
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

<script setup lang="ts">
import { useForm } from 'vee-validate'

import { BaseActions, BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { updateUsername } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import { usernameSchema } from '@features/onboarding/onboarding.schema'
import { focusFirstError, TextField } from '@shared/forms'

const emit = defineEmits<{
	done: []
	cancel: []
}>()

const auth = useAuthStore()
const toast = useToast()

const { handleSubmit, isSubmitting } = useForm({
	validationSchema: usernameSchema,
	initialValues: { username: auth.user?.username ?? '' },
})

const onSubmit = handleSubmit(
	async ({ username }) => {
		try {
			auth.setUser(await updateUsername(username))
			toast.show('Benutzername gespeichert')
			emit('done')
		} catch {
			toast.show('Der Benutzername konnte nicht gespeichert werden.', 'danger')
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
			hint="3 bis 20 Zeichen: Buchstaben (auch Umlaute und ß), Zahlen und Unterstrich. Andere Nutzer sehen ihn nicht, nur die Moderation bei eingereichten Rezepten."
			autocomplete="username"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
			>
				Speichern
			</BaseButton>

			<BaseButton
				variant="ghost"
				@click="emit('cancel')"
			>
				Abbrechen
			</BaseButton>
		</BaseActions>
	</form>
</template>

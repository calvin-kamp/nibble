<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'

import { BaseActions, BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { changePassword } from '@features/account/account.api'
import { passwordChangeSchema } from '@features/account/account.schema'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField } from '@shared/forms'

const emit = defineEmits<{
	done: []
	cancel: []
}>()

const toast = useToast()

const { handleSubmit, isSubmitting, setFieldError } = useForm({
	validationSchema: passwordChangeSchema,
})

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async ({ currentPassword, newPassword }, { evt }) => {
		submitError.value = null

		try {
			await changePassword(currentPassword, newPassword)
			toast.show('Passwort geändert')
			emit('done')
		} catch (error) {
			if (error instanceof ApiError && error.hasFieldError('current_password')) {
				setFieldError('currentPassword', 'Das aktuelle Passwort stimmt nicht.')
				focusFirstError(evt)
			} else {
				submitError.value =
					'Das Passwort konnte nicht geändert werden. Versuch es bitte noch einmal.'
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
		<p
			v-if="submitError"
			class="notice notice--danger"
			role="alert"
		>
			{{ submitError }}
		</p>

		<PasswordField
			name="currentPassword"
			label="Aktuelles Passwort"
			autocomplete="current-password"
		/>

		<PasswordField
			name="newPassword"
			label="Neues Passwort"
			hint="Mindestens 8 Zeichen."
			autocomplete="new-password"
		/>

		<PasswordField
			name="newPasswordConfirmation"
			label="Neues Passwort wiederholen"
			autocomplete="new-password"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Passwort ändern</BaseButton
			>

			<BaseButton
				variant="ghost"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>

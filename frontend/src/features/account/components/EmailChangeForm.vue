<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'

import { BaseActions, BaseButton } from '@shared/ui'

import { changeEmail } from '@features/account/account.api'
import { emailChangeSchema } from '@features/account/account.schema'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField, TextField } from '@shared/forms'

const emit = defineEmits<{
	/** The confirmation email is on its way; the new address only applies after the click */
	done: [email: string]
	cancel: []
}>()

const { handleSubmit, isSubmitting, setFieldError } = useForm({
	validationSchema: emailChangeSchema,
})

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async ({ email, password }, { evt }) => {
		submitError.value = null

		try {
			await changeEmail(email, password)
			emit('done', email)
		} catch (error) {
			if (error instanceof ApiError && error.hasFieldError('password')) {
				setFieldError('password', 'Das Passwort stimmt nicht.')
				focusFirstError(evt)
			} else if (error instanceof ApiError && error.hasFieldError('email')) {
				// Already taken, or already the account's own address; the backend says which
				setFieldError('email', error.fieldErrors.email)
				focusFirstError(evt)
			} else {
				submitError.value =
					'Die E-Mail-Adresse konnte nicht geändert werden. Versuch es bitte noch einmal.'
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

		<TextField
			name="email"
			label="Neue E-Mail-Adresse"
			type="email"
			autocomplete="email"
			inputmode="email"
		/>

		<PasswordField
			name="password"
			label="Passwort zur Bestätigung"
			autocomplete="current-password"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Bestätigungslink senden</BaseButton
			>

			<BaseButton
				variant="ghost"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>

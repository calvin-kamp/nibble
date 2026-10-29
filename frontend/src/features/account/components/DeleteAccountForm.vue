<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'

import { BaseActions, BaseButton } from '@shared/ui'

import { requestAccountDeletion } from '@features/account/account.api'
import { deleteAccountSchema } from '@features/account/account.schema'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField } from '@shared/forms'

const emit = defineEmits<{
	/** Time at which the account is permanently deleted (ISO) */
	deleted: [scheduledFor: string]
	cancel: []
}>()

const { handleSubmit, isSubmitting, setFieldError } = useForm({
	validationSchema: deleteAccountSchema,
})

const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async ({ password }, { evt }) => {
		submitError.value = null

		try {
			emit('deleted', await requestAccountDeletion(password))
		} catch (error) {
			if (error instanceof ApiError && error.hasFieldError('password')) {
				setFieldError('password', 'Das Passwort stimmt nicht.')
				focusFirstError(evt)
			} else {
				submitError.value =
					'Das Konto konnte nicht gelöscht werden. Versuch es bitte noch einmal.'
			}
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

			<PasswordField
				name="password"
				label="Passwort zur Bestätigung"
				autocomplete="current-password"
			/>
		</div>

		<BaseActions>
			<BaseButton
				type="submit"
				variant="danger"
				:disabled="isSubmitting"
				>Löschung beantragen</BaseButton
			>

			<BaseButton
				variant="outline"
				@click="emit('cancel')"
				>Abbrechen</BaseButton
			>
		</BaseActions>
	</form>
</template>

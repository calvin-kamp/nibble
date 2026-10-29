<script setup lang="ts">
import { useForm } from 'vee-validate'

import { BaseActions, BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { updateDataConsent } from '@features/account/account.api'
import { consentSchema } from '@features/account/account.schema'
import { useAuthStore } from '@features/auth/auth.store'
import { CONSENT_LABEL } from '@features/legal/legal.constants'
import { CheckboxField, focusFirstError } from '@shared/forms'

const auth = useAuthStore()
const toast = useToast()

const { handleSubmit, isSubmitting } = useForm({ validationSchema: consentSchema })

const onSubmit = handleSubmit(
	async () => {
		try {
			auth.setUser(await updateDataConsent(true))
			toast.show('Danke! Das Tracking ist eingeschaltet.')
		} catch {
			toast.show('Die Einwilligung konnte nicht gespeichert werden.', 'danger')
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
		<CheckboxField
			name="consent"
			:label="CONSENT_LABEL"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Einwilligen</BaseButton
			>
		</BaseActions>
	</form>
</template>

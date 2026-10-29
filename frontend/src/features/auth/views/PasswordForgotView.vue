<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'

import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseButton, BaseLink } from '@shared/ui'

import { requestPasswordReset } from '@features/auth/auth.api'
import { passwordForgotSchema } from '@features/auth/auth.schema'
import { ApiError } from '@shared/api/client'
import { focusFirstError, TextField } from '@shared/forms'

const { handleSubmit, isSubmitting } = useForm({ validationSchema: passwordForgotSchema })

// The API answers the same way for unknown addresses, so the page cannot reveal who has an account
const sentTo = ref<string | null>(null)
const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async ({ email }) => {
		submitError.value = null

		try {
			await requestPasswordReset(email)
			sentTo.value = email
		} catch (error) {
			submitError.value =
				error instanceof ApiError && error.status === 429
					? 'Zu viele Versuche. Warte bitte eine Weile und versuch es dann noch einmal.'
					: 'Die E-Mail konnte nicht verschickt werden. Versuch es bitte noch einmal.'
		}
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<AuthLayout
		title="Passwort vergessen"
		lead="Wir schicken dir einen Link, mit dem du ein neues Passwort festlegst."
	>
		<p
			v-if="sentTo"
			class="notice notice--info"
			role="status"
		>
			Falls es zu {{ sentTo }} ein Konto gibt, ist der Link unterwegs. Er ist eine Stunde
			gültig.
		</p>

		<form
			v-else
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
				label="E-Mail"
				type="email"
				autocomplete="email"
				inputmode="email"
			/>

			<BaseButton
				type="submit"
				class="w-full"
				:disabled="isSubmitting"
			>
				Link anfordern
			</BaseButton>
		</form>

		<p class="pt-5 border-t border-divider text-ink-soft">
			Doch wieder eingefallen?

			<BaseLink
				route-name="auth-login"
				variant="inline"
			>
				Anmelden
			</BaseLink>
		</p>
	</AuthLayout>
</template>

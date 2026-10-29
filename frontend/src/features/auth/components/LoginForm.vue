<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { BaseButton, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { login } from '@features/auth/auth.api'
import { loginSchema } from '@features/auth/auth.schema'
import { useAuthStore } from '@features/auth/auth.store'
import { redirectTarget } from '@features/auth/auth.utils'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField, TextField } from '@shared/forms'
import { formatLongDate } from '@shared/utils/date'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const { handleSubmit, isSubmitting } = useForm({ validationSchema: loginSchema })

// API error, e.g. wrong password. Not tied to a single field.
const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async (values) => {
		submitError.value = null

		try {
			const user = await login(values)

			auth.signIn(user)

			// A requested deletion does not block signing in; it can be cancelled from the account
			if (user.deletionScheduledFor) {
				toast.show(
					`Dein Konto wird am ${formatLongDate(new Date(user.deletionScheduledFor))} gelöscht. Unter Konto › Konto löschen kannst du das abbrechen.`,
					'info',
				)
			} else {
				toast.show('Schön, dass du wieder da bist.')
			}

			// Back to the page the user came from, e.g. after the session expired
			await router.push(redirectTarget(route.query) ?? { name: 'dashboard' })
		} catch (error) {
			submitError.value =
				error instanceof ApiError && error.status === 429
					? 'Zu viele Versuche. Warte bitte eine Minute und versuch es dann noch einmal.'
					: 'E-Mail-Adresse oder Passwort stimmen nicht. Prüf deine Angaben.'
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
			label="E-Mail"
			type="email"
			autocomplete="email"
			inputmode="email"
		/>

		<div class="flex flex-col gap-3">
			<PasswordField
				name="password"
				label="Passwort"
				autocomplete="current-password"
			/>

			<BaseLink
				route-name="auth-password-forgot"
				class="self-start"
				>Passwort vergessen?</BaseLink
			>
		</div>

		<BaseButton
			type="submit"
			class="w-full"
			:disabled="isSubmitting"
		>
			Anmelden
		</BaseButton>
	</form>
</template>

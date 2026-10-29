<script setup lang="ts">
import { useForm } from 'vee-validate'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { BaseButton, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { register } from '@features/auth/auth.api'
import { registerSchema } from '@features/auth/auth.schema'
import { useAuthStore } from '@features/auth/auth.store'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField, TextField } from '@shared/forms'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const { handleSubmit, isSubmitting } = useForm({ validationSchema: registerSchema })

// API error, e.g. email address already registered
const submitError = ref<string | null>(null)

const onSubmit = handleSubmit(
	async ({ email, password }) => {
		submitError.value = null

		try {
			auth.signIn(await register({ email, password }))
			toast.show(
				'Dein Konto ist erstellt. Wir haben dir eine E-Mail zum Bestätigen geschickt.',
			)
			await router.push({ name: 'onboarding' })
		} catch (error) {
			if (error instanceof ApiError && error.code === 'email_taken') {
				submitError.value =
					'Zu dieser E-Mail-Adresse gibt es schon ein Konto. Melde dich an.'
			} else if (error instanceof ApiError && error.hasFieldError('password')) {
				submitError.value =
					'Dein Passwort ist zu leicht zu erraten. Wähl bitte ein anderes.'
			} else {
				submitError.value =
					'Das Konto konnte nicht erstellt werden. Versuch es bitte noch einmal.'
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
			label="E-Mail"
			type="email"
			autocomplete="email"
			inputmode="email"
		/>

		<PasswordField
			name="password"
			label="Passwort"
			hint="Mindestens 8 Zeichen."
			autocomplete="new-password"
		/>

		<PasswordField
			name="passwordConfirmation"
			label="Passwort wiederholen"
			autocomplete="new-password"
		/>

		<p class="text-sm text-muted">
			Mit dem Erstellen deines Kontos gelten unsere
			<BaseLink
				route-name="legal-tos"
				variant="inline"
				>AGB</BaseLink
			>
			. Wie wir mit deinen Daten umgehen, steht in der
			<BaseLink
				route-name="legal-privacy"
				variant="inline"
				>Datenschutzerklärung</BaseLink
			>.
		</p>

		<BaseButton
			type="submit"
			class="w-full"
			:disabled="isSubmitting"
		>
			Konto erstellen
		</BaseButton>
	</form>
</template>

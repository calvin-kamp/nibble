<script setup lang="ts">
import { useForm } from 'vee-validate'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseButton, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { resetPassword } from '@features/auth/auth.api'
import { passwordResetSchema } from '@features/auth/auth.schema'
import { useAuthStore } from '@features/auth/auth.store'
import { ApiError } from '@shared/api/client'
import { focusFirstError, PasswordField } from '@shared/forms'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

// Link from the reset email, e.g. /reset-password?token=...
const token = computed<string | null>(() =>
	typeof route.query.token === 'string' ? route.query.token : null,
)

const { handleSubmit, isSubmitting } = useForm({ validationSchema: passwordResetSchema })

const submitError = ref<string | null>(null)
const linkInvalid = ref<boolean>(false)

const onSubmit = handleSubmit(
	async ({ password }) => {
		if (!token.value) return

		submitError.value = null

		try {
			await resetPassword(token.value, password)

			// The reset ends every session, including one on this device
			auth.signOut()
			toast.show('Dein Passwort ist geändert. Melde dich jetzt damit an.')
			await router.push({ name: 'auth-login' })
		} catch (error) {
			if (error instanceof ApiError && error.hasFieldError('new_password')) {
				submitError.value =
					'Dein Passwort ist zu leicht zu erraten. Wähl bitte ein anderes.'
			} else if (error instanceof ApiError && error.code === 'invalid_token') {
				linkInvalid.value = true
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
	<AuthLayout title="Neues Passwort">
		<template v-if="!token || linkInvalid">
			<p
				class="notice notice--danger"
				role="alert"
			>
				Der Link ist ungültig oder abgelaufen.
			</p>

			<BaseButton
				route-name="auth-password-forgot"
				class="w-full"
			>
				Neuen Link anfordern
			</BaseButton>
		</template>

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

			<PasswordField
				name="password"
				label="Neues Passwort"
				hint="Mindestens 8 Zeichen."
				autocomplete="new-password"
			/>

			<PasswordField
				name="passwordConfirmation"
				label="Passwort wiederholen"
				autocomplete="new-password"
			/>

			<BaseButton
				type="submit"
				class="w-full"
				:disabled="isSubmitting"
			>
				Passwort speichern
			</BaseButton>
		</form>

		<p class="pt-5 border-t border-divider text-ink-soft">
			<BaseLink
				route-name="auth-login"
				variant="inline"
			>
				Zurück zur Anmeldung
			</BaseLink>
		</p>
	</AuthLayout>
</template>

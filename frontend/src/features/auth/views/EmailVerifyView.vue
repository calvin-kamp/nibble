<script setup lang="ts">
import type { VerifyState } from '@features/auth/auth.types'

import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseButton, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { resendVerificationEmail, verifyEmail } from '@features/auth/auth.api'
import { useAuthStore } from '@features/auth/auth.store'

const route = useRoute()
const auth = useAuthStore()
const toast = useToast()

const state = ref<VerifyState>('pending')
const isResending = ref<boolean>(false)

// Link from the confirmation email, e.g. /verify-email?token=...
onMounted(async () => {
	const { token } = route.query

	if (typeof token !== 'string') {
		state.value = 'failed'

		return
	}

	try {
		await verifyEmail(token)
		state.value = 'verified'

		// The link also works without being signed in, e.g. on a phone. Then there is nothing to reload.
		if (auth.isLoggedIn) await auth.refreshUser()
	} catch {
		state.value = 'failed'
	}
})

async function onResend(): Promise<void> {
	isResending.value = true

	try {
		await resendVerificationEmail()
		toast.show('Wir haben dir eine neue E-Mail geschickt.')
	} catch {
		toast.show(
			'Die E-Mail konnte nicht verschickt werden. Versuch es später noch einmal.',
			'danger',
		)
	} finally {
		isResending.value = false
	}
}
</script>

<template>
	<AuthLayout title="E-Mail bestätigen">
		<p
			v-if="state === 'pending'"
			aria-live="polite"
		>
			Einen Moment, wir prüfen deinen Link …
		</p>

		<template v-else-if="state === 'verified'">
			<p
				class="notice notice--info"
				role="status"
			>
				Deine E-Mail-Adresse ist bestätigt. Danke!
			</p>

			<BaseButton
				:route-name="auth.isLoggedIn ? 'dashboard' : 'auth-login'"
				class="w-full"
			>
				{{ auth.isLoggedIn ? 'Zur Übersicht' : 'Anmelden' }}
			</BaseButton>
		</template>

		<template v-else>
			<p
				class="notice notice--danger"
				role="alert"
			>
				Der Link ist ungültig oder abgelaufen.
			</p>

			<BaseButton
				v-if="auth.isLoggedIn && !auth.isEmailVerified"
				class="w-full"
				:disabled="isResending"
				@click="onResend"
			>
				Neuen Link schicken
			</BaseButton>

			<p v-else-if="!auth.isLoggedIn">
				<BaseLink route-name="auth-login">Melde dich an</BaseLink>, um dir einen neuen Link
				schicken zu lassen.
			</p>
		</template>
	</AuthLayout>
</template>

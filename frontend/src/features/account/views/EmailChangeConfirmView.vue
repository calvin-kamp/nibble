<script setup lang="ts">
import type { EmailChangeState } from '@features/account/account.types'

import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseButton, BaseLink } from '@shared/ui'

import { confirmEmailChange } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import { ApiError } from '@shared/api/client'

const route = useRoute()
const auth = useAuthStore()

const state = ref<EmailChangeState>('pending')

// Link from the email to the new address, e.g. /email-aendern?token=...
onMounted(async () => {
	const { token } = route.query

	if (typeof token !== 'string') {
		state.value = 'failed'

		return
	}

	try {
		await confirmEmailChange(token)
		state.value = 'changed'

		// The link also works without being signed in, e.g. on a phone. Then there is nothing to reload.
		if (auth.isLoggedIn) await auth.refreshUser()
	} catch (error) {
		state.value = error instanceof ApiError && error.code === 'email_taken' ? 'taken' : 'failed'
	}
})
</script>

<template>
	<AuthLayout title="E-Mail-Adresse ändern">
		<p
			v-if="state === 'pending'"
			aria-live="polite"
		>
			Einen Moment, wir prüfen deinen Link …
		</p>

		<template v-else-if="state === 'changed'">
			<p
				class="notice notice--info"
				role="status"
			>
				Deine neue E-Mail-Adresse ist gespeichert. Ab jetzt meldest du dich damit an.
			</p>

			<BaseButton
				:route-name="auth.isLoggedIn ? 'account-profile' : 'auth-login'"
				class="w-full"
			>
				{{ auth.isLoggedIn ? 'Zu den Einstellungen' : 'Anmelden' }}
			</BaseButton>
		</template>

		<template v-else>
			<p
				class="notice notice--danger"
				role="alert"
			>
				{{
					state === 'taken'
						? 'Zu dieser E-Mail-Adresse gibt es inzwischen ein anderes Konto. Deine bisherige Adresse bleibt.'
						: 'Der Link ist ungültig oder abgelaufen. Deine bisherige Adresse bleibt.'
				}}
			</p>

			<p>
				In den
				<BaseLink route-name="account-profile">Einstellungen</BaseLink> kannst du die
				Änderung noch einmal anfordern.
			</p>
		</template>
	</AuthLayout>
</template>

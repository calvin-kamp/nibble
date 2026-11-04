<script setup lang="ts">
import { ref } from 'vue'

import AccountPanel from '@features/account/components/AccountPanel.vue'
import AccountSettingRow from '@features/account/components/AccountSettingRow.vue'
import EmailChangeForm from '@features/account/components/EmailChangeForm.vue'
import PasswordChangeForm from '@features/account/components/PasswordChangeForm.vue'
import UsernameForm from '@features/account/components/UsernameForm.vue'
import { BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { resendVerificationEmail } from '@features/auth/auth.api'
import { useAuthStore } from '@features/auth/auth.store'
import { ApiError } from '@shared/api/client'

const auth = useAuthStore()
const toast = useToast()

const isResending = ref<boolean>(false)

async function onResend(): Promise<void> {
	isResending.value = true

	try {
		await resendVerificationEmail()
		toast.show(`Wir haben dir eine neue E-Mail an ${auth.user?.email} geschickt.`)
	} catch (error) {
		if (error instanceof ApiError && error.code === 'already_verified') {
			// Confirmed in another tab in the meantime: the notice disappears
			await auth.refreshUser().catch(() => {})
			toast.show('Deine E-Mail-Adresse ist schon bestätigt.')
		} else if (error instanceof ApiError && error.status === 429) {
			toast.show(
				'Du hast schon mehrere E-Mails angefordert. Versuch es in einer Stunde noch einmal.',
				'danger',
			)
		} else {
			toast.show(
				'Die E-Mail konnte nicht verschickt werden. Versuch es später noch einmal.',
				'danger',
			)
		}
	} finally {
		isResending.value = false
	}
}

function onEmailChangeRequested(email: string, close: () => void): void {
	toast.show(
		`Wir haben dir einen Link an ${email} geschickt. Bis du ihn öffnest, bleibt deine bisherige Adresse.`,
	)
	close()
}
</script>

<template>
	<AccountPanel title="Anmeldedaten">
		<AccountSettingRow
			label="Benutzername"
			:value="auth.user?.username ?? 'Noch keiner'"
		>
			<template #default="{ close }">
				<UsernameForm
					@done="close"
					@cancel="close"
				/>
			</template>
		</AccountSettingRow>

		<AccountSettingRow
			label="E-Mail-Adresse"
			:value="auth.user?.email ?? '–'"
		>
			<template #default="{ close }">
				<EmailChangeForm
					@done="(email) => onEmailChangeRequested(email, close)"
					@cancel="close"
				/>
			</template>

			<template
				v-if="auth.user && !auth.user.isEmailVerified"
				#status
			>
				<div
					class="notice notice--info flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
					role="status"
				>
					<p>
						Noch nicht bestätigt. Öffne den Link aus unserer E-Mail.
					</p>

					<BaseButton
						class="shrink-0"
						variant="outline"
						size="sm"
						:disabled="isResending"
						@click="onResend"
					>
						E-Mail erneut senden
					</BaseButton>
				</div>
			</template>
		</AccountSettingRow>

		<AccountSettingRow label="Passwort">
			<template #value>
				<span aria-hidden="true">
					••••••••••
				</span>

				<span class="sr-only">
					Gesetzt
				</span>
			</template>

			<template #default="{ close }">
				<PasswordChangeForm
					@done="close"
					@cancel="close"
				/>
			</template>
		</AccountSettingRow>
	</AccountPanel>
</template>

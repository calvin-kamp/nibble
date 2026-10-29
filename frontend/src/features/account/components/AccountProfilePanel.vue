<script setup lang="ts">
import AccountPanel from '@features/account/components/AccountPanel.vue'
import AccountSettingRow from '@features/account/components/AccountSettingRow.vue'
import EmailChangeForm from '@features/account/components/EmailChangeForm.vue'
import PasswordChangeForm from '@features/account/components/PasswordChangeForm.vue'
import UsernameForm from '@features/account/components/UsernameForm.vue'

import { useToast } from '@shared/composables/toast'

import { useAuthStore } from '@features/auth/auth.store'

const auth = useAuthStore()
const toast = useToast()

// Nothing changes until the link is opened, so the row keeps showing the current address
function onEmailChangeRequested(email: string, close: () => void): void {
	toast.show(
		`Wir haben dir einen Link an ${email} geschickt. Bis du ihn öffnest, bleibt deine bisherige Adresse.`,
	)
	close()
}
</script>

<template>
	<AccountPanel title="Konto">
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
				<p
					class="notice notice--info"
					role="status"
				>
					Noch nicht bestätigt. Öffne den Link aus unserer E-Mail.
				</p>
			</template>
		</AccountSettingRow>

		<AccountSettingRow label="Passwort">
			<template #value>
				<span aria-hidden="true">••••••••••</span>

				<span class="sr-only">Gesetzt</span>
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

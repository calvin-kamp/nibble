<script setup lang="ts">
import { DownloadIcon, TrashIcon } from '@lucide/vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import AccountPanel from '@features/account/components/AccountPanel.vue'
import DeleteAccountForm from '@features/account/components/DeleteAccountForm.vue'
import { BaseActions, BaseButton, BaseDialog, BaseIcon } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { cancelAccountDeletion, exportData } from '@features/account/account.api'
import { logout } from '@features/auth/auth.api'
import { useAuthStore } from '@features/auth/auth.store'
import { formatLongDate } from '@shared/utils/date'
import { downloadBlob } from '@shared/utils/download'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const dialogOpen = ref<boolean>(false)

async function onExport(): Promise<void> {
	try {
		downloadBlob(await exportData(), 'nibble-daten.json')
	} catch {
		toast.show('Der Export hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
	}
}

const scheduledFor = computed<string | null>(() => {
	const value = auth.user?.deletionScheduledFor

	return value ? formatLongDate(new Date(value)) : null
})

async function onDeleted(date: string): Promise<void> {
	dialogOpen.value = false

	try {
		await logout()
	} catch {}

	auth.signOut()

	toast.show(
		`Dein Konto wird am ${formatLongDate(new Date(date))} gelöscht. Meld dich bis dahin an, um es dir anders zu überlegen.`,
		'info',
	)

	await router.push({ name: 'home' })
}

const cancelling = ref<boolean>(false)

async function onCancelDeletion(): Promise<void> {
	cancelling.value = true

	try {
		auth.setUser(await cancelAccountDeletion())

		toast.show('Die Löschung ist abgebrochen. Schön, dass du bleibst.')
	} catch {
		toast.show(
			'Die Löschung konnte nicht abgebrochen werden. Versuch es bitte noch einmal.',
			'danger',
		)
	} finally {
		cancelling.value = false
	}
}
</script>

<template>
	<AccountPanel title="Konto löschen">
		<section
			v-if="scheduledFor"
			class="flex flex-col gap-5 p-4 border-2 md:p-5 border-destructive-border rounded-lg bg-destructive-soft/50"
			aria-labelledby="account-delete-scheduled-title"
		>
			<div class="flex flex-col gap-1">
				<h3
					id="account-delete-scheduled-title"
					class="font-sans text-lg font-bold tracking-normal text-destructive"
				>
					Löschung beantragt
				</h3>

				<p class="text-destructive-soft-foreground">
					Dein Konto wird am {{ scheduledFor }} endgültig gelöscht. Bis dahin kannst du es
					dir anders überlegen.
				</p>
			</div>

			<BaseActions>
				<BaseButton
					:disabled="cancelling"
					@click="onCancelDeletion"
				>
					Löschung abbrechen
				</BaseButton>

				<BaseButton
					variant="outline"
					@click="onExport"
				>
					<BaseIcon :icon="DownloadIcon" />

					Daten herunterladen
				</BaseButton>
			</BaseActions>
		</section>

		<section
			v-else
			class="flex flex-col gap-5 p-4 border-2 md:p-5 border-destructive-border rounded-lg bg-destructive-soft/50"
			aria-labelledby="account-delete-title"
		>
			<div class="flex flex-col gap-1">
				<h3
					id="account-delete-title"
					class="font-sans text-lg font-bold tracking-normal text-destructive"
				>
					Alle Daten entfernen
				</h3>

				<p class="text-destructive-soft-foreground">
					Wir löschen dein Konto, deine gespeicherten und noch nicht freigegebenen Rezepte
					und alle Tracking-Daten. Freigegebene Rezepte bleiben ohne deinen Namen. Die
					Löschung passiert erst nach 7 Tagen: Bis dahin kannst du dich anmelden und sie
					hier abbrechen, danach ist alles endgültig weg. Lad deine Daten vorher herunter,
					wenn du sie behalten willst.
				</p>
			</div>

			<BaseActions>
				<BaseButton
					variant="danger"
					@click="dialogOpen = true"
				>
					<BaseIcon :icon="TrashIcon" />

					Konto löschen
				</BaseButton>

				<BaseButton
					variant="outline"
					@click="onExport"
				>
					<BaseIcon :icon="DownloadIcon" />

					Daten herunterladen
				</BaseButton>
			</BaseActions>
		</section>

		<BaseDialog
			v-model:open="dialogOpen"
			title="Konto löschen?"
			description="Gib zur Sicherheit dein Passwort ein. In 7 Tagen sind alle Daten weg, bis dahin kannst du die Löschung nach dem Anmelden abbrechen."
		>
			<DeleteAccountForm
				@deleted="onDeleted"
				@cancel="dialogOpen = false"
			/>
		</BaseDialog>
	</AccountPanel>
</template>

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

// The backend deletes after 7 days. Until then the deletion can be cancelled after signing in.
const scheduledFor = computed<string | null>(() => {
	const value = auth.user?.deletionScheduledFor

	return value ? formatLongDate(new Date(value)) : null
})

async function onDeleted(date: string): Promise<void> {
	dialogOpen.value = false

	try {
		await logout()
	} catch {
		// Deletion has been requested, but the user is still signed out here
	}

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
			class="flex flex-col gap-5 p-4 border-2 md:p-5 border-danger-line rounded-lg bg-danger-subtle"
			aria-labelledby="account-delete-scheduled-title"
		>
			<div class="flex flex-col gap-1">
				<h3
					id="account-delete-scheduled-title"
					class="font-sans text-lg font-bold tracking-normal text-danger"
				>
					Löschung beantragt
				</h3>

				<p class="text-danger-strong">
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

		<!-- Separate, red-bordered area: something is lost irreversibly here -->
		<section
			v-else
			class="flex flex-col gap-5 p-4 border-2 md:p-5 border-danger-line rounded-lg bg-danger-subtle"
			aria-labelledby="account-delete-title"
		>
			<div class="flex flex-col gap-1">
				<h3
					id="account-delete-title"
					class="font-sans text-lg font-bold tracking-normal text-danger"
				>
					Alle Daten entfernen
				</h3>

				<p class="text-danger-strong">
					Wir löschen dein Konto, deine gespeicherten und noch nicht freigegebenen Rezepte
					und alle Tracking-Daten. Freigegebene Rezepte bleiben ohne deinen Namen. Nach 7
					Tagen lässt sich das nicht mehr rückgängig machen. Lad deine Daten vorher
					herunter, wenn du sie behalten willst.
				</p>
			</div>

			<!-- Primary action first: on top on phones, on the right from tablet up -->
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

		<!-- A dialog instead of a plain confirmation: the password confirms it is really the user -->
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

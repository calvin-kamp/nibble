<script setup lang="ts">
import { CircleCheckIcon, CircleSlashIcon, DownloadIcon } from '@lucide/vue'
import { computed, ref } from 'vue'

import AccountPanel from '@features/account/components/AccountPanel.vue'
import AccountSection from '@features/account/components/AccountSection.vue'
import ConsentForm from '@features/account/components/ConsentForm.vue'
import { BaseAlertDialog, BaseButton, BaseIcon, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { exportData, updateDataConsent } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import { formatLongDate } from '@shared/utils/date'
import { downloadBlob } from '@shared/utils/download'

const auth = useAuthStore()
const toast = useToast()

// When consent was last given or revoked. Without a date, the user never consented.
const changedAt = computed<{ iso: string; label: string } | null>(() => {
	const value = auth.user?.dataConsentChangedAt

	return value ? { iso: value, label: formatLongDate(new Date(value)) } : null
})

const revokeOpen = ref<boolean>(false)

// Revoking is as easy as consenting: one button and one confirmation
async function revoke(): Promise<void> {
	try {
		auth.setUser(await updateDataConsent(false))
		toast.show('Einwilligung widerrufen. Das Tracking ist ausgeschaltet.', 'info')
	} catch {
		toast.show('Der Widerruf hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
	}
}

const exporting = ref<boolean>(false)

async function onExport(): Promise<void> {
	exporting.value = true

	try {
		downloadBlob(await exportData(), 'nibble-daten.json')
	} catch {
		toast.show('Der Export hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
	} finally {
		exporting.value = false
	}
}
</script>

<template>
	<AccountPanel title="Datenschutz">
		<AccountSection
			title="Einwilligung ins Tracking"
			description="Mit dieser Einwilligung speichern wir deine Gesundheitsdaten: Gewicht, Körperdaten, Tagebuch, eigene Mahlzeiten und Kalorienbedarf. Ohne sie bleiben dir Rezepte und Rechner."
		>
			<p
				class="flex flex-wrap items-center gap-x-3 gap-y-2"
				role="status"
			>
				<span
					class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold"
					:class="
						auth.hasDataConsent
							? 'bg-brand-soft text-brand-ink'
							: 'bg-surface-muted text-ink-soft'
					"
				>
					<BaseIcon
						:icon="auth.hasDataConsent ? CircleCheckIcon : CircleSlashIcon"
						:size="16"
					/>
					{{
						auth.hasDataConsent
							? 'Eingewilligt'
							: changedAt
								? 'Widerrufen'
								: 'Nicht eingewilligt'
					}}
				</span>

				<span
					v-if="changedAt"
					class="text-ink-soft"
				>
					am <time :datetime="changedAt.iso">{{ changedAt.label }}</time>
				</span>
			</p>

			<template v-if="auth.hasDataConsent">
				<p class="text-sm text-muted">
					Was wir speichern und wie lange, steht in der
					<BaseLink
						route-name="legal-privacy"
						variant="inline"
						>Datenschutzerklärung</BaseLink
					>.
				</p>

				<BaseButton
					class="self-start"
					variant="outline"
					@click="revokeOpen = true"
				>
					Einwilligung widerrufen
				</BaseButton>
			</template>

			<template v-else>
				<p class="notice notice--info">
					Das Tracking ist ausgeschaltet. Übersicht, Tagebuch und eigene Mahlzeiten sind
					dadurch nicht nutzbar.
				</p>

				<ConsentForm />
			</template>
		</AccountSection>

		<AccountSection
			title="Datenexport"
			description="Du bekommst eine JSON-Datei mit allen Daten zu deinem Konto: Konto- und Profildaten, Einwilligungsverlauf, Körperdaten, Ziele, Gewichts- und Tagebucheinträge, eigene Mahlzeiten mit Notizen, deine Rezepte und Einreichungen mit Ablehnungsgründen sowie deine Merkliste."
		>
			<BaseButton
				class="self-start"
				variant="outline"
				:disabled="exporting"
				@click="onExport"
			>
				<BaseIcon :icon="DownloadIcon" />
				Meine Daten herunterladen
			</BaseButton>
		</AccountSection>

		<BaseAlertDialog
			v-model:open="revokeOpen"
			title="Einwilligung widerrufen?"
			description="Wir löschen sofort und endgültig dein Gewicht, deine Körperdaten, deine Einträge, eigene Mahlzeiten mit Notizen und deinen Tagesbedarf. Tagebuch und eigene Mahlzeiten sind dann nicht nutzbar. Du kannst jederzeit wieder einwilligen, die gelöschten Daten kommen aber nicht zurück."
			confirm-label="Widerrufen"
			cancel-label="Abbrechen"
			variant="danger"
			@confirm="revoke"
		/>
	</AccountPanel>
</template>

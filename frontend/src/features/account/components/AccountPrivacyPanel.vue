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
import { OPERATOR } from '@features/legal/legal.constants'
import { formatLongDate } from '@shared/utils/date'
import { downloadBlob } from '@shared/utils/download'

const auth = useAuthStore()
const toast = useToast()

const changedAt = computed<{ iso: string; label: string } | null>(() => {
	const value = auth.user?.dataConsentChangedAt

	return value ? { iso: value, label: formatLongDate(new Date(value)) } : null
})

const revokeOpen = ref<boolean>(false)

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
			title="Einwilligung Gesundheitsdaten"
			description="Mit dieser Einwilligung speichern wir deine Gesundheitsdaten: Gewicht, Körperdaten, Tagebuch, eigene Mahlzeiten und Kalorienbedarf. Ohne sie bleiben dir Rezepte und Rechner."
		>
			<p
				class="flex flex-wrap items-center gap-x-3 gap-y-2"
				role="status"
			>
				<span
					class="tag"
					:class="auth.hasDataConsent ? 'tag--accent' : ''"
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
					class="text-foreground/80"
				>
					am <time :datetime="changedAt.iso">
						{{ changedAt.label }}
					</time>
				</span>
			</p>

			<!-- In both states: also before consenting, the policy is one click away -->
			<p class="text-md text-muted-foreground">
				Was wir speichern und wie lange, steht in der

				<BaseLink
					route-name="legal-privacy"
					variant="inline"
				>
					Datenschutzerklärung
				</BaseLink>. Fragen zu deinen Daten beantworten wir unter

				<BaseLink
					:href="`mailto:${OPERATOR.privacyEmail}`"
					variant="inline"
				>
					{{ OPERATOR.privacyEmail }}
				</BaseLink>.
			</p>

			<template v-if="auth.hasDataConsent">
				<BaseButton
					class="self-start"
					variant="danger-soft"
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
			description="Du bekommst eine JSON-Datei mit allen Daten zu deinem Konto: Konto- und Profildaten, Einwilligungsverlauf, Körperdaten, Ziele, Gewichts- und Tagebucheinträge, eigene Mahlzeiten, deine Rezepte und Einreichungen mit Ablehnungsgründen sowie deine Merkliste."
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
			description="Wir löschen sofort und endgültig dein Gewicht, deine Körperdaten, deine Einträge, eigene Mahlzeiten und deinen Tagesbedarf. Tagebuch und eigene Mahlzeiten sind dann nicht nutzbar. Du kannst jederzeit wieder einwilligen, die gelöschten Daten kommen aber nicht zurück."
			confirm-label="Widerrufen"
			cancel-label="Abbrechen"
			variant="danger"
			@confirm="revoke"
		/>
	</AccountPanel>
</template>

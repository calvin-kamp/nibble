<script setup lang="ts">
import type { WeightEntry } from '@features/tracking/tracking.types'

import { onMounted, ref } from 'vue'

import AccountPanel from '@features/account/components/AccountPanel.vue'
import AccountSection from '@features/account/components/AccountSection.vue'
import PersonalDataForm from '@features/account/components/PersonalDataForm.vue'
import { BaseLink } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'
import { fetchWeightEntries } from '@features/tracking/tracking.api'
import { formatRelativeDay } from '@shared/utils/date'
import { formatKg } from '@shared/utils/number'

// Details for the basal metabolic rate. The calorie calculator is prefilled with them; weight
// comes from the diary.
const auth = useAuthStore()

// The latest diary entry, only with consent
const latestWeight = ref<WeightEntry | undefined>(undefined)

onMounted(async () => {
	if (!auth.hasDataConsent) return

	try {
		latestWeight.value = (await fetchWeightEntries()).at(-1)
	} catch {
		// Without a weight, only the pointer to the diary is shown
	}
})
</script>

<template>
	<AccountPanel title="Persönliches">
		<div class="flex flex-col gap-2">
			<p class="text-ink-soft">
				Damit rechnet der Kalorienrechner, du musst nichts doppelt eingeben. Die Angaben
				sieht niemand außer dir.
			</p>

			<!-- Body data is health data: without consent the backend stores none, so there is no form -->
			<p
				v-if="!auth.hasDataConsent"
				class="notice notice--info"
			>
				Körperdaten kannst du nur mit Einwilligung speichern. Du kannst sie im Bereich
				<BaseLink
					route-name="account-privacy"
					variant="inline"
					>Datenschutz</BaseLink
				>
				erteilen.
			</p>

			<AccountSection
				v-else
				title="Körperdaten"
			>
				<PersonalDataForm />
			</AccountSection>
		</div>

		<!-- Weight changes constantly, so it lives in the diary rather than here -->
		<section
			v-if="auth.hasDataConsent"
			class="flex flex-col gap-0.5 pt-7 border-t border-divider"
			aria-labelledby="account-weight-title"
		>
			<h3
				id="account-weight-title"
				class="font-sans text-md font-bold tracking-normal"
			>
				Gewicht
			</h3>

			<p
				v-if="latestWeight"
				class="text-ink-soft tabular-nums"
			>
				{{ formatKg(latestWeight.kg) }} - {{ formatRelativeDay(latestWeight.date) }}
			</p>

			<p class="text-sm text-muted">
				Kommt aus deinem

				<BaseLink route-name="diary-weight"> Gewichtstagebuch </BaseLink>

				,dort trägst du es ein.
			</p>
		</section>
	</AccountPanel>
</template>

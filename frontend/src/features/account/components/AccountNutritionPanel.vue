<script setup lang="ts">
import type { NutritionSettings } from '@features/account/account.types'

import { CalculatorIcon, PencilIcon } from '@lucide/vue'
import { computed, nextTick, onMounted, ref } from 'vue'

import AccountPanel from '@features/account/components/AccountPanel.vue'
import AccountSection from '@features/account/components/AccountSection.vue'
import NutritionForm from '@features/account/components/NutritionForm.vue'
import MacroSplitBar from '@features/tracking/components/MacroSplitBar.vue'
import { BaseButton, BaseIcon, BaseLink } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { fetchNutritionSettings, saveNutritionSettings } from '@features/account/account.api'
import { useAuthStore } from '@features/auth/auth.store'
import {
	GOAL_LABELS,
	KCAL_PER_GRAM,
} from '@features/calorie-calculator/calorie-calculator.constants'
import { macroShares } from '@features/calorie-calculator/calorie-calculator.utils'
import { formatNumber } from '@shared/utils/number'

// Below 1,500 kcal a day, it is better to check with a doctor what is appropriate
const LOW_KCAL = 1500

const auth = useAuthStore()
const toast = useToast()

const settings = ref<NutritionSettings | null>(null)
const loaded = ref<boolean>(false)
const loadError = ref<boolean>(false)
const editing = ref<boolean>(false)
const saving = ref<boolean>(false)

onMounted(async () => {
	if (!auth.hasDataConsent) return

	try {
		settings.value = await fetchNutritionSettings()
		loaded.value = true
	} catch {
		loadError.value = true
	}
})

const macros = computed(() => {
	if (!settings.value) return []

	const { protein, carbs, fat } = settings.value.needs

	const items = [
		{
			label: 'Protein',
			grams: protein,
			kcal: protein * KCAL_PER_GRAM.protein,
			color: 'var(--macro-protein)',
		},
		{
			label: 'Kohlenhydrate',
			grams: carbs,
			kcal: carbs * KCAL_PER_GRAM.carbs,
			color: 'var(--macro-carbs)',
		},
		{
			label: 'Fett',
			grams: fat,
			kcal: fat * KCAL_PER_GRAM.fat,
			color: 'var(--macro-fat)',
		},
	]
	const shares = macroShares({ protein, carbs, fat })
	const keys = ['protein', 'carbs', 'fat'] as const

	return items.map((item, index) => Object.assign(item, { share: shares[keys[index]!] }))
})

const editButton = ref<InstanceType<typeof BaseButton> | null>(null)

async function closeForm(): Promise<void> {
	editing.value = false

	await nextTick()

	const element = editButton.value?.$el as HTMLElement | undefined

	element?.focus()
}

async function onSave(updated: NutritionSettings): Promise<void> {
	saving.value = true

	try {
		await saveNutritionSettings(updated)

		settings.value = updated

		await closeForm()

		toast.show('Tagesbedarf gespeichert')
	} catch {
		toast.show('Der Tagesbedarf konnte nicht gespeichert werden.', 'danger')
	} finally {
		saving.value = false
	}
}
</script>

<template>
	<AccountPanel title="Ernährung">
		<p
			v-if="!auth.hasDataConsent"
			class="notice notice--info"
		>
			Das Tracking ist ausgeschaltet, deshalb gibt es keinen gespeicherten Tagesbedarf. Du
			kannst es im Bereich

			<BaseLink
				route-name="account-privacy"
				variant="inline"
			>
				Datenschutz
			</BaseLink>

			einschalten.
		</p>

		<p
			v-else-if="loadError"
			class="notice notice--danger"
			role="alert"
		>
			Dein Tagesbedarf konnte nicht geladen werden. Lad die Seite bitte neu.
		</p>

		<template v-else-if="loaded">
			<p
				v-if="!settings"
				class="notice notice--info"
			>
				Du hast noch keinen Tagesbedarf festgelegt. Berechne ihn mit dem Rechner oder leg
				ihn selbst fest.
			</p>

			<AccountSection
				v-if="settings"
				title="Dein Tagesbedarf"
			>
				<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-3">
					<p class="flex flex-wrap items-baseline gap-x-2">
						<strong class="figure figure--2xl">
							{{ formatNumber(settings.needs.kcal) }}
						</strong>

						<span class="font-semibold text-foreground/80">
							kcal pro Tag
						</span>
					</p>

					<p class="flex flex-wrap items-center gap-2 text-md text-muted-foreground">
						<span
							v-if="settings.goal"
							class="tag tag--accent"
						>
							Ziel: {{ GOAL_LABELS[settings.goal] }}
						</span>

						<template v-if="settings.needs.source">
							{{
								settings.needs.source === 'manual'
									? 'Selbst festgelegt'
									: 'Mit dem Rechner berechnet'
							}}
						</template>
					</p>
				</div>

				<MacroSplitBar :macros="settings.needs" />

				<dl class="data-list">
					<div
						v-for="macro in macros"
						:key="macro.label"
						class="data-list__row"
					>
						<dt class="data-list__label">
							<span class="flex items-center gap-2 font-semibold text-foreground">
								<span
									class="size-2.5 shrink-0 rounded-full"
									:style="{ backgroundColor: macro.color }"
									aria-hidden="true"
								/>

								{{ macro.label }}
							</span>

							<span class="data-list__meta pl-4.5">
								{{ macro.share }} % der Kalorien
							</span>
						</dt>

						<dd class="data-list__value">
							{{ formatNumber(macro.grams) }} g
						</dd>
					</div>
				</dl>

				<p
					v-if="settings.needs.kcal < LOW_KCAL"
					class="notice notice--warning"
				>
					<strong>
						Bitte sprich mit einer Ärztin oder einem Arzt.
					</strong> Dein Wert liegt
					unter 1.500 kcal. Wie viel für dich passt, solltest du ärztlich abklären.
				</p>
			</AccountSection>

			<AccountSection
				:title="settings ? 'Bedarf anpassen' : 'Bedarf festlegen'"
				:description="
					editing || !settings
						? undefined
						: 'Hat sich dein Gewicht oder dein Alltag geändert? Dann lohnt sich ein neuer Wert.'
				"
			>
				<NutritionForm
					v-if="editing"
					:settings="settings"
					:submitting="saving"
					@save="onSave"
					@cancel="closeForm"
				/>

				<div
					v-else
					class="flex flex-col gap-3 sm:flex-row"
				>
					<BaseButton route-name="calorie-calculator">
						<BaseIcon :icon="CalculatorIcon" />

						Neu berechnen
					</BaseButton>

					<BaseButton
						ref="editButton"
						variant="outline"
						@click="editing = true"
					>
						<BaseIcon :icon="PencilIcon" />

						Makros selbst festlegen
					</BaseButton>
				</div>
			</AccountSection>
		</template>
	</AccountPanel>
</template>

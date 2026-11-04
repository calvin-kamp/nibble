<script setup lang="ts">
import type { OnboardingData } from '@features/onboarding/onboarding.types'

import { ArrowRightIcon } from '@lucide/vue'
import { computed } from 'vue'

import OnboardingNav from '@features/onboarding/components/OnboardingNav.vue'
import OnboardingStep from '@features/onboarding/components/OnboardingStep.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { GOAL_LABELS, SEX_LABELS } from '@features/calorie-calculator/calorie-calculator.constants'
import { formatLongDate, parseIsoDate } from '@shared/utils/date'
import { formatKg, formatNumber } from '@shared/utils/number'

interface Props {
	data: OnboardingData
}

const props = defineProps<Props>()

const emit = defineEmits<{
	back: []
	complete: []
}>()

const NOT_SET = 'Noch nicht festgelegt'
const NOT_ENTERED = 'Nicht angegeben'

const lead = computed<string>(() =>
	props.data.consent
		? 'Du kannst jetzt dein Essen und dein Gewicht eintragen. Alles Weitere findest du in den Einstellungen.'
		: 'Du kannst alle Rezepte und den Rechner nutzen. Wenn nibble später doch deine Daten speichern soll, kannst du in den Einstellungen einwilligen.',
)

const account = computed(() => [
	{ label: 'Benutzername', value: props.data.username },
	// Consent covers the health data (section 5 of the privacy policy), not the policy itself
	{
		label: 'Einwilligung Gesundheitsdaten',
		value: props.data.consent ? 'Erteilt' : 'Nicht erteilt',
	},
])

const healthData = computed(() => {
	if (!props.data.consent) return []

	const body = props.data.body
	const needs = props.data.needs
	const source = needs?.source === 'calculated' ? 'berechnet' : 'selbst eingetragen'

	return [
		{
			label: 'Geburtsdatum',
			value: body?.birthDate ? formatLongDate(parseIsoDate(body.birthDate)!) : NOT_ENTERED,
		},
		{ label: 'Geschlecht', value: body?.sex ? SEX_LABELS[body.sex] : NOT_ENTERED },
		{
			label: 'Größe',
			value: body?.heightCm ? `${formatNumber(body.heightCm)} cm` : NOT_ENTERED,
		},
		{ label: 'Gewicht', value: body?.weightKg ? formatKg(body.weightKg) : NOT_ENTERED },
		{ label: 'Ziel', value: props.data.goal ? GOAL_LABELS[props.data.goal] : NOT_SET },
		{
			label: 'Tagesbedarf',
			value: needs ? `${formatNumber(needs.kcal)} kcal (${source})` : NOT_SET,
		},
	]
})

const primary = computed(() =>
	props.data.consent ? { label: 'Zur Übersicht' } : { label: 'Rezepte entdecken' },
)
</script>

<template>
	<OnboardingStep
		as="section"
		:title="`Alles bereit, ${props.data.username}.`"
		:lead="lead"
	>
		<dl class="data-list data-list--stacked">
			<div
				v-for="row in account"
				:key="row.label"
				class="data-list__row"
			>
				<dt class="data-list__label">
					{{ row.label }}
				</dt>

				<dd class="data-list__value">
					{{ row.value }}
				</dd>
			</div>
		</dl>

		<section
			v-if="healthData.length"
			class="flex flex-col"
			aria-labelledby="done-health-title"
		>
			<h2
				id="done-health-title"
				class="text-xl"
			>
				Deine Gesundheitsdaten
			</h2>

			<dl class="data-list data-list--stacked">
				<div
					v-for="row in healthData"
					:key="row.label"
					class="data-list__row"
				>
					<dt class="data-list__label">
						{{ row.label }}
					</dt>

					<dd
						class="data-list__value"
						:class="{
							'font-normal text-muted-foreground':
								row.value === NOT_ENTERED || row.value === NOT_SET,
						}"
					>
						{{ row.value }}
					</dd>
				</div>
			</dl>
		</section>

		<OnboardingNav @back="emit('back')">
			<template #primary>
				<!-- Not a link: the view navigates only once the onboarding is saved, otherwise the
				router guard still sees it as unfinished and sends the user back to step 1 -->
				<BaseButton @click="emit('complete')">
					{{ primary.label }}

					<BaseIcon :icon="ArrowRightIcon" />
				</BaseButton>
			</template>
		</OnboardingNav>
	</OnboardingStep>
</template>

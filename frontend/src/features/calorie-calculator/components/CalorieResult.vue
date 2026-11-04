<script setup lang="ts">
import type {
	CalorieCalculatorValues,
	CalorieResult,
	MacroGrams,
	Workout,
} from '@features/calorie-calculator/calorie-calculator.types'
import type { DonutSegment } from '@shared/ui/types'

import { computed, onMounted, ref } from 'vue'

import { BaseCard, BaseDonutChart, BaseProgressBar } from '@shared/ui'

import {
	ADULT_AGE,
	GOAL_FACTOR,
	GOAL_LABELS,
} from '@features/calorie-calculator/calorie-calculator.constants'
import { macroShares, trainingLabel } from '@features/calorie-calculator/calorie-calculator.utils'
import { formatNumber } from '@shared/utils/number'

interface Props {
	result: CalorieResult
	values: CalorieCalculatorValues
}

const props = defineProps<Props>()

const MACRO_COLORS: Record<string, string> = {
	Fett: 'var(--macro-fat)',
	Protein: 'var(--macro-protein)',
	Kohlenhydrate: 'var(--macro-carbs)',
}

const heading = ref<HTMLElement | null>(null)

onMounted(() => heading.value?.focus())

function roundKcal(kcal: number): number {
	return Math.round(kcal / 10) * 10
}

function formatKcal(kcal: number): string {
	return `${formatNumber(roundKcal(kcal))} kcal`
}

function isComplete(workout: Workout): boolean {
	return workout.met !== '' && workout.duration > 0 && workout.frequency > 0
}

const trainingDescription = computed<string>(() => {
	const list = props.values.exercises
		.filter(isComplete)
		.map((workout) => {
			const label = trainingLabel(workout.met) ?? 'Training'

			return `${label} ${workout.duration} Min., ${workout.frequency} Mal pro Woche`
		})
		.join('; ')

	return `${list} (Ø pro Tag)`
})

const parts = computed(() =>
	[
		{
			label: 'Grundumsatz',
			description: 'Das verbrennt dein Körper in Ruhe.',
			kcal: props.result.basalMetabolicRate,
		},
		{
			label: 'Alltagsbewegung',
			description: `${formatNumber(props.values.steps)} Schritte pro Tag`,
			kcal: props.result.stepsConsumption,
		},
		{
			label: 'Training',
			description: trainingDescription.value,
			kcal: props.result.trainingConsumption,
		},
		{
			label: 'Verdauung',
			description: 'Das verbraucht dein Körper beim Verdauen.',
			kcal: props.result.maintenanceCalories - props.result.consumptionBeforeTef,
		},
	].filter((part) => roundKcal(part.kcal) > 0),
)

// From the rounded values, so total needs + goal add up exactly to the target
const goalDifference = computed<number>(
	() => roundKcal(props.result.targetCalories) - roundKcal(props.result.maintenanceCalories),
)

const targetLabel = computed<string>(() => formatNumber(roundKcal(props.result.targetCalories)))

const isRaised = computed<boolean>(() => props.result.safetyAdjustment > 0)

// The floor can be above total needs, in which case there is no deficit at all
const isAboveMaintenance = computed<boolean>(
	() => props.result.targetCalories > props.result.maintenanceCalories,
)

const goalDescription = computed<string>(() => {
	if (isRaised.value) return `Angehoben auf die Untergrenze von ${targetLabel.value} kcal`

	const percent = Math.round(Math.abs(GOAL_FACTOR[props.values.goal] - 1) * 100)

	if (props.values.goal === 'diet') return `Abnehmen: ${percent} % unter deinem Bedarf`
	if (props.values.goal === 'gain') return `Zunehmen: ${percent} % über deinem Bedarf`

	return 'Gewicht halten: entspricht deinem Bedarf'
})

const rawTarget = computed<number>(
	() => props.result.targetCalories - props.result.safetyAdjustment,
)

const macroSegments = computed<DonutSegment[]>(() =>
	props.result.macros.map((macro) => ({ value: macro.kcal, color: MACRO_COLORS[macro.name] })),
)

// From the grams as shown, so the shares match the settings and always add up to 100 %
const shares = computed(() => {
	const grams = (name: string) =>
		props.result.macros.find((macro) => macro.name === name)?.amount ?? 0

	return macroShares({
		protein: grams('Protein'),
		carbs: grams('Kohlenhydrate'),
		fat: grams('Fett'),
	})
})

const SHARE_KEYS: Record<string, keyof MacroGrams> = {
	Protein: 'protein',
	Kohlenhydrate: 'carbs',
	Fett: 'fat',
}

function macroShare(name: string): number {
	const key = SHARE_KEYS[name]

	return key ? shares.value[key] : 0
}

function formatSigned(kcal: number): string {
	if (kcal === 0) return '0 kcal'

	return `${kcal > 0 ? '+' : '−'}${formatNumber(Math.abs(kcal))} kcal`
}
</script>

<template>
	<div class="flex flex-col gap-8">
		<BaseCard
			as="section"
			variant="inverse"
			size="lg"
			aria-labelledby="calorie-result-title"
		>
			<div class="flex flex-col items-center gap-8 md:flex-row md:gap-12">
				<BaseDonutChart
					class="w-56 shrink-0"
					variant="inverse"
					:height="224"
					:segments="macroSegments"
					:rounded="false"
					:label="`Makro-Verteilung von ${targetLabel} Kilokalorien`"
					:central-label="targetLabel"
					central-sub-label="kcal pro Tag"
				/>

				<div class="flex flex-col gap-8 w-full min-w-0">
					<div class="flex flex-col gap-6">
						<div class="flex flex-col gap-3">
							<h2
								id="calorie-result-title"
								ref="heading"
								class="text-forest-foreground outline-none"
								tabindex="-1"
							>
								Dein Richtwert
							</h2>

							<p class="flex flex-wrap items-center gap-x-3 gap-y-2">
								<strong class="text-lg text-forest-foreground tabular-nums">
									{{ targetLabel }} kcal pro Tag
								</strong>

								<span class="tag tag--highlight">
									{{ GOAL_LABELS[props.values.goal] }}
								</span>
							</p>
						</div>

						<section
							class="flex flex-col gap-1"
							aria-labelledby="calorie-macros-title"
						>
							<h3
								id="calorie-macros-title"
								class="font-sans text-md font-bold tracking-normal text-forest-foreground"
							>
								Makro-Verteilung
							</h3>

							<ul class="data-list data-list--inverse text-md md:text-base">
								<li
									v-for="macro in props.result.macros"
									:key="macro.name"
									class="data-list__row gap-3"
								>
									<span class="data-list__label flex-row items-center gap-2 hyphens-none">
										<span
											class="size-2.5 shrink-0 rounded-full"
											:style="{ backgroundColor: MACRO_COLORS[macro.name] }"
											aria-hidden="true"
										/>

										{{ macro.name }}
									</span>

									<span class="data-list__aside text-forest-muted-foreground">
										{{ macroShare(macro.name) }} %
									</span>

									<span class="data-list__value">
										{{ formatNumber(Math.round(macro.amount)) }} g
									</span>
								</li>
							</ul>
						</section>
					</div>

					<slot name="actions" />
				</div>
			</div>
		</BaseCard>

		<p
			v-if="isRaised && isAboveMaintenance"
			class="notice notice--warning"
			role="note"
		>
			Dein Gesamtbedarf liegt rechnerisch unter {{ targetLabel }} kcal. Weniger als das
			empfehlen wir nicht, weil es darunter schwer wird, genug Vitamine und Mineralstoffe zu
			bekommen.

			<template v-if="props.values.goal === 'diet'">
				Über weniger Essen abzunehmen ist für dich deshalb nicht sinnvoll.
			</template>

			Sprich bitte mit einer Ärztin oder einem Arzt, wie du gut auf deinen Bedarf kommst.
		</p>

		<p
			v-else-if="isRaised"
			class="notice notice--warning"
			role="note"
		>
			Rechnerisch kämen wir auf {{ formatKcal(rawTarget) }}. Darunter wird es schwer, genug
			Vitamine und Mineralstoffe zu bekommen, deshalb zeigen wir dir mindestens

			{{ targetLabel }} kcal. Wenn du weniger essen möchtest, sprich bitte vorher mit einer
			Ärztin oder einem Arzt.
		</p>

		<p
			v-if="props.values.age < ADULT_AGE"
			class="notice notice--info"
			role="note"
		>
			Der Rechner ist für Erwachsene gemacht. Solange du noch wächst, kann dein Bedarf höher
			sein.
		</p>

		<section
			class="flex flex-col gap-8"
			aria-labelledby="calorie-breakdown-title"
		>
			<div class="flex flex-col gap-5">
				<h2 id="calorie-breakdown-title">
					So setzt sich dein Bedarf zusammen
				</h2>

				<ul class="flex flex-col gap-6">
					<li
						v-for="part in parts"
						:key="part.label"
						class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1"
					>
						<span class="font-semibold">
							{{ part.label }}
						</span>

						<span class="font-bold tabular-nums">
							{{ formatKcal(part.kcal) }}
						</span>

						<div class="flex flex-col gap-2 basis-full">
							<span class="text-md text-muted-foreground">
								{{
									part.description
								}}
							</span>

							<BaseProgressBar
								:value="part.kcal"
								:max="props.result.maintenanceCalories"
								:label="`${part.label}, Anteil am Gesamtbedarf`"
							/>
						</div>
					</li>
				</ul>
			</div>

			<dl class="border-t-2 border-foreground">
				<div
					class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 py-4"
					:class="{ 'border-b border-divider': goalDifference !== 0 }"
				>
					<dt class="font-semibold">
						Gesamtbedarf
					</dt>

					<dd class="font-bold tabular-nums">
						{{ formatKcal(props.result.maintenanceCalories) }}
					</dd>

					<dd class="basis-full text-md text-muted-foreground">
						Das verbrauchst du etwa pro Tag.
					</dd>
				</div>

				<div
					v-if="goalDifference !== 0"
					class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 py-4"
				>
					<dt class="font-semibold">
						Dein Ziel
					</dt>

					<dd class="font-bold tabular-nums">
						{{ formatSigned(goalDifference) }}
					</dd>

					<dd class="basis-full text-md text-muted-foreground">
						{{ goalDescription }}
					</dd>
				</div>
			</dl>
		</section>

		<p
			class="notice notice--info"
			role="note"
		>
			<strong>
				Wichtig:
			</strong> Wir sind keine Ärzte. Alle Werte sind Richtwerte und eine
			Schätzung, sie ersetzen keine ärztliche Beratung. In der Schwangerschaft und Stillzeit,
			bei einer Essstörung oder bei Erkrankungen wie Diabetes oder einer Nierenerkrankung
			passt der Rechner nicht. Sprich dann bitte mit deiner Ärztin oder deinem Arzt.
		</p>
	</div>
</template>

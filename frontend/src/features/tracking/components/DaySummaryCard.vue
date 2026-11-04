<script setup lang="ts">
import type { FoodEntry, NutritionGoals } from '@features/tracking/tracking.types'

import { useId } from 'reka-ui'
import { computed } from 'vue'

import { BaseCard, BaseDonutChart, BaseProgressBar } from '@shared/ui'

import { summarizeDay } from '@features/tracking/tracking.utils'
import { formatNumber } from '@shared/utils/number'

interface Props {
	entries: FoodEntry[]
	goals: NutritionGoals | null
	date: string
	title?: string
	titleHidden?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	title: 'Summe des Tags',
	titleHidden: false,
})

defineSlots<{
	actions?(): unknown
}>()

const titleId = useId(undefined, 'day-summary')

const summary = computed(() => summarizeDay(props.entries, props.date))

const remaining = computed<number>(() => (props.goals?.kcal ?? 0) - summary.value.kcal)

const macros = computed(() => [
	{
		label: 'Protein',
		value: summary.value.protein,
		goal: props.goals?.protein,
		color: 'var(--macro-protein)',
	},
	{
		label: 'Kohlenhydrate',
		value: summary.value.carbs,
		goal: props.goals?.carbs,
		color: 'var(--macro-carbs)',
	},
	{
		label: 'Fett',
		value: summary.value.fat,
		goal: props.goals?.fat,
		color: 'var(--macro-fat)',
	},
])
</script>

<template>
	<BaseCard
		as="section"
		variant="inverse"
		size="lg"
		:aria-labelledby="titleId"
	>
		<div
			v-if="!props.titleHidden || $slots.actions"
			class="card__header mb-6"
		>
			<h2
				:id="titleId"
				class="card__title text-forest-foreground"
				:class="{ 'sr-only': props.titleHidden }"
			>
				{{ props.title }}
			</h2>

			<slot name="actions" />
		</div>

		<h2
			v-else
			:id="titleId"
			class="sr-only"
		>
			{{ props.title }}
		</h2>

		<div class="flex flex-col items-center gap-10 lg:flex-row lg:justify-around lg:gap-12">
			<div class="flex flex-col items-center gap-4 shrink-0">
				<BaseDonutChart
					class="w-56"
					variant="inverse"
					:height="224"
					:segments="[{ value: summary.kcal }]"
					:max="props.goals?.kcal"
					:label="
						props.goals
							? `${formatNumber(summary.kcal)} von ${formatNumber(props.goals.kcal)} Kilokalorien gegessen`
							: `${formatNumber(summary.kcal)} Kilokalorien gegessen`
					"
					:central-label="formatNumber(props.goals ? Math.abs(remaining) : summary.kcal)"
					:central-sub-label="
						props.goals ? (remaining >= 0 ? 'kcal übrig' : 'kcal drüber') : 'kcal'
					"
				/>

				<p class="text-lg text-center text-balance">
					<strong class="text-forest-foreground">
						{{ formatNumber(summary.kcal) }}
					</strong>

					<template v-if="props.goals">
						von {{ formatNumber(props.goals.kcal) }}
					</template>

					kcal gegessen
				</p>
			</div>

			<div class="@container w-full max-w-xl">
				<!-- Narrow: bars like on the dashboard, three rings stacked would take a whole screen -->
				<ul class="flex flex-col gap-3 @md:hidden">
					<li
						v-for="macro in macros"
						:key="macro.label"
						class="grid grid-cols-[minmax(0,1fr)_auto] items-baseline gap-x-3 gap-y-1.5 text-md md:text-base"
					>
						<span class="min-w-0 font-bold text-forest-foreground wrap-break-word">
							{{ macro.label }}
						</span>

						<span class="tabular-nums whitespace-nowrap">
							<strong class="text-forest-foreground">
								{{ formatNumber(Math.round(macro.value)) }}
							</strong>

							<template v-if="macro.goal !== undefined">
								/ {{ formatNumber(macro.goal) }}
							</template>

							g
						</span>

						<BaseProgressBar
							class="col-span-2"
							variant="inverse"
							:value="macro.value"
							:max="macro.goal ?? 0"
							:label="macro.label"
							:color="macro.color"
						/>
					</li>
				</ul>

				<ul class="hidden grid-cols-12 gap-4 @md:grid">
					<li
						v-for="macro in macros"
						:key="macro.label"
						class="flex flex-col items-center gap-2 col-span-4 text-center"
					>
						<BaseDonutChart
							class="w-28 shrink-0"
							variant="inverse"
							size="sm"
							:height="112"
							:arc-width="12"
							:segments="[{ value: macro.value, color: macro.color }]"
							:max="macro.goal"
							:label="
								macro.goal === undefined
									? `${macro.label}: ${formatNumber(Math.round(macro.value))} Gramm`
									: `${macro.label}: ${formatNumber(Math.round(macro.value))} von ${formatNumber(macro.goal)} Gramm`
							"
							:central-label="formatNumber(Math.round(macro.value))"
							central-sub-label="g"
						/>

						<div class="flex flex-col items-center gap-1 min-w-0">
							<span class="font-bold text-forest-foreground">
								{{ macro.label }}
							</span>

							<span v-if="macro.goal !== undefined">
								von {{ formatNumber(macro.goal) }} g
							</span>
						</div>
					</li>
				</ul>
			</div>
		</div>
	</BaseCard>
</template>

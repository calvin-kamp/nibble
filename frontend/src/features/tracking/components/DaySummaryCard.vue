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
	/** Before the day has loaded: empty rings and no numbers, but already the final layout */
	loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	title: 'Summe des Tags',
	titleHidden: false,
	loading: false,
})

defineSlots<{
	actions?(): unknown
}>()

const titleId = useId(undefined, 'day-summary')

const summary = computed(() => summarizeDay(props.entries, props.date))

const remaining = computed<number>(() => (props.goals?.kcal ?? 0) - summary.value.kcal)

/** While loading, an empty ring: nothing eaten of an unknown target */
const kcalMax = computed<number | undefined>(() => (props.loading ? 1 : props.goals?.kcal))

function figure(value: number): string {
	return props.loading ? '–' : formatNumber(Math.round(value))
}

const macros = computed(() => [
	{
		label: 'Protein',
		value: summary.value.protein,
		goal: props.loading ? 1 : props.goals?.protein,
		color: 'var(--macro-protein)',
	},
	{
		label: 'Kohlenhydrate',
		value: summary.value.carbs,
		goal: props.loading ? 1 : props.goals?.carbs,
		color: 'var(--macro-carbs)',
	},
	{
		label: 'Fett',
		value: summary.value.fat,
		goal: props.loading ? 1 : props.goals?.fat,
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

		<!-- Fixed widths and lines that are always there: the card keeps its layout while the
			day loads and on days with and without a target -->
		<div
			class="flex flex-col items-center gap-10 lg:flex-row lg:justify-around lg:gap-12"
			:aria-busy="props.loading"
		>
			<div class="flex flex-col items-center gap-4 shrink-0 lg:w-72">
				<BaseDonutChart
					class="w-56"
					variant="inverse"
					:height="224"
					:segments="[{ value: props.loading ? 0 : summary.kcal }]"
					:max="kcalMax"
					:label="
						props.goals
							? `${formatNumber(summary.kcal)} von ${formatNumber(props.goals.kcal)} Kilokalorien gegessen`
							: `${formatNumber(summary.kcal)} Kilokalorien gegessen`
					"
					:central-label="figure(props.goals ? Math.abs(remaining) : summary.kcal)"
					:central-sub-label="
						props.goals ? (remaining >= 0 ? 'kcal übrig' : 'kcal drüber') : 'kcal'
					"
				/>

				<p class="text-lg text-center text-balance">
					<strong class="text-forest-foreground">
						{{ figure(summary.kcal) }}
					</strong>

					<template v-if="props.goals && !props.loading">
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
								{{ figure(macro.value) }}
							</strong>

							<template v-if="macro.goal !== undefined && !props.loading">
								/ {{ formatNumber(macro.goal) }}
							</template>

							g
						</span>

						<BaseProgressBar
							class="col-span-2"
							variant="inverse"
							:value="props.loading ? 0 : macro.value"
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
							:segments="[{ value: props.loading ? 0 : macro.value, color: macro.color }]"
							:max="macro.goal"
							:label="
								macro.goal === undefined
									? `${macro.label}: ${formatNumber(Math.round(macro.value))} Gramm`
									: `${macro.label}: ${formatNumber(Math.round(macro.value))} von ${formatNumber(macro.goal)} Gramm`
							"
							:central-label="figure(macro.value)"
							central-sub-label="g"
						/>

						<div class="flex flex-col items-center gap-1 min-w-0">
							<span class="font-bold text-forest-foreground">
								{{ macro.label }}
							</span>

							<!-- Always there, so the rings don't jump when the target arrives -->
							<span :class="{ invisible: macro.goal === undefined || props.loading }">
								von {{ formatNumber(macro.goal ?? 0) }} g
							</span>
						</div>
					</li>
				</ul>
			</div>
		</div>
	</BaseCard>
</template>

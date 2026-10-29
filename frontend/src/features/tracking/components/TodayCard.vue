<script setup lang="ts">
import type { FoodEntry, NutritionGoals, WeightEntry } from '@features/tracking/tracking.types'

import { ArrowRightIcon, PlusIcon, WeightIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'

import {
	BaseButton,
	BaseCard,
	BaseDonutChart,
	BaseIcon,
	BaseLink,
	BaseProgressBar,
} from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { summarizeDay } from '@features/tracking/tracking.utils'
import { toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

interface Props {
	foodEntries: FoodEntry[]
	weightEntries: WeightEntry[]
	/** null while no daily needs are set. The card then only shows what was eaten. */
	goals: NutritionGoals | null
	/** Day in the format YYYY-MM-DD, defaults to today */
	date?: string
}

const props = withDefaults(defineProps<Props>(), {
	date: undefined,
})

// Opens the same dialogs as "Eintrag hinzufügen" in the navigation
const { openEntry } = useTrackingDialogs()

const day = computed<string>(() => props.date ?? toIsoDate())
const summary = computed(() => summarizeDay(props.foodEntries, day.value))

const remainingKcal = computed<number>(() => (props.goals?.kcal ?? 0) - summary.value.kcal)

const macros = computed(() => [
	{
		label: 'Protein',
		value: summary.value.protein,
		goal: props.goals?.protein,
		color: 'var(--color-macro-protein)',
	},
	{
		label: 'Kohlenhydrate',
		value: summary.value.carbs,
		goal: props.goals?.carbs,
		color: 'var(--color-macro-carbs)',
	},
	{
		label: 'Fett',
		value: summary.value.fat,
		goal: props.goals?.fat,
		color: 'var(--color-macro-fat)',
	},
])

const hasFoodEntry = computed<boolean>(() => summary.value.meals.length > 0)
const hasWeightEntry = computed<boolean>(() =>
	props.weightEntries.some((entry) => entry.date === day.value),
)

const heading = ref<HTMLElement | null>(null)
const actions = ref<HTMLElement | null>(null)

// A new entry hides its button. If that button had focus, e.g. because the dialog returned it
// there, focus moves to the remaining button or the heading instead of falling back to the page.
watch(
	[hasFoodEntry, hasWeightEntry],
	async () => {
		if (!actions.value?.contains(document.activeElement)) return

		await nextTick()

		const next = actions.value?.querySelector<HTMLElement>('button') ?? heading.value
		next?.focus()
	},
	{ flush: 'pre' },
)
</script>

<template>
	<BaseCard
		as="section"
		variant="inverse"
		size="lg"
		aria-labelledby="today-card-title"
	>
		<div class="grid grid-cols-12 gap-8 xl:gap-x-10">
			<div class="flex flex-col gap-6 col-span-12 min-w-0 xl:col-span-9">
				<h2
					id="today-card-title"
					ref="heading"
					class="text-2xl text-white outline-none"
					tabindex="-1"
				>
					Heute
				</h2>

				<div class="flex flex-col items-center gap-6 sm:flex-row sm:gap-8">
					<BaseDonutChart
						class="w-60 shrink-0"
						variant="inverse"
						:segments="[{ value: summary.kcal }]"
						:max="props.goals?.kcal"
						:label="
							props.goals
								? `${formatNumber(summary.kcal)} von ${formatNumber(props.goals.kcal)} Kilokalorien gegessen`
								: `${formatNumber(summary.kcal)} Kilokalorien gegessen`
						"
						:central-label="
							formatNumber(props.goals ? Math.abs(remainingKcal) : summary.kcal)
						"
						:central-sub-label="
							props.goals
								? remainingKcal >= 0
									? 'kcal übrig'
									: 'kcal zu viel'
								: 'kcal'
						"
					/>

					<div class="flex flex-col gap-4 w-full min-w-0">
						<p class="text-md sm:text-lg">
							<strong class="text-white">{{ formatNumber(summary.kcal) }}</strong>

							<template v-if="props.goals">
								von {{ formatNumber(props.goals.kcal) }}</template
							>
							kcal gegessen
						</p>

						<p
							v-if="!props.goals"
							class="text-sm"
						>
							Noch kein Tagesbedarf festgelegt.
							<BaseLink
								route-name="account-nutrition"
								variant="inline"
								class="text-lime"
								>Jetzt festlegen</BaseLink
							>
						</p>

						<ul class="flex flex-col gap-3">
							<li
								v-for="macro in macros"
								:key="macro.label"
								class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1"
							>
								<span class="font-bold text-white">{{ macro.label }}</span>

								<span class="tabular-nums">
									<strong class="text-white">{{
										formatNumber(Math.round(macro.value))
									}}</strong>

									<template v-if="macro.goal !== undefined">
										/ {{ formatNumber(macro.goal) }}</template
									>
									g
								</span>

								<BaseProgressBar
									class="basis-full"
									variant="inverse"
									:value="macro.value"
									:max="macro.goal ?? 0"
									:label="macro.label"
									:color="macro.color"
								/>
							</li>
						</ul>
					</div>
				</div>

				<div
					v-if="!hasFoodEntry || !hasWeightEntry"
					ref="actions"
					class="flex flex-wrap gap-3 mt-auto"
				>
					<BaseButton
						v-if="!hasFoodEntry"
						variant="secondary"
						@click="openEntry('food')"
					>
						<BaseIcon :icon="PlusIcon" />
						Essen eintragen
					</BaseButton>

					<BaseButton
						v-if="!hasWeightEntry"
						variant="outline"
						@click="openEntry('weight')"
					>
						<BaseIcon :icon="WeightIcon" />
						Gewicht eintragen
					</BaseButton>
				</div>
			</div>

			<div
				class="flex flex-col gap-2 col-span-12 pt-8 border-t border-white/15 xl:col-span-3 xl:pt-0 xl:pl-10 xl:border-t-0 xl:border-l"
			>
				<h3 class="text-2xl text-white">Gegessen</h3>

				<ul
					v-if="hasFoodEntry"
					class="data-list data-list--inverse"
				>
					<li
						v-for="meal in summary.meals"
						:key="meal.meal"
						class="data-list__row"
					>
						<span class="data-list__label">{{ meal.label }}</span>

						<span class="data-list__value">{{ formatNumber(meal.kcal) }} kcal</span>
					</li>
				</ul>

				<p v-else>Heute noch nichts eingetragen.</p>

				<BaseLink
					variant="no-decoration"
					route-name="diary-food"
					class="self-start mt-auto text-lime"
				>
					Zum Tagebuch
					<BaseIcon
						:icon="ArrowRightIcon"
						:size="16"
					/>
				</BaseLink>
			</div>
		</div>
	</BaseCard>
</template>

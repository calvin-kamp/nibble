<script setup lang="ts">
import type { FoodEntry, MealType, NutritionGoals } from '@features/tracking/tracking.types'

import { ChevronLeftIcon, ChevronRightIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import MacroList from '@features/tracking/components/MacroList.vue'
import {
	BaseAlertDialog,
	BaseBreadcrumb,
	BaseButton,
	BaseCard,
	BaseDonutChart,
	BaseIcon,
} from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { deleteFoodEntry, fetchDay } from '@features/tracking/tracking.api'
import { MEAL_LABELS, MEAL_ORDER } from '@features/tracking/tracking.constants'
import { formatQuantity, summarizeDay } from '@features/tracking/tracking.utils'
import { addDays, formatRelativeDay, formatWeekdayDate, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

interface Props {
	/** Calendar day in the format YYYY-MM-DD, already validated by the route */
	date: string
}

const props = defineProps<Props>()

usePageTitle(() => `${formatRelativeDay(props.date)} · Ernährung`)

const toast = useToast()
const { openEntry } = useTrackingDialogs()

// Entries and the targets that applied that day. Reload on a different day or a new entry.
const entries = ref<FoodEntry[]>([])
const goals = ref<NutritionGoals | null>(null)
const loadError = ref<boolean>(false)

watch(
	[() => props.date, useTrackingChanges()],
	async ([date]) => {
		try {
			const day = await fetchDay(date)

			if (day.date !== props.date) return

			entries.value = day.entries
			goals.value = day.goals
			loadError.value = false
		} catch {
			loadError.value = true
		}
	},
	{ immediate: true },
)

const summary = computed(() => summarizeDay(entries.value, props.date))

const previousDay = computed<string>(() => addDays(props.date, -1))
const nextDay = computed<string | null>(() =>
	props.date < toIsoDate() ? addDays(props.date, 1) : null,
)

const remaining = computed<number>(() => (goals.value?.kcal ?? 0) - summary.value.kcal)

// Without daily needs, the rings only show what was eaten
const macros = computed(() => [
	{
		label: 'Protein',
		value: summary.value.protein,
		goal: goals.value?.protein,
		color: 'var(--color-macro-protein)',
	},
	{
		label: 'Kohlenhydrate',
		value: summary.value.carbs,
		goal: goals.value?.carbs,
		color: 'var(--color-macro-carbs)',
	},
	{
		label: 'Fett',
		value: summary.value.fat,
		goal: goals.value?.fat,
		color: 'var(--color-macro-fat)',
	},
])

// All four meals, including empty ones: that is where entries are added after the fact
const meals = computed(() =>
	MEAL_ORDER.map((meal) => {
		const mealEntries = entries.value.filter((entry) => entry.meal === meal)

		return {
			meal,
			label: MEAL_LABELS[meal],
			entries: mealEntries,
			kcal: mealEntries.reduce((sum, entry) => sum + entry.kcal, 0),
		}
	}),
)

function addTo(meal: MealType): void {
	openEntry('food', { date: props.date, meal })
}

// The entry stays set until the confirmation has closed, so its text remains while fading out.
const pendingDelete = ref<FoodEntry | null>(null)
const deleteOpen = ref<boolean>(false)

function askDelete(entry: FoodEntry): void {
	pendingDelete.value = entry
	deleteOpen.value = true
}

async function confirmDelete(): Promise<void> {
	const entry = pendingDelete.value

	if (!entry) return

	try {
		await deleteFoodEntry(entry.id)
		toast.show(`${entry.name} gelöscht`, 'info')
	} catch {
		toast.show(
			'Der Eintrag konnte nicht gelöscht werden. Versuch es bitte noch einmal.',
			'danger',
		)
	}
}
</script>

<template>
	<main class="content-wrapper flex flex-col gap-6 pt-6 pb-10">
		<BaseBreadcrumb
			:items="[{ label: 'Ernährung', routeName: 'diary-food' }]"
			:current="formatRelativeDay(props.date)"
		/>

		<div class="flex items-end justify-between gap-4">
			<div class="flex flex-col gap-2">
				<h1>{{ formatRelativeDay(props.date) }}</h1>

				<p class="text-lg text-muted">{{ formatWeekdayDate(props.date) }}</p>
			</div>

			<nav
				class="flex shrink-0 gap-2"
				aria-label="Tage"
			>
				<BaseButton
					variant="outline"
					size="icon"
					route-name="diary-food-day"
					:params="{ date: previousDay }"
					:aria-label="`Vorheriger Tag: ${formatWeekdayDate(previousDay)}`"
				>
					<BaseIcon :icon="ChevronLeftIcon" />
				</BaseButton>
				<!-- Always present so the arrows do not jump. There is no going past today. -->
				<BaseButton
					variant="outline"
					size="icon"
					:route-name="nextDay ? 'diary-food-day' : undefined"
					:params="nextDay ? { date: nextDay } : undefined"
					:disabled="!nextDay"
					:aria-label="
						nextDay ? `Nächster Tag: ${formatWeekdayDate(nextDay)}` : 'Nächster Tag'
					"
				>
					<BaseIcon :icon="ChevronRightIcon" />
				</BaseButton>
			</nav>
		</div>

		<p
			v-if="loadError"
			class="notice notice--danger"
			role="alert"
		>
			Der Tag konnte nicht geladen werden. Lad die Seite bitte neu.
		</p>

		<div class="flex flex-col gap-8">
			<!-- Day total: the only card on the page, full width. A large ring for calories, smaller
             ones for the macros. -->
			<BaseCard
				as="section"
				variant="inverse"
				size="lg"
				aria-labelledby="day-summary-title"
			>
				<h2
					id="day-summary-title"
					class="sr-only"
				>
					Summe des Tags
				</h2>

				<!-- Calorie ring with the total below on the left, as on the dashboard. Macros on the right. -->
				<div
					class="flex flex-col items-center gap-10 md:flex-row md:justify-around md:gap-12"
				>
					<div class="flex flex-col items-center gap-4 shrink-0">
						<BaseDonutChart
							class="w-56"
							variant="inverse"
							:height="224"
							:segments="[{ value: summary.kcal }]"
							:max="goals?.kcal"
							:label="
								goals
									? `${formatNumber(summary.kcal)} von ${formatNumber(goals.kcal)} Kilokalorien gegessen`
									: `${formatNumber(summary.kcal)} Kilokalorien gegessen`
							"
							:central-label="
								formatNumber(goals ? Math.abs(remaining) : summary.kcal)
							"
							:central-sub-label="
								goals ? (remaining >= 0 ? 'kcal übrig' : 'kcal drüber') : 'kcal'
							"
						/>

						<p class="text-lg text-center">
							<strong class="text-white">{{ formatNumber(summary.kcal) }}</strong>

							<template v-if="goals"> von {{ formatNumber(goals.kcal) }}</template>
							kcal gegessen
						</p>
					</div>

					<!-- One ring per row until all three fit side by side. @container: depends on the space
                 next to the calorie ring, not on the screen. -->
					<div class="@container w-full md:max-w-xl">
						<ul class="grid grid-cols-12 gap-8 @md:gap-4">
							<li
								v-for="macro in macros"
								:key="macro.label"
								class="flex flex-col items-center gap-2 col-span-12 text-center @md:col-span-4"
							>
								<BaseDonutChart
									class="w-full max-w-36"
									variant="inverse"
									size="sm"
									:height="144"
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

								<div class="flex flex-col items-center gap-1">
									<span class="font-bold text-white">{{ macro.label }}</span>

									<span v-if="macro.goal !== undefined"
										>von {{ formatNumber(macro.goal) }} g</span
									>
								</div>
							</li>
						</ul>
					</div>
				</div>
			</BaseCard>

			<!-- All entries by meal, as lists without their own surfaces. Narrower and centered: name and
             calories stay close enough together. -->
			<div class="content-column content-column--narrow gap-8">
				<section
					v-for="meal in meals"
					:key="meal.meal"
					class="flex flex-col"
					:class="meal.entries.length ? 'gap-1' : 'gap-3'"
					:aria-labelledby="`meal-${meal.meal}-title`"
				>
					<!-- Heading, total and add button in the same columns as the entries below: name,
                 calories, action. Empty meals get the add button as their content instead. -->
					<div class="flex items-center gap-4">
						<h2
							:id="`meal-${meal.meal}-title`"
							class="flex-1 min-w-0 text-xl sm:text-2xl"
						>
							{{ meal.label }}
						</h2>

						<template v-if="meal.entries.length">
							<p class="font-semibold whitespace-nowrap tabular-nums text-muted">
								{{ formatNumber(meal.kcal) }} kcal
							</p>

							<BaseButton
								variant="outline"
								size="icon-sm"
								:aria-label="`Hinzufügen: ${meal.label}`"
								@click="addTo(meal.meal)"
							>
								<BaseIcon
									:icon="PlusIcon"
									:size="18"
								/>
							</BaseButton>
						</template>
					</div>

					<ul
						v-if="meal.entries.length"
						class="data-list"
					>
						<!-- The macros get their own line below name and calories, across the full width up
                   to the delete button, instead of being squeezed into the name column -->
						<li
							v-for="entry in meal.entries"
							:key="entry.id"
							class="data-list__row items-start"
						>
							<div class="flex flex-col flex-1 gap-2 min-w-0">
								<div class="flex items-start justify-between gap-4">
									<div class="data-list__label gap-0.5">
										<span class="font-semibold text-ink">{{ entry.name }}</span>

										<span
											v-if="entry.brand || entry.quantity"
											class="data-list__meta"
										>
											{{
												[
													entry.brand,
													entry.quantity &&
														formatQuantity(entry.quantity),
												]
													.filter(Boolean)
													.join(' · ')
											}}
										</span>
									</div>

									<span class="data-list__value"
										>{{ formatNumber(entry.kcal) }} kcal</span
									>
								</div>

								<MacroList
									inline
									:macros="entry"
								/>
							</div>

							<BaseButton
								class="-my-1"
								variant="ghost"
								size="icon-sm"
								:aria-label="`${entry.name} löschen`"
								@click="askDelete(entry)"
							>
								<BaseIcon
									:icon="TrashIcon"
									:size="18"
								/>
							</BaseButton>
						</li>
					</ul>

					<button
						v-else
						type="button"
						class="flex items-center justify-center gap-2 min-h-13 px-4 border-2 border-dashed border-line rounded-md font-semibold text-muted transition-interactive hover:border-brand hover:text-brand-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
						@click="addTo(meal.meal)"
					>
						<BaseIcon
							:icon="PlusIcon"
							:size="18"
						/>

						Hinzufügen<span class="sr-only">: {{ meal.label }}</span>
					</button>
				</section>
			</div>
		</div>

		<BaseAlertDialog
			v-model:open="deleteOpen"
			title="Eintrag löschen?"
			:description="
				pendingDelete ? `${pendingDelete.name} verschwindet aus deinem Tagebuch.` : ''
			"
			confirm-label="Löschen"
			variant="danger"
			@confirm="confirmDelete"
		/>
	</main>
</template>

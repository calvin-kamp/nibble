<script setup lang="ts">
import type {
	DiaryDay,
	DiaryDayWeek,
	FoodWeekSummary,
	NutritionGoals,
	TrackedDay,
} from '@features/tracking/tracking.types'

import { ArrowRightIcon, ChevronDownIcon, ChevronRightIcon, PlusIcon } from '@lucide/vue'
import { computed, ref, shallowRef, watch } from 'vue'
import { RouterLink } from 'vue-router'

import DaySummaryCard from '@features/tracking/components/DaySummaryCard.vue'
import WeekRangeSection from '@features/tracking/components/WeekRangeSection.vue'
import { BaseButton, BaseIcon, BaseLink } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useWeekHistory, WEEKS_PER_PAGE } from '@features/tracking/composables/week-history'

import {
	fetchCurrentGoals,
	fetchFoodWeeks,
	fetchWeekDays,
} from '@features/tracking/tracking.api'
import { averageKcal, formatCalendarWeekTitle, weekStart } from '@features/tracking/tracking.utils'
import { formatRelativeDay, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

const { openEntry } = useTrackingDialogs()

const today = toIsoDate()
const thisWeek = weekStart(today)

// Weeks with entries come from the backend, five at once; their days are loaded afterwards
const history = useWeekHistory<FoodWeekSummary>(fetchFoodWeeks)

const goals = ref<NutritionGoals | null>(null)
const days = shallowRef<TrackedDay[]>([])
const daysLoading = ref<boolean>(false)
const daysError = ref<boolean>(false)

watch(
	useTrackingChanges(),
	async () => {
		goals.value = await fetchCurrentGoals().catch(() => goals.value)
	},
	{ immediate: true },
)

// The current week always shows, with today, unless a range leaves it out
const showsThisWeek = computed<boolean>(
	() => !history.range.value || history.range.value.to >= thisWeek,
)

const weekStarts = computed<string[]>(() => {
	const starts = history.weeks.value.map((week) => week.start)

	return showsThisWeek.value && !starts.includes(thisWeek) ? [thisWeek, ...starts] : starts
})

// A range or a reload can start a new load while the last one runs; only the newest counts
let daysLoadId = 0

watch(weekStarts, async (starts) => {
	const id = ++daysLoadId
	daysLoading.value = true

	try {
		const loaded = await fetchWeekDays(starts)

		if (id !== daysLoadId) return

		days.value = loaded
		daysError.value = false
	} catch {
		if (id === daysLoadId) daysError.value = true
	} finally {
		if (id === daysLoadId) daysLoading.value = false
	}
})

const loading = computed<boolean>(() => history.loading.value || daysLoading.value)
const loadError = computed<boolean>(() => history.loadError.value || daysError.value)

const todayDay = computed<TrackedDay | null>(
	() => days.value.find((day) => day.date === today) ?? null,
)

function toOverview(day: TrackedDay): DiaryDay {
	const sum = (key: 'kcal' | 'protein' | 'carbs' | 'fat') =>
		day.entries.reduce((total, entry) => total + entry[key], 0)

	return {
		date: day.date,
		kcal: sum('kcal'),
		protein: sum('protein'),
		carbs: sum('carbs'),
		fat: sum('fat'),
		entryCount: day.entries.length,
		goalKcal: day.goals?.kcal ?? null,
	}
}

const weeks = computed<DiaryDayWeek[]>(() => {
	const result: DiaryDayWeek[] = []

	for (const day of days.value.map(toOverview)) {
		if (!day.entryCount && day.date !== today) continue

		const start = weekStart(day.date)
		const week = result[result.length - 1]

		if (week?.start === start) week.days.push(day)
		else result.push({ start, days: [day], averageKcal: null })
	}

	for (const week of result) week.averageKcal = averageKcal(week.days)

	return result
})

/**
 * Note on daily needs, only where it says something: today, what is left; otherwise only when
 * the day exceeded its needs. Below that is the normal case and needs no extra line.
 */
function goalNote(day: DiaryDay): string | null {
	if (day.goalKcal === null) return null

	const difference = day.goalKcal - day.kcal

	if (difference < 0) return `${formatNumber(-difference)} über Bedarf`
	if (day.date === today) return `${formatNumber(difference)} übrig`

	return null
}

function dayCountLabel(week: DiaryDayWeek): string {
	const count = week.days.filter((day) => day.entryCount).length

	return count === 1 ? '1 Tag' : `${count} Tage`
}
</script>

<template>
	<main class="page">
		<div class="page__header">
			<div class="page__intro">
				<h1>
					Essen
				</h1>

				<p
					v-if="goals"
					class="page__lead"
				>
					Dein Tagesbedarf:

					<strong class="whitespace-nowrap text-foreground tabular-nums">
						{{ formatNumber(goals.kcal) }} kcal
					</strong>
				</p>
			</div>

			<BaseButton @click="openEntry('food')">
				<BaseIcon :icon="PlusIcon" />

				Essen eintragen
			</BaseButton>
		</div>

		<p
			v-if="loadError"
			class="notice notice--danger"
			role="alert"
		>
			Dein Tagebuch konnte nicht geladen werden. Lad die Seite bitte neu.
		</p>

		<!-- Already there while loading, so nothing below jumps when today arrives -->
		<DaySummaryCard
			v-if="!history.range.value"
			:entries="todayDay?.entries ?? []"
			:goals="todayDay?.goals ?? null"
			:date="today"
			:loading="!todayDay"
			title="Heute"
		>
			<template #actions>
				<BaseLink
					route-name="diary-food-day"
					:params="{ date: today }"
					variant="no-decoration"
					class="text-highlight"
				>
					Zum Tag

					<BaseIcon
						:icon="ArrowRightIcon"
						:size="18"
					/>
				</BaseLink>
			</template>
		</DaySummaryCard>

		<div class="content-column gap-6">
			<WeekRangeSection
				v-if="history.showsRange.value"
				:range="history.range.value"
				:total="history.total.value"
				@change="history.setRange"
			/>

			<!-- Same as the weight list: one week per block, the newest open -->
			<div
				class="week-list"
				:aria-busy="loading"
			>
				<details
					v-for="(week, index) in weeks"
					:key="week.start"
					class="week-list__week week-list__week--collapsible"
					:open="index === 0"
				>
					<summary class="week-list__toggle">
						<span class="flex flex-col flex-1 min-w-0 py-1">
							<span class="week-list__title">
								{{ formatCalendarWeekTitle(week.start) }}
							</span>

							<span class="week-list__meta">
								<template v-if="week.averageKcal !== null">
									Schnitt {{ formatNumber(Math.round(week.averageKcal)) }} kcal,
								</template>

								{{ dayCountLabel(week) }}
							</span>
						</span>

						<BaseIcon
							class="week-list__chevron"
							:icon="ChevronDownIcon"
						/>
					</summary>

					<ol class="data-list mt-2">
						<li
							v-for="day in week.days"
							:key="day.date"
						>
							<RouterLink
								:to="{ name: 'diary-food-day', params: { date: day.date } }"
								class="data-list__row data-list__row--link"
							>
								<!-- The day keeps its width, the note beside it wraps instead -->
								<span class="data-list__label flex-none">
									{{ formatRelativeDay(day.date) }}

									<span
										v-if="day.entryCount && goalNote(day)"
										class="data-list__meta md:hidden"
									>
										{{ goalNote(day) }}
									</span>
								</span>

								<span
									v-if="day.entryCount && goalNote(day)"
									class="data-list__aside max-md:hidden"
								>
									{{ goalNote(day) }}
								</span>

								<span class="flex flex-1 items-center justify-end gap-2 min-w-0">
									<span
										v-if="day.entryCount"
										class="data-list__value"
									>
										{{ formatNumber(day.kcal) }} kcal
									</span>

									<span
										v-else
										class="data-list__aside text-right whitespace-normal"
									>
										Nichts eingetragen
									</span>

									<BaseIcon
										class="shrink-0 text-muted-foreground"
										:icon="ChevronRightIcon"
										:size="18"
									/>
								</span>
							</RouterLink>
						</li>
					</ol>
				</details>
			</div>

			<BaseButton
				v-if="history.canLoadMore.value"
				class="self-center"
				:disabled="loading"
				@click="history.loadMore"
			>
				{{ WEEKS_PER_PAGE }} weitere Wochen laden
			</BaseButton>
		</div>
	</main>
</template>

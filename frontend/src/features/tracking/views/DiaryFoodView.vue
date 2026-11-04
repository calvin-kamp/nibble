<script setup lang="ts">
import type {
	DiaryDay,
	DiaryDayWeek,
	NutritionGoals,
	TrackedDay,
} from '@features/tracking/tracking.types'

import { ArrowRightIcon, ChevronRightIcon, PlusIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import DaySummaryCard from '@features/tracking/components/DaySummaryCard.vue'
import { BaseButton, BaseIcon, BaseLink } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { fetchCurrentGoals, fetchDayRange } from '@features/tracking/tracking.api'
import { averageKcal, formatCalendarWeekTitle, weekStart } from '@features/tracking/tracking.utils'
import { addDays, formatRelativeDay, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

// Five weeks at once and five more per click, each load one request for the whole range
const WEEKS_PER_LOAD = 5

const { openEntry } = useTrackingDialogs()

const today = toIsoDate()
const thisWeek = weekStart(today)

const goals = ref<NutritionGoals | null>(null)
const days = ref<TrackedDay[]>([])
const weekCount = ref<number>(WEEKS_PER_LOAD)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

function oldestDay(count: number): string {
	return addDays(thisWeek, -7 * (count - 1))
}

watch(
	[weekCount, useTrackingChanges()],
	async () => {
		loading.value = true

		try {
			const [current, loaded] = await Promise.all([
				fetchCurrentGoals(),
				fetchDayRange(oldestDay(weekCount.value), today),
			])

			goals.value = current
			days.value = loaded
			loadError.value = false
		} catch {
			loadError.value = true
		} finally {
			loading.value = false
		}
	},
	{ immediate: true },
)

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

function loadMore(): void {
	weekCount.value += WEEKS_PER_LOAD
}

// The API knows no oldest entry, and entries may be dated before registration. So more weeks
// are only offered while the last loaded batch had entries before today: a new account, or
// five empty weeks in a row, ends the list. Single days stay reachable via the day view.
const hasOlderEntries = computed<boolean>(() => {
	const from = oldestDay(weekCount.value)
	const until =
		weekCount.value === WEEKS_PER_LOAD ? today : oldestDay(weekCount.value - WEEKS_PER_LOAD)

	return days.value.some((day) => day.date >= from && day.date < until && day.entries.length)
})
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

		<DaySummaryCard
			v-if="todayDay"
			:entries="todayDay.entries"
			:goals="todayDay.goals"
			:date="today"
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

		<div class="content-column gap-12">
			<div
				class="week-list"
				:aria-busy="loading"
			>
				<section
					v-for="week in weeks"
					:key="week.start"
					class="week-list__week"
					:aria-labelledby="`week-${week.start}-title`"
				>
					<div class="week-list__header">
						<h2
							:id="`week-${week.start}-title`"
							class="week-list__title"
							tabindex="-1"
						>
							{{ formatCalendarWeekTitle(week.start) }}
						</h2>

						<p
							v-if="week.averageKcal !== null"
							class="week-list__meta"
						>
							Schnitt

							<strong class="whitespace-nowrap text-foreground tabular-nums">
								{{ formatNumber(Math.round(week.averageKcal)) }} kcal
							</strong>
						</p>
					</div>

					<ol class="data-list">
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
				</section>
			</div>

			<BaseButton
				v-if="hasOlderEntries || (loading && weekCount > WEEKS_PER_LOAD)"
				class="self-center"
				:disabled="loading"
				@click="loadMore"
			>
				{{ WEEKS_PER_LOAD }} weitere Wochen laden
			</BaseButton>

			<p
				v-else-if="!loading && !loadError"
				class="self-center text-muted-foreground"
			>
				Keine älteren Einträge.
			</p>
		</div>
	</main>
</template>

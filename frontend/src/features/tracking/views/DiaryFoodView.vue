<script setup lang="ts">
import type {
	DiaryDay,
	DiaryDayWeek,
	DiaryWeek,
	NutritionGoals,
	TrackedDay,
} from '@features/tracking/tracking.types'

import { ChevronRightIcon, PlusIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import { BaseButton, BaseIcon } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { fetchCurrentGoals, fetchDays } from '@features/tracking/tracking.api'
import { averageKcal, weekStart } from '@features/tracking/tracking.utils'
import { addDays, formatDayRange, formatRelativeDay, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

// The backend only returns entries per day, so the list loads two weeks at once and older ones
// via "Ältere Wochen laden".
const WEEKS_PER_LOAD = 2

const { openEntry } = useTrackingDialogs()

const today = toIsoDate()
const thisWeek = weekStart(today)

const goals = ref<NutritionGoals | null>(null)
const days = ref<TrackedDay[]>([])
const weekCount = ref<number>(WEEKS_PER_LOAD)
const loading = ref<boolean>(true)
const loadError = ref<boolean>(false)

/** Days from today back to the Monday of the oldest loaded week, newest first */
function datesOf(count: number): string[] {
	const oldest = addDays(thisWeek, -7 * (count - 1))
	const dates: string[] = []

	for (let date = today; date >= oldest; date = addDays(date, -1)) dates.push(date)

	return dates
}

// After new or deleted entries, e.g. from the dialog, reload everything already loaded
watch(
	[weekCount, useTrackingChanges()],
	async () => {
		loading.value = true

		try {
			const [current, loaded] = await Promise.all([
				fetchCurrentGoals(),
				fetchDays(datesOf(weekCount.value)),
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

// Days with entries grouped by week. Today is always on top, even without an entry.
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

function weekTitle(week: DiaryWeek): string {
	if (week.start === thisWeek) return 'Diese Woche'
	if (week.start === addDays(thisWeek, -7)) return 'Letzte Woche'

	return formatDayRange(week.start, addDays(week.start, 6))
}

function loadMore(): void {
	weekCount.value += WEEKS_PER_LOAD
}
</script>

<template>
	<main class="content-wrapper pt-6 pb-10">
		<!-- Reading width like every diary page: date and calories stay close enough together -->
		<div class="content-column content-column--narrow gap-8">
			<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
				<div class="flex flex-col gap-3">
					<h1>Ernährung</h1>

					<p
						v-if="goals"
						class="text-lg text-muted"
					>
						Dein Tagesbedarf:
						<strong class="text-ink tabular-nums"
							>{{ formatNumber(goals.kcal) }} kcal</strong
						>
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

			<!-- Weeks instead of one long list: the heading carries the average, the days are quiet rows -->
			<div
				class="flex flex-col gap-8"
				:aria-busy="loading"
			>
				<section
					v-for="week in weeks"
					:key="week.start"
					class="flex flex-col gap-2"
					:aria-labelledby="`week-${week.start}-title`"
				>
					<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
						<h2
							:id="`week-${week.start}-title`"
							class="text-2xl outline-none"
							tabindex="-1"
						>
							{{ weekTitle(week) }}
						</h2>

						<p
							v-if="week.averageKcal !== null"
							class="text-sm text-muted"
						>
							Schnitt
							<strong class="text-ink tabular-nums"
								>{{ formatNumber(Math.round(week.averageKcal)) }} kcal</strong
							>
						</p>
					</div>

					<!-- A bar per day would just be noise across 28 rows. The number is enough; a note is only
               added where it says something. The arrow shows that every row leads to its day. -->
					<ol class="data-list">
						<li
							v-for="day in week.days"
							:key="day.date"
						>
							<RouterLink
								:to="{ name: 'diary-food-day', params: { date: day.date } }"
								class="data-list__row data-list__row--link"
							>
								<span class="data-list__label">{{
									formatRelativeDay(day.date)
								}}</span>

								<span
									v-if="day.entryCount && goalNote(day)"
									class="data-list__aside"
									>{{ goalNote(day) }}</span
								>

								<!-- The arrow sits closer to the value than the row gap -->
								<span class="flex items-center gap-2">
									<span
										v-if="day.entryCount"
										class="data-list__value"
										>{{ formatNumber(day.kcal) }} kcal</span
									>

									<span
										v-else
										class="data-list__aside"
										>Nichts eingetragen</span
									>

									<BaseIcon
										class="shrink-0 text-muted"
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
				class="self-start"
				variant="outline"
				:disabled="loading"
				@click="loadMore"
			>
				Ältere Wochen laden
			</BaseButton>
		</div>
	</main>
</template>

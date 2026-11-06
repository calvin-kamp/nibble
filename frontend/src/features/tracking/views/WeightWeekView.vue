<script setup lang="ts">
import type { WeightEntry } from '@features/tracking/tracking.types'

import { ChevronLeftIcon, ChevronRightIcon, PlusIcon, TrashIcon, WeightIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import WeightChart from '@features/tracking/components/WeightChart.vue'
import { BaseAlertDialog, BaseBreadcrumb, BaseButton, BaseEmptyState, BaseIcon } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { deleteWeightEntry, fetchWeightEntries } from '@features/tracking/tracking.api'
import {
	formatCalendarWeekTitle,
	formatKgChange,
	weekSlug,
	weekStart,
} from '@features/tracking/tracking.utils'
import {
	calendarWeek,
	addDays,
	formatDayRange,
	formatRelativeDay,
	formatWeekdayDate,
	toIsoDate,
} from '@shared/utils/date'
import { formatKg } from '@shared/utils/number'

interface Props {
	start: string
}

const props = defineProps<Props>()

const end = computed<string>(() => addDays(props.start, 6))
const title = computed<string>(() => formatCalendarWeekTitle(props.start))
const range = computed<string>(() => formatDayRange(props.start, end.value))

// "Diese Woche" and "Letzte Woche" do not say which week it is, so the number stands next to it
const weekNumber = computed<string>(() => `KW ${calendarWeek(props.start).week}`)
const lead = computed<string>(() =>
	title.value.startsWith('KW') ? range.value : `${weekNumber.value}, ${range.value}`,
)

usePageTitle(() => `${title.value} – Gewicht`)

// The dialog suggests a day of this week: today in the current week, else its Sunday
const entryDate = computed<string>(() => (nextWeek.value ? end.value : toIsoDate()))

const toast = useToast()
const { openEntry } = useTrackingDialogs()

const previousWeek = computed<string>(() => addDays(props.start, -7))
const nextWeek = computed<string | null>(() =>
	props.start < weekStart(toIsoDate()) ? addDays(props.start, 7) : null,
)

// The whole history: the week, the week before and the curve's weekly average need it
const entries = ref<WeightEntry[]>([])
const loaded = ref<boolean>(false)
const loadError = ref<boolean>(false)

watch(
	useTrackingChanges(),
	async () => {
		try {
			entries.value = await fetchWeightEntries()
			loadError.value = false
		} catch {
			loadError.value = true
		} finally {
			loaded.value = true
		}
	},
	{ immediate: true },
)

function entriesBetween(from: string, to: string): WeightEntry[] {
	return entries.value
		.filter((entry) => entry.date >= from && entry.date <= to)
		.toSorted((a, b) => b.date.localeCompare(a.date))
}

function average(list: WeightEntry[]): number | null {
	return list.length ? list.reduce((sum, entry) => sum + entry.kg, 0) / list.length : null
}

const weekEntries = computed(() => {
	const inWeek = entriesBetween(props.start, end.value)
	const sorted = entries.value.toSorted((a, b) => a.date.localeCompare(b.date))

	return inWeek.map((entry) => {
		const index = sorted.findIndex((other) => other.date === entry.date)
		const before = index > 0 ? sorted[index - 1] : undefined

		return { ...entry, difference: before ? entry.kg - before.kg : null }
	})
})

const weekAverage = computed<number | null>(() => average(weekEntries.value))
const previousAverage = computed<number | null>(() =>
	average(entriesBetween(previousWeek.value, addDays(props.start, -1))),
)

const lowest = computed<number | null>(() =>
	weekEntries.value.length ? Math.min(...weekEntries.value.map((entry) => entry.kg)) : null,
)
const highest = computed<number | null>(() =>
	weekEntries.value.length ? Math.max(...weekEntries.value.map((entry) => entry.kg)) : null,
)

const changeLabel = computed<string>(() => {
	if (weekAverage.value === null || previousAverage.value === null) return '–'

	return formatKgChange(weekAverage.value - previousAverage.value)
})

// The curve of this week, from Monday to the last entry. The weekly average uses only the
// days of the week as well, like every chart shows only the average of what it shows.
const chartEntries = computed<WeightEntry[]>(() => entriesBetween(props.start, end.value))
const chartDays = computed<number>(() => {
	const newest = weekEntries.value[0]

	if (!newest) return 7

	let days = 1

	while (addDays(props.start, days - 1) < newest.date) days++

	return days
})

const pendingDelete = ref<WeightEntry | null>(null)
const deleteOpen = ref<boolean>(false)

function askDelete(entry: WeightEntry): void {
	pendingDelete.value = entry
	deleteOpen.value = true
}

async function confirmDelete(): Promise<void> {
	const entry = pendingDelete.value

	if (!entry) return

	try {
		await deleteWeightEntry(entry.id)
		toast.show('Eintrag gelöscht', 'info')
	} catch {
		toast.show(
			'Der Eintrag konnte nicht gelöscht werden. Versuch es bitte noch einmal.',
			'danger',
		)
	}
}
</script>

<template>
	<main class="page page--compact">
		<BaseBreadcrumb
			:items="[{ label: 'Gewicht', routeName: 'diary-weight' }]"
			:current="title"
		/>

		<div class="page__header flex-nowrap gap-x-3">
			<div class="page__intro">
				<h1>
					{{ title }}
				</h1>

				<p class="page__lead">
					{{ lead }}
				</p>
			</div>

			<nav
				class="flex shrink-0 gap-2"
				aria-label="Wochen"
			>
				<BaseButton
					variant="outline"
					size="icon"
					route-name="diary-weight-week"
					:params="{ week: weekSlug(previousWeek) }"
					:aria-label="`Vorherige Woche: ${formatDayRange(previousWeek, addDays(previousWeek, 6))}`"
				>
					<BaseIcon :icon="ChevronLeftIcon" />
				</BaseButton>

				<BaseButton
					variant="outline"
					size="icon"
					:route-name="nextWeek ? 'diary-weight-week' : undefined"
					:params="nextWeek ? { week: weekSlug(nextWeek) } : undefined"
					:disabled="!nextWeek"
					:aria-label="
						nextWeek
							? `Nächste Woche: ${formatDayRange(nextWeek, addDays(nextWeek, 6))}`
							: 'Nächste Woche'
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
			Dein Gewicht konnte nicht geladen werden. Lad die Seite bitte neu.
		</p>

		<template v-else-if="loaded">
			<section
				v-if="weekEntries.length"
				class="card card__body flex flex-col gap-6 rounded-xl md:p-8"
				aria-labelledby="weight-week-summary-title"
			>
				<h2
					id="weight-week-summary-title"
					class="sr-only"
				>
					Zusammenfassung der Woche
				</h2>

				<WeightChart
					:entries="chartEntries"
					:days="chartDays"
					:height="220"
				/>

				<dl class="nutrition-facts nutrition-facts--lg">
					<div class="nutrition-facts__item">
						<dt class="nutrition-facts__label">
							Schnitt
						</dt>

						<dd class="nutrition-facts__value">
							{{ formatKg(weekAverage ?? 0) }}
						</dd>
					</div>

					<div class="nutrition-facts__item">
						<dt class="nutrition-facts__label">
							Zur Vorwoche
						</dt>

						<dd class="nutrition-facts__value">
							{{ changeLabel }}
						</dd>
					</div>

					<div class="nutrition-facts__item">
						<dt class="nutrition-facts__label">
							Niedrigster Wert
						</dt>

						<dd class="nutrition-facts__value">
							{{ formatKg(lowest ?? 0) }}
						</dd>
					</div>

					<div class="nutrition-facts__item">
						<dt class="nutrition-facts__label">
							Höchster Wert
						</dt>

						<dd class="nutrition-facts__value">
							{{ formatKg(highest ?? 0) }}
						</dd>
					</div>
				</dl>
			</section>

			<section
				class="content-column gap-4"
				aria-labelledby="weight-week-entries-title"
			>
				<div class="flex flex-wrap items-center justify-between gap-3">
					<h2 id="weight-week-entries-title">
						Einträge
					</h2>

					<BaseButton
						v-if="weekEntries.length"
						variant="outline"
						size="sm"
						@click="openEntry('weight', { date: entryDate })"
					>
						<BaseIcon
							:icon="PlusIcon"
							:size="16"
						/>

						Gewicht eintragen
					</BaseButton>
				</div>

				<ol
					v-if="weekEntries.length"
					class="data-list data-list--card"
				>
					<li
						v-for="entry in weekEntries"
						:key="entry.date"
						class="data-list__row"
					>
						<span class="data-list__label">
							{{ formatRelativeDay(entry.date) }}

							<span
								v-if="entry.difference !== null"
								class="data-list__meta"
							>
								{{ formatKgChange(entry.difference) }} zum Eintrag davor
							</span>
						</span>

						<span class="data-list__value">
							{{ formatKg(entry.kg) }}
						</span>

						<BaseButton
							class="-my-1 shrink-0"
							variant="danger-soft"
							size="icon"
							:aria-label="`Eintrag vom ${formatWeekdayDate(entry.date)} löschen`"
							@click="askDelete(entry)"
						>
							<BaseIcon
								:icon="TrashIcon"
								:size="18"
							/>
						</BaseButton>
					</li>
				</ol>

				<BaseEmptyState
					v-else
					:icon="WeightIcon"
					title="Keine Einträge in dieser Woche"
				>
					Am besten wiegst du dich morgens vor dem Frühstück. Ein Eintrag pro Tag reicht.

					<template #actions>
						<BaseButton @click="openEntry('weight', { date: entryDate })">
							<BaseIcon :icon="PlusIcon" />

							Gewicht eintragen
						</BaseButton>
					</template>
				</BaseEmptyState>
			</section>
		</template>

		<BaseAlertDialog
			v-model:open="deleteOpen"
			title="Eintrag löschen?"
			:description="
				pendingDelete
					? `Das Gewicht vom ${formatWeekdayDate(pendingDelete.date)} verschwindet aus deinem Verlauf.`
					: ''
			"
			confirm-label="Löschen"
			variant="danger"
			@confirm="confirmDelete"
		/>
	</main>
</template>

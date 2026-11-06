<script setup lang="ts">
import type {
	WeightEntry,
	WeightPoint,
	WeightWeekSummary,
} from '@features/tracking/tracking.types'
import type { SelectOption } from '@shared/ui/types'

import { ArrowRightIcon, ChevronDownIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import WeekRangeSection from '@features/tracking/components/WeekRangeSection.vue'
import WeightChart from '@features/tracking/components/WeightChart.vue'
import { BaseAlertDialog, BaseButton, BaseIcon, BaseLink, BaseSelect } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useWeekHistory, WEEKS_PER_PAGE } from '@features/tracking/composables/week-history'
import { useToast } from '@shared/composables/toast'

import {
	deleteWeightEntry,
	fetchWeightEntries,
	fetchWeightWeeks,
} from '@features/tracking/tracking.api'
import { WEIGHT_PERIODS } from '@features/tracking/tracking.constants'
import {
	buildWeightPoints,
	formatKgChange,
	formatPeriodChange,
	formatCalendarWeekTitle,
	getPeriodChange,
	weekSlug,
} from '@features/tracking/tracking.utils'
import { addDays, formatRelativeDay, formatWeekdayDate } from '@shared/utils/date'
import { formatKg, formatNumber } from '@shared/utils/number'

const DEFAULT_PERIOD = '30'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { openEntry } = useTrackingDialogs()

const PERIOD_OPTIONS: SelectOption[] = WEIGHT_PERIODS.map((period) => ({
	value: period.value,
	label: period.label,
}))

const period = computed(
	() =>
		WEIGHT_PERIODS.find((item) => item.value === route.query.zeitraum) ??
		WEIGHT_PERIODS.find((item) => item.value === DEFAULT_PERIOD)!,
)

const periodValue = computed<string | undefined>({
	get: () => period.value.value,
	set: (value) => {
		router.replace({
			query: { ...route.query, zeitraum: value === DEFAULT_PERIOD ? undefined : value },
		})
	},
})

const entries = ref<WeightEntry[]>([])
const loadError = ref<boolean>(false)

watch(
	useTrackingChanges(),
	async () => {
		try {
			entries.value = await fetchWeightEntries()
			loadError.value = false
		} catch {
			loadError.value = true
		}
	},
	{ immediate: true },
)

const points = computed<WeightPoint[]>(() => buildWeightPoints(entries.value))
const latest = computed<WeightPoint | undefined>(() => points.value[points.value.length - 1])
const change = computed<number | null>(() => getPeriodChange(points.value, period.value.days))

// The list does not depend on the chart's range: it shows weeks with entries, five at once
const history = useWeekHistory<WeightWeekSummary>(fetchWeightWeeks)

const sortedEntries = computed<WeightEntry[]>(() =>
	entries.value.toSorted((a, b) => a.date.localeCompare(b.date)),
)

const weeks = computed(() =>
	history.weeks.value.map((week) => {
		const end = addDays(week.start, 6)
		const weekEntries = sortedEntries.value
			.map((entry, index) => ({
				id: entry.id,
				date: entry.date,
				kg: entry.kg,
				difference: index > 0 ? entry.kg - sortedEntries.value[index - 1]!.kg : null,
			}))
			.filter((entry) => entry.date >= week.start && entry.date <= end)
			.toReversed()

		return { start: week.start, average: week.average, count: week.count, entries: weekEntries }
	}),
)

function entryCountLabel(count: number): string {
	return count === 1 ? '1 Eintrag' : `${count} Einträge`
}

const rangeLabel = computed<string | null>(() => {
	const range = history.range.value

	return range ? `${formatWeekdayDate(range.from)} bis ${formatWeekdayDate(range.to)}` : null
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
	<main class="page">
		<div class="page__header">
			<h1>
				Gewicht
			</h1>

			<BaseButton @click="openEntry('weight')">
				<BaseIcon :icon="PlusIcon" />

				Gewicht eintragen
			</BaseButton>
		</div>

		<section
			class="card card__body flex flex-col gap-6 rounded-xl md:p-8"
			aria-labelledby="weight-history-title"
		>
			<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
				<div class="flex flex-col gap-2">
					<h2
						id="weight-history-title"
						class="card__title"
					>
						Verlauf
					</h2>

					<p
						v-if="latest"
						class="figure figure--2xl"
					>
						{{ formatNumber(latest.kg, 1) }}<span class="figure__unit">
							kg
						</span>
					</p>

					<p
						class="font-semibold text-foreground/80"
						role="status"
					>
						{{
							change === null
								? `Zu wenige Einträge ${period.phrase}`
								: formatPeriodChange(change, period)
						}}
					</p>
				</div>

				<div class="field w-full sm:w-56">
					<label
						for="weight-period"
						class="field__label"
					>
						Zeitraum
					</label>

					<BaseSelect
						id="weight-period"
						v-model="periodValue"
						:options="PERIOD_OPTIONS"
					/>
				</div>
			</div>

			<p
				v-if="loadError"
				class="notice notice--danger"
				role="alert"
			>
				Dein Gewicht konnte nicht geladen werden. Lad die Seite bitte neu.
			</p>

			<WeightChart
				:entries="entries"
				:days="period.days"
				:height="220"
			/>
		</section>

		<section
			class="content-column gap-6"
			aria-labelledby="weight-entries-title"
		>
			<div class="flex flex-col gap-4">
				<h2
					id="weight-entries-title"
					class="outline-none"
					tabindex="-1"
				>
					Einträge
				</h2>

				<WeekRangeSection
					v-if="history.showsRange.value"
					:range="history.range.value"
					:total="history.total.value"
					@change="history.setRange"
				/>

				<div
					v-if="weeks.length"
					class="week-list"
					:aria-busy="history.loading.value"
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
									{{
										formatCalendarWeekTitle(week.start)
									}}
								</span>

								<span class="week-list__meta">
									Schnitt {{ formatKg(week.average) }},

									{{ entryCountLabel(week.count) }}
								</span>
							</span>

							<BaseIcon
								class="week-list__chevron"
								:icon="ChevronDownIcon"
							/>
						</summary>

						<ol class="data-list mt-2">
							<li
								v-for="entry in week.entries"
								:key="entry.date"
								class="data-list__row"
							>
								<span class="data-list__label">
									{{ formatRelativeDay(entry.date) }}

									<span
										v-if="entry.difference !== null"
										class="data-list__meta"
									>
										{{ formatKgChange(entry.difference) }} zum Eintrag
										davor
									</span>
								</span>

								<span class="data-list__value">
									{{ formatKg(entry.kg) }}
								</span>

								<BaseButton
									class="-my-1"
									variant="danger-soft"
									size="icon-sm"
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

						<BaseLink
							class="mt-1"
							route-name="diary-weight-week"
							:params="{ week: weekSlug(week.start) }"
						>
							Woche ansehen

							<BaseIcon
								:icon="ArrowRightIcon"
								:size="18"
							/>
						</BaseLink>
					</details>
				</div>

				<p
					v-else-if="!history.loading.value"
					class="py-3 text-muted-foreground"
				>
					{{ history.range.value ? `Keine Einträge vom ${rangeLabel}.` : 'Noch keine Einträge.' }}
				</p>
			</div>

			<BaseButton
				v-if="history.canLoadMore.value"
				class="self-center"
				:disabled="history.loading.value"
				@click="history.loadMore"
			>
				{{ WEEKS_PER_PAGE }} weitere Wochen laden
			</BaseButton>
		</section>

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

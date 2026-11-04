<script setup lang="ts">
import type { WeightEntry, WeightPoint } from '@features/tracking/tracking.types'
import type { SelectOption } from '@shared/ui/types'

import { ArrowRightIcon, ChevronDownIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import WeightChart from '@features/tracking/components/WeightChart.vue'
import {
	BaseAlertDialog,
	BaseButton,
	BaseIcon,
	BaseLink,
	BasePagination,
	BaseSelect,
} from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useToast } from '@shared/composables/toast'

import { deleteWeightEntry, fetchWeightEntries } from '@features/tracking/tracking.api'
import { WEIGHT_PERIODS } from '@features/tracking/tracking.constants'
import {
	buildWeightPoints,
	formatKgChange,
	formatPeriodChange,
	formatCalendarWeekTitle,
	getPeriodChange,
	limitToDays,
	weekSlug,
	weekStart,
} from '@features/tracking/tracking.utils'
import { PAGE_SIZE } from '@shared/constants'
import { formatRelativeDay, formatWeekdayDate } from '@shared/utils/date'
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
		router.replace({ query: { zeitraum: value === DEFAULT_PERIOD ? undefined : value } })
	},
})

const page = computed<number>({
	get: () => {
		const value = Number(route.query.seite)

		return Number.isInteger(value) && value > 1 ? value : 1
	},
	set: (target) => {
		router.push({ query: { ...route.query, seite: target > 1 ? target : undefined } })
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

const periodEntries = computed(() => {
	const visible = limitToDays(points.value, period.value.days)

	return visible
		.map((point, index) => ({
			id: point.id,
			date: point.date,
			kg: point.kg,
			difference: index > 0 ? point.kg - visible[index - 1]!.kg : null,
		}))
		.toReversed()
})

type PeriodEntry = (typeof periodEntries.value)[number]

const weeks = computed(() => {
	const result: { start: string; entries: PeriodEntry[]; average: number }[] = []

	for (const entry of periodEntries.value) {
		const start = weekStart(entry.date)
		const week = result[result.length - 1]

		if (week?.start === start) week.entries.push(entry)
		else result.push({ start, entries: [entry], average: 0 })
	}

	for (const week of result) {
		week.average = week.entries.reduce((sum, entry) => sum + entry.kg, 0) / week.entries.length
	}

	return result
})

const visibleWeeks = computed(() =>
	weeks.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE),
)

function entryCountLabel(count: number): string {
	return count === 1 ? '1 Eintrag' : `${count} Einträge`
}

const entriesHeading = ref<HTMLElement | null>(null)

watch(page, async () => {
	await nextTick()
	entriesHeading.value?.focus()
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
					ref="entriesHeading"
					class="outline-none"
					tabindex="-1"
				>
					Einträge
				</h2>

				<div
					v-if="visibleWeeks.length"
					class="week-list"
				>
					<details
						v-for="(week, index) in visibleWeeks"
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

									{{ entryCountLabel(week.entries.length) }}
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
					v-else
					class="py-3 text-muted-foreground"
				>
					Keine Einträge {{ period.phrase }}.
				</p>
			</div>

			<BasePagination
				v-if="weeks.length > PAGE_SIZE"
				v-model:page="page"
				label="Seiten der Gewichtseinträge"
				:total="weeks.length"
				:items-per-page="PAGE_SIZE"
			/>
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

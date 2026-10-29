<script setup lang="ts">
import type { WeightEntry, WeightPoint } from '@features/tracking/tracking.types'
import type { SelectOption } from '@shared/ui/types'

import { PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import WeightChart from '@features/tracking/components/WeightChart.vue'
import { BaseAlertDialog, BaseButton, BaseIcon, BasePagination, BaseSelect } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { useToast } from '@shared/composables/toast'

import { deleteWeightEntry, fetchWeightEntries } from '@features/tracking/tracking.api'
import { WEIGHT_PERIODS } from '@features/tracking/tracking.constants'
import {
	buildWeightPoints,
	formatKgChange,
	formatPeriodChange,
	getPeriodChange,
	limitToDays,
} from '@features/tracking/tracking.utils'
import { formatRelativeDay, formatWeekdayDate } from '@shared/utils/date'
import { formatKg, formatNumber } from '@shared/utils/number'

const PAGE_SIZE = 10
const DEFAULT_PERIOD = '30'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { openEntry } = useTrackingDialogs()

// Range and page in the address, e.g. ?zeitraum=90. A new range replaces the history entry
// and starts again on page 1.
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

// The whole history; range and pages derive from it. Reload after new entries.
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

// Entries within the chosen range, newest first, with the difference to the previous entry
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

const visibleEntries = computed(() =>
	periodEntries.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE),
)

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
	<main class="content-wrapper flex flex-col gap-8 pt-6 pb-10">
		<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
			<h1>Gewicht</h1>

			<BaseButton @click="openEntry('weight')">
				<BaseIcon :icon="PlusIcon" />
				Gewicht eintragen
			</BaseButton>
		</div>

		<!-- The only surface on the page: the chart needs a calm background -->
		<section
			class="flex flex-col gap-6 px-5 py-6 rounded-xl bg-surface md:p-8"
			aria-labelledby="weight-history-title"
		>
			<div class="flex flex-wrap items-end justify-between gap-x-6 gap-y-4">
				<div class="flex flex-col gap-2">
					<h2
						id="weight-history-title"
						class="text-2xl"
					>
						Verlauf
					</h2>

					<p
						v-if="latest"
						class="font-display text-6xl font-extrabold leading-none tracking-[-0.03em] tabular-nums"
					>
						{{ formatNumber(latest.kg, 1)
						}}<span class="ml-1 font-sans text-xl tracking-normal">kg</span>
					</p>

					<!-- When the range changes, screen readers announce the new change -->
					<p
						class="font-semibold text-ink-soft"
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
						>Zeitraum</label
					>

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

		<!-- Narrower and centered: day and weight stay close enough together. Same structure as every list. -->
		<section
			class="content-column content-column--narrow gap-6"
			aria-labelledby="weight-entries-title"
		>
			<div class="flex flex-col gap-2">
				<h2
					id="weight-entries-title"
					ref="entriesHeading"
					class="text-2xl outline-none"
					tabindex="-1"
				>
					Einträge
				</h2>

				<ol
					v-if="visibleEntries.length"
					class="data-list"
				>
					<li
						v-for="entry in visibleEntries"
						:key="entry.date"
						class="data-list__row"
					>
						<span class="data-list__label">{{ formatRelativeDay(entry.date) }}</span>

						<span
							v-if="entry.difference !== null"
							class="data-list__aside"
							>{{ formatKgChange(entry.difference) }}</span
						>

						<span class="data-list__value">{{ formatKg(entry.kg) }}</span>

						<BaseButton
							class="-my-1"
							variant="ghost"
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

				<p
					v-else
					class="py-3 text-muted"
				>
					Keine Einträge {{ period.phrase }}.
				</p>
			</div>

			<BasePagination
				v-if="periodEntries.length > PAGE_SIZE"
				v-model:page="page"
				label="Seiten der Gewichtseinträge"
				:total="periodEntries.length"
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

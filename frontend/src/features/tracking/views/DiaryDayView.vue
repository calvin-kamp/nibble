<script setup lang="ts">
import type { FoodEntry, MealType, NutritionGoals } from '@features/tracking/tracking.types'

import { ChevronLeftIcon, ChevronRightIcon, PencilIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import DaySummaryCard from '@features/tracking/components/DaySummaryCard.vue'
import FoodEntryEditForm from '@features/tracking/components/FoodEntryEditForm.vue'
import MacroList from '@features/tracking/components/MacroList.vue'
import { BaseAlertDialog, BaseBreadcrumb, BaseButton, BaseDialog, BaseIcon } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'
import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'
import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { deleteFoodEntry, fetchDay } from '@features/tracking/tracking.api'
import { MEAL_LABELS, MEAL_ORDER } from '@features/tracking/tracking.constants'
import { formatQuantity } from '@features/tracking/tracking.utils'
import { addDays, formatRelativeDay, formatWeekdayDate, toIsoDate } from '@shared/utils/date'
import { formatNumber } from '@shared/utils/number'

interface Props {
	date: string
}

const props = defineProps<Props>()

usePageTitle(() => `${formatRelativeDay(props.date)} – Essen`)

const toast = useToast()
const { openEntry } = useTrackingDialogs()

const entries = ref<FoodEntry[]>([])
const goals = ref<NutritionGoals | null>(null)
const loadError = ref<boolean>(false)
// The summary keeps its layout until the shown day has loaded
const loadedDate = ref<string | null>(null)

watch(
	[() => props.date, useTrackingChanges()],
	async ([date]) => {
		try {
			const day = await fetchDay(date)

			if (day.date !== props.date) return

			entries.value = day.entries
			goals.value = day.goals
			loadedDate.value = day.date
			loadError.value = false
		} catch {
			loadError.value = true
		}
	},
	{ immediate: true },
)

const previousDay = computed<string>(() => addDays(props.date, -1))
const nextDay = computed<string | null>(() =>
	props.date < toIsoDate() ? addDays(props.date, 1) : null,
)

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

// Like deleting: the entry stays set while the dialog fades out
const pendingEdit = ref<FoodEntry | null>(null)
const editOpen = ref<boolean>(false)

function openEdit(entry: FoodEntry): void {
	pendingEdit.value = entry
	editOpen.value = true
}

function onEdited(entry: FoodEntry): void {
	editOpen.value = false
	toast.show(
		entry.date === props.date
			? `${entry.name} geändert`
			: `${entry.name} verschoben auf ${formatWeekdayDate(entry.date)}`,
	)
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
	<main class="page page--compact">
		<BaseBreadcrumb
			:items="[{ label: 'Essen', routeName: 'diary-food' }]"
			:current="formatRelativeDay(props.date)"
		/>

		<div class="page__header flex-nowrap gap-x-3">
			<div class="page__intro">
				<h1>
					{{ formatRelativeDay(props.date) }}
				</h1>

				<p class="page__lead">
					{{ formatWeekdayDate(props.date) }}
				</p>
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
			<DaySummaryCard
				:entries="entries"
				:goals="goals"
				:date="props.date"
				:loading="loadedDate !== props.date"
				title-hidden
			/>

			<div class="content-column week-list">
				<section
					v-for="meal in meals"
					:key="meal.meal"
					class="week-list__week gap-3"
					:aria-labelledby="`meal-${meal.meal}-title`"
				>
					<div class="flex items-center justify-between gap-4">
						<div class="flex flex-col min-w-0">
							<h2
								:id="`meal-${meal.meal}-title`"
								class="text-xl"
							>
								{{ meal.label }}
							</h2>

							<p
								v-if="meal.entries.length"
								class="text-md tabular-nums text-muted-foreground"
							>
								{{ formatNumber(meal.kcal) }} kcal
							</p>
						</div>

						<BaseButton
							class="shrink-0 max-md:w-9 max-md:px-0"
							variant="outline"
							size="sm"
							@click="addTo(meal.meal)"
						>
							<BaseIcon
								:icon="PlusIcon"
								:size="18"
							/>

							<span class="max-md:sr-only">
								Hinzufügen
							</span>

							<span class="sr-only">
								{{ meal.label }}
							</span>
						</BaseButton>
					</div>

					<ul
						v-if="meal.entries.length"
						class="data-list"
					>
						<li
							v-for="entry in meal.entries"
							:key="entry.id"
							class="data-list__row grid grid-cols-[minmax(0,1fr)_auto] items-start gap-x-4 gap-y-2 md:grid-cols-[minmax(0,1fr)_auto_auto]"
						>
							<!-- Phones: name and actions, then kcal and macros below in the full
								width. From tablet on the kcal sit next to the name. -->
							<div class="data-list__label gap-0.5 col-start-1 row-start-1">
								<span class="font-semibold text-foreground">
									{{
										entry.name
									}}
								</span>

								<span
									v-if="entry.brand || entry.quantity || entry.source === 'manual'"
									class="data-list__meta"
								>
									{{
										[
											entry.brand,
											entry.quantity &&
												formatQuantity(entry.quantity),
											entry.source === 'manual' && 'Selbst eingetragen',
										]
											.filter(Boolean)
											.join(' – ')
									}}
								</span>
							</div>

							<span class="data-list__value col-span-2 row-start-2 md:col-span-1 md:col-start-2 md:row-start-1">
								{{ formatNumber(entry.kcal) }} kcal
							</span>

							<MacroList
								class="col-span-2 row-start-3 md:row-start-2"
								inline
								:macros="entry"
							/>

							<div class="flex gap-1 -my-1 col-start-2 row-start-1 md:col-start-3 md:row-span-2">
								<BaseButton
									variant="ghost"
									size="icon-sm"
									:aria-label="`${entry.name} bearbeiten`"
									@click="openEdit(entry)"
								>
									<BaseIcon
										:icon="PencilIcon"
										:size="18"
									/>
								</BaseButton>

								<BaseButton
									variant="danger-soft"
									size="icon-sm"
									:aria-label="`${entry.name} löschen`"
									@click="askDelete(entry)"
								>
									<BaseIcon
										:icon="TrashIcon"
										:size="18"
									/>
								</BaseButton>
							</div>
						</li>
					</ul>

					<p
						v-else
						class="text-foreground/80"
					>
						Noch nichts eingetragen.
					</p>
				</section>
			</div>
		</div>

		<BaseDialog
			v-model:open="editOpen"
			title="Eintrag bearbeiten"
			:description="pendingEdit?.name"
		>
			<FoodEntryEditForm
				v-if="pendingEdit"
				:key="pendingEdit.id"
				:entry="pendingEdit"
				@saved="onEdited"
				@cancel="editOpen = false"
			/>
		</BaseDialog>

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

<script setup lang="ts">
import type { WeightEntry } from '@features/tracking/tracking.types'

import { ArrowRightIcon } from '@lucide/vue'
import { computed } from 'vue'

import WeightChart from '@features/tracking/components/WeightChart.vue'
import WeightSummary from '@features/tracking/components/WeightSummary.vue'
import { BaseCard, BaseIcon, BaseLink } from '@shared/ui'

import { toTime } from '@features/tracking/tracking.utils'
import { formatDayMonth } from '@shared/utils/date'
import { formatKg } from '@shared/utils/number'

interface Props {
	entries: WeightEntry[]
	days?: number
	latestCount?: number
}

const props = withDefaults(defineProps<Props>(), {
	days: 7,
	latestCount: 5,
})

const latestEntries = computed<WeightEntry[]>(() =>
	props.entries.toSorted((a, b) => b.date.localeCompare(a.date)).slice(0, props.latestCount),
)
</script>

<template>
	<BaseCard
		as="section"
		size="lg"
		aria-labelledby="weight-card-title"
	>
		<div class="grid grid-cols-12 gap-y-8 xl:gap-x-10">
			<div class="flex flex-col gap-6 col-span-12 min-w-0 xl:col-span-8">
				<div class="flex flex-col gap-3">
					<h2
						id="weight-card-title"
						class="card__title"
					>
						Gewicht
					</h2>

					<WeightSummary :entries="props.entries" />
				</div>

				<WeightChart
					:entries="props.entries"
					:days="props.days"
				/>
			</div>

			<div class="flex flex-col gap-4 col-span-12 pt-8 border-t border-divider xl:col-span-4 xl:pt-0 xl:pl-10 xl:border-t-0 xl:border-l">
				<div class="flex flex-col gap-2">
					<h3 class="font-sans text-lg font-semibold tracking-normal">
						Letzte Einträge
					</h3>

					<ul
						v-if="latestEntries.length"
						class="data-list"
					>
						<li
							v-for="entry in latestEntries"
							:key="entry.date"
							class="data-list__row"
						>
							<span class="data-list__label">
								{{
									formatDayMonth(new Date(toTime(entry.date)))
								}}
							</span>

							<span class="data-list__value">
								{{ formatKg(entry.kg) }}
							</span>
						</li>
					</ul>

					<p
						v-else
						class="text-foreground/80"
					>
						Noch keine Einträge.
					</p>
				</div>

				<BaseLink
					route-name="diary-weight"
					class="self-start mt-auto"
				>
					Zum Gewichtstagebuch

					<BaseIcon
						:icon="ArrowRightIcon"
						:size="16"
					/>
				</BaseLink>
			</div>
		</div>
	</BaseCard>
</template>

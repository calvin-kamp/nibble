<script setup lang="ts">
import type { WeekRange } from '@features/tracking/composables/week-history'

import { useId } from 'reka-ui'
import { computed } from 'vue'

import WeekRangeFilter from '@features/tracking/components/WeekRangeFilter.vue'

import { MAX_LOADED_WEEKS } from '@features/tracking/composables/week-history'

import { formatWeekdayDate } from '@shared/utils/date'

// Above the week lists of the diaries once there are more weeks than the list loads itself

interface Props {
	range: WeekRange | null
	/** Weeks with entries in the range, or all of them without one */
	total: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
	change: [range: WeekRange | null]
}>()

const titleId = useId(undefined, 'week-range-title')

const rangeLabel = computed<string | null>(() =>
	props.range
		? `${formatWeekdayDate(props.range.from)} bis ${formatWeekdayDate(props.range.to)}`
		: null,
)
</script>

<template>
	<!-- A card like the week list below, so it doesn't float on the page -->
	<section
		class="flex flex-col gap-4 p-5 border border-divider rounded-lg bg-card md:p-6"
		:aria-labelledby="titleId"
	>
		<div class="flex flex-col gap-1">
			<h3
				:id="titleId"
				class="week-list__title"
			>
				Zeitraum
			</h3>

			<p class="text-muted-foreground">
				<template v-if="rangeLabel">
					Wochen mit Einträgen vom {{ rangeLabel }}.
				</template>

				<template v-else>
					{{ props.total }} Wochen mit Einträgen. Die Liste zeigt bis zu

					{{ MAX_LOADED_WEEKS }}, ältere findest du über einen Zeitraum.
				</template>
			</p>
		</div>

		<WeekRangeFilter
			:key="rangeLabel ?? ''"
			:range="props.range"
			@change="emit('change', $event)"
		/>
	</section>
</template>

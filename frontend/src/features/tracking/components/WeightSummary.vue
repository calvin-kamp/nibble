<script setup lang="ts">
import type { WeightEntry, WeightPoint } from '@features/tracking/tracking.types'

import { computed } from 'vue'

import {
	buildWeightPoints,
	formatWeeklyBalance,
	getWeeklyBalance,
} from '@features/tracking/tracking.utils'
import { formatKg, formatNumber } from '@shared/utils/number'

interface Props {
	entries: WeightEntry[]
}

const props = defineProps<Props>()

const points = computed<WeightPoint[]>(() => buildWeightPoints(props.entries))
const latest = computed<WeightPoint | undefined>(() => points.value[points.value.length - 1])
const weeklyBalance = computed(() => getWeeklyBalance(points.value))
</script>

<template>
	<div
		v-if="latest"
		class="flex flex-col gap-2"
	>
		<p
			class="font-display text-6xl font-extrabold leading-none tracking-[-0.03em] tabular-nums"
		>
			{{ formatNumber(latest.kg, 1)
			}}<span class="ml-1 font-sans text-xl tracking-normal">kg</span>
		</p>

		<p
			v-if="weeklyBalance"
			class="text-md md:text-base"
		>
			<template v-if="weeklyBalance.balance !== null">
				{{ formatWeeklyBalance(weeklyBalance.balance) }},
			</template>

			Wochenschnitt {{ formatKg(weeklyBalance.average) }}
		</p>
	</div>
</template>

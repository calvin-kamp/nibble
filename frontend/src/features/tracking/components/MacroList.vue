<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed } from 'vue'

import { formatNumber } from '@shared/utils/number'

// Protein, carbs and fat spelled out and rounded to whole grams. The color dots tie the values
// to rings and bars. Stacked by default, the width is set by the consumer. inline puts them in
// one wrapping line, e.g. below an entry in a list.
interface Props {
	macros: Pick<Nutrition, 'protein' | 'carbs' | 'fat'>
	inline?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	inline: false,
})

const rows = computed(() => [
	{ label: 'Protein', grams: props.macros.protein, color: 'var(--color-macro-protein)' },
	{ label: 'Kohlenhydrate', grams: props.macros.carbs, color: 'var(--color-macro-carbs)' },
	{ label: 'Fett', grams: props.macros.fat, color: 'var(--color-macro-fat)' },
])
</script>

<template>
	<dl
		v-if="props.inline"
		class="flex flex-wrap gap-x-4 gap-y-1 text-sm tabular-nums"
	>
		<div
			v-for="row in rows"
			:key="row.label"
			class="flex items-center gap-1.5"
		>
			<dt class="flex items-center gap-1.5 text-muted">
				<span
					class="size-2 shrink-0 rounded-full"
					:style="{ backgroundColor: row.color }"
					aria-hidden="true"
				/>
				{{ row.label }}
			</dt>

			<dd class="font-semibold text-ink">{{ formatNumber(Math.round(row.grams)) }} g</dd>
		</div>
	</dl>

	<dl
		v-else
		class="data-list data-list--compact"
	>
		<div
			v-for="row in rows"
			:key="row.label"
			class="data-list__row"
		>
			<dt class="data-list__label flex-row items-center gap-2">
				<span
					class="size-2.5 shrink-0 rounded-full"
					:style="{ backgroundColor: row.color }"
					aria-hidden="true"
				/>
				{{ row.label }}
			</dt>

			<dd class="data-list__value">{{ formatNumber(Math.round(row.grams)) }} g</dd>
		</div>
	</dl>
</template>

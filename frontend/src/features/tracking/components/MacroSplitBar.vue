<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed } from 'vue'

import { KCAL_PER_GRAM } from '@features/calorie-calculator/calorie-calculator.constants'

// Shares of protein, carbs and fat in the calories as a bar. Purely visual: the numbers are
// always shown next to it, hence aria-hidden.
interface Props {
	macros: Pick<Nutrition, 'protein' | 'carbs' | 'fat'>
}

const props = defineProps<Props>()

const parts = computed(() => [
	{
		key: 'protein',
		kcal: props.macros.protein * KCAL_PER_GRAM.protein,
		color: 'var(--color-macro-protein)',
	},
	{
		key: 'carbs',
		kcal: props.macros.carbs * KCAL_PER_GRAM.carbs,
		color: 'var(--color-macro-carbs)',
	},
	{ key: 'fat', kcal: props.macros.fat * KCAL_PER_GRAM.fat, color: 'var(--color-macro-fat)' },
])
</script>

<template>
	<div
		class="flex h-3 gap-0.5 overflow-hidden rounded-full"
		aria-hidden="true"
	>
		<span
			v-for="part in parts"
			:key="part.key"
			class="h-full basis-0"
			:style="{ flexGrow: part.kcal, backgroundColor: part.color }"
		/>
	</div>
</template>

<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed } from 'vue'

import { formatAmount } from '@features/tracking/tracking.utils'
import { buildModifierClasses } from '@shared/utils/classes'
import { formatNumber } from '@shared/utils/number'

// Calories, protein, carbs and fat, spelled out and in the macro colors.
// Without values (e.g. while the amount is missing) a dash is shown.
interface Props {
	nutrition: Nutrition | null
	size?: 'default' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
	size: 'default',
})

const modifierClasses = computed<string[]>(() =>
	buildModifierClasses('nutrition-facts', [props.size]),
)

const facts = computed(() => {
	const values = props.nutrition

	return [
		{
			label: 'Kalorien',
			value: values ? `${formatNumber(values.kcal)} kcal` : '–',
			color: undefined,
		},
		{
			label: 'Protein',
			value: values ? `${formatAmount(values.protein)} g` : '–',
			color: 'var(--color-macro-protein)',
		},
		{
			label: 'Kohlenhydrate',
			value: values ? `${formatAmount(values.carbs)} g` : '–',
			color: 'var(--color-macro-carbs)',
		},
		{
			label: 'Fett',
			value: values ? `${formatAmount(values.fat)} g` : '–',
			color: 'var(--color-macro-fat)',
		},
	]
})
</script>

<template>
	<dl
		class="nutrition-facts"
		:class="modifierClasses"
	>
		<div
			v-for="fact in facts"
			:key="fact.label"
			class="nutrition-facts__item"
		>
			<dt class="nutrition-facts__label">
				<span
					v-if="fact.color"
					class="nutrition-facts__dot"
					:style="{ backgroundColor: fact.color }"
					aria-hidden="true"
				/>
				{{ fact.label }}
			</dt>

			<dd class="nutrition-facts__value">{{ fact.value }}</dd>
		</div>
	</dl>
</template>

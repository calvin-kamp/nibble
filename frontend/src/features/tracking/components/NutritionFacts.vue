<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed } from 'vue'

import { formatAmount } from '@features/tracking/tracking.utils'
import { buildModifierClasses } from '@shared/utils/classes'
import { formatNumber } from '@shared/utils/number'

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
			color: 'var(--macro-protein)',
		},
		{
			label: 'Kohlenhydrate',
			value: values ? `${formatAmount(values.carbs)} g` : '–',
			color: 'var(--macro-carbs)',
		},
		{
			label: 'Fett',
			value: values ? `${formatAmount(values.fat)} g` : '–',
			color: 'var(--macro-fat)',
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

				<span class="min-w-0">
					{{ fact.label }}
				</span>
			</dt>

			<dd class="nutrition-facts__value">
				{{ fact.value }}
			</dd>
		</div>
	</dl>
</template>

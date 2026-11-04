<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed, useId } from 'vue'

import { BaseCard } from '@shared/ui'

import { formatAmount } from '@features/tracking/tracking.utils'
import { formatNumber } from '@shared/utils/number'

interface Props {
	title: string
	nutrition: Nutrition
}

const props = defineProps<Props>()

const titleId = useId()

const macros = computed(() => [
	{ label: 'Protein', grams: props.nutrition.protein, color: 'var(--macro-protein)' },
	{
		label: 'Kohlen\u00ADhydrate',
		grams: props.nutrition.carbs,
		color: 'var(--macro-carbs)',
	},
	{ label: 'Fett', grams: props.nutrition.fat, color: 'var(--macro-fat)' },
])
</script>

<template>
	<BaseCard
		as="section"
		class="@container"
		variant="inverse"
		size="lg"
		:aria-labelledby="titleId"
	>
		<div class="flex flex-col gap-5 @4xl:flex-row @4xl:items-center @4xl:gap-10">
			<div class="flex flex-col gap-1 shrink-0">
				<h2
					:id="titleId"
					class="text-xl text-forest-foreground"
				>
					{{ props.title }}
				</h2>

				<p class="figure figure--2xl flex flex-wrap items-baseline gap-x-2 text-highlight">
					{{ formatNumber(props.nutrition.kcal) }}

					<span class="font-sans text-lg font-bold tracking-normal text-forest-muted-foreground">
						kcal
					</span>
				</p>
			</div>

			<dl class="flex-1 @md:grid @md:grid-cols-12 @md:gap-6">
				<div
					v-for="macro in macros"
					:key="macro.label"
					class="flex flex-col gap-0.5 py-2.5 border-t border-forest-border @md:col-span-4 @md:py-1 @md:pl-5 @md:border-t-0 @md:border-l @md:first:pl-0 @md:first:border-l-0 @4xl:first:pl-5 @4xl:first:border-l"
				>
					<dt class="flex items-center gap-2 min-w-0">
						<span
							class="size-2.5 shrink-0 rounded-full"
							:style="{ backgroundColor: macro.color }"
							aria-hidden="true"
						/>

						{{ macro.label }}
					</dt>

					<dd class="font-bold whitespace-nowrap tabular-nums text-forest-foreground @md:font-display @md:text-3xl @md:font-bold @md:tracking-tighter">
						{{ formatAmount(macro.grams) }} g
					</dd>
				</div>
			</dl>
		</div>
	</BaseCard>
</template>

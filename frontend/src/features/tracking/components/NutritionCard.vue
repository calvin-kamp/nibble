<script setup lang="ts">
import type { Nutrition } from '@features/tracking/tracking.types'

import { computed, useId } from 'vue'

import { BaseCard } from '@shared/ui'

import { formatAmount } from '@features/tracking/tracking.utils'
import { formatNumber } from '@shared/utils/number'

// Green card with nutrition values, e.g. per serving of a recipe or for a whole meal
interface Props {
	title: string
	nutrition: Nutrition
}

const props = defineProps<Props>()

const titleId = useId()

const macros = computed(() => [
	{ label: 'Protein', grams: props.nutrition.protein, color: 'var(--color-macro-protein)' },
	{ label: 'Kohlenhydrate', grams: props.nutrition.carbs, color: 'var(--color-macro-carbs)' },
	{ label: 'Fett', grams: props.nutrition.fat, color: 'var(--color-macro-fat)' },
])
</script>

<template>
	<!-- @container: the card is sometimes full width (recipe), sometimes in the narrow column
       (meal). It adapts to its own space, not to the screen. -->
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
					class="text-xl text-white"
				>
					{{ props.title }}
				</h2>

				<p
					class="font-display text-6xl font-extrabold leading-none tracking-tighter tabular-nums text-lime"
				>
					{{ formatNumber(props.nutrition.kcal) }}

					<span class="font-sans text-lg font-bold tracking-normal text-on-forest-muted"
						>kcal</span
					>
				</p>
			</div>

			<!-- Narrow: one row per macro. Wider: three columns with dividers -->
			<dl class="flex-1 @md:grid @md:grid-cols-12 @md:gap-6">
				<div
					v-for="macro in macros"
					:key="macro.label"
					class="flex justify-between gap-4 py-2.5 border-t border-white/20 @md:col-span-4 @md:flex-col @md:gap-0.5 @md:py-1 @md:pl-5 @md:border-t-0 @md:border-l @md:first:pl-0 @md:first:border-l-0 @4xl:first:pl-5 @4xl:first:border-l"
				>
					<dt class="flex items-center gap-2">
						<span
							class="size-2.5 shrink-0 rounded-full"
							:style="{ backgroundColor: macro.color }"
							aria-hidden="true"
						/>
						{{ macro.label }}
					</dt>

					<dd
						class="font-bold whitespace-nowrap tabular-nums text-white @md:font-display @md:text-3xl @md:font-extrabold @md:tracking-tighter"
					>
						{{ formatAmount(macro.grams) }} g
					</dd>
				</div>
			</dl>
		</div>
	</BaseCard>
</template>

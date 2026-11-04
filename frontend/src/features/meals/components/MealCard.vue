<script setup lang="ts">
import type { SavedMeal } from '@features/meals/meals.types'

import { RouterLink } from 'vue-router'

import MacroList from '@features/tracking/components/MacroList.vue'
import { BaseCard } from '@shared/ui'

import { formatNumber } from '@shared/utils/number'

interface Props {
	meal: SavedMeal
}

const props = defineProps<Props>()
</script>

<template>
	<BaseCard
		as="article"
		stretch
		class="relative hover:ring-2 hover:ring-green-500 has-[a:focus-visible]:ring-3 has-[a:focus-visible]:ring-ring"
	>
		<div class="flex flex-col flex-1 gap-3">
			<h2 class="text-xl">
				<RouterLink
					:to="{ name: 'meal-detail', params: { id: props.meal.id } }"
					class="after:absolute after:inset-0 focus-visible:outline-none"
				>
					{{ props.meal.name }}
				</RouterLink>
			</h2>

			<MacroList :macros="props.meal" />

			<div class="flex items-center justify-between gap-3 pt-4 mt-auto border-t border-divider">
				<p class="text-foreground/80">
					<strong class="figure figure--lg text-foreground">
						{{ formatNumber(props.meal.kcal) }}
					</strong>

					kcal
				</p>
			</div>
		</div>
	</BaseCard>
</template>

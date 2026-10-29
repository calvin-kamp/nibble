<script setup lang="ts">
import type { SavedMeal } from '@features/meals/meals.types'

import { PlusIcon } from '@lucide/vue'
import { RouterLink } from 'vue-router'

import MacroList from '@features/tracking/components/MacroList.vue'
import { BaseButton, BaseCard, BaseIcon } from '@shared/ui'

import { useTrackingDialogs } from '@features/tracking/composables/tracking-dialogs'

import { formatNumber } from '@shared/utils/number'

// Name, macros, calories and the way to log it. The user knows what is in it; the contents are
// on the meal's own page.
interface Props {
	meal: SavedMeal
}

const props = defineProps<Props>()

const { openEntry } = useTrackingDialogs()
</script>

<template>
	<!-- The whole card links to the meal. "Eintragen" sits on top and stays a separate button. -->
	<BaseCard
		as="article"
		stretch
		class="relative hover:ring-2 hover:ring-leaf has-[a:focus-visible]:ring-3 has-[a:focus-visible]:ring-brand-ink"
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

			<!-- mt-auto: in a row, calories and button line up regardless of how long the name is -->
			<div
				class="flex items-center justify-between gap-3 pt-4 mt-auto border-t border-divider"
			>
				<p class="text-ink-soft">
					<strong
						class="font-display text-3xl font-extrabold tracking-tighter tabular-nums text-ink"
					>
						{{ formatNumber(props.meal.kcal) }}
					</strong>
					kcal
				</p>

				<BaseButton
					class="relative z-1"
					variant="outline"
					size="sm"
					@click="openEntry('food', { savedMealId: props.meal.id })"
				>
					<BaseIcon
						:icon="PlusIcon"
						:size="16"
					/>

					Eintragen<span class="sr-only">: {{ props.meal.name }}</span>
				</BaseButton>
			</div>
		</div>
	</BaseCard>
</template>

<script setup lang="ts">
import type { Recipe } from '@features/recipes/recipes.types'

import { MinusIcon, PlusIcon } from '@lucide/vue'
import { ref, watch } from 'vue'

import { BaseButton, BaseCard, BaseIcon } from '@shared/ui'

import { MAX_SERVINGS, MIN_SERVINGS } from '@features/recipes/recipes.constants'
import { formatAmount } from '@features/recipes/recipes.utils'

interface Props {
	recipe: Recipe
}

const props = defineProps<Props>()

const servings = ref<number>(props.recipe.servings)

watch(
	() => props.recipe.servings,
	(value) => (servings.value = value),
)
</script>

<template>
	<BaseCard
		as="section"
		aria-labelledby="recipe-ingredients-title"
	>
		<div class="flex flex-col gap-4">
			<h2
				id="recipe-ingredients-title"
				class="card__title"
			>
				Zutaten
			</h2>

			<div class="flex flex-col gap-2">
				<div class="flex items-center justify-between gap-2">
					<span
						id="recipe-servings-label"
						class="min-w-0 font-semibold"
					>
						Portionen
					</span>

					<div class="flex shrink-0 items-center gap-1 sm:gap-3">
						<BaseButton
							variant="outline"
							size="icon"
							aria-label="Eine Portion weniger"
							:disabled="servings <= MIN_SERVINGS"
							@click="servings--"
						>
							<BaseIcon :icon="MinusIcon" />
						</BaseButton>

						<output
							class="figure figure--md min-w-8 text-center"
							aria-labelledby="recipe-servings-label"
						>
							{{ servings }}
						</output>

						<BaseButton
							variant="outline"
							size="icon"
							aria-label="Eine Portion mehr"
							:disabled="servings >= MAX_SERVINGS"
							@click="servings++"
						>
							<BaseIcon :icon="PlusIcon" />
						</BaseButton>
					</div>
				</div>

				<ul class="data-list">
					<li
						v-for="(ingredient, index) in props.recipe.ingredients"
						:key="index"
						class="data-list__row"
					>
						<span class="data-list__label">
							{{ ingredient.name }}
						</span>

						<span class="data-list__value">
							{{
								formatAmount(
									ingredient.amount,
									ingredient.unit,
									servings,
									props.recipe.servings,
								)
							}}
						</span>
					</li>
				</ul>
			</div>
		</div>
	</BaseCard>
</template>

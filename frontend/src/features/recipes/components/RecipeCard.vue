<script setup lang="ts">
import type { RecipeSummary } from '@features/recipes/recipes.types'

import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import RecipeMedia from '@features/recipes/components/RecipeMedia.vue'
import { BaseCard } from '@shared/ui'

import { DIET_LABELS } from '@features/recipes/recipes.constants'
import { recipeParams } from '@features/recipes/recipes.utils'
import { formatNumber } from '@shared/utils/number'

interface Props {
	recipe: RecipeSummary
	index?: number
	headingLevel?: 2 | 3
}

const props = withDefaults(defineProps<Props>(), {
	index: 0,
	headingLevel: 3,
})

const MEDIA_COLORS = ['recipe-media--1', 'recipe-media--2', 'recipe-media--3', 'recipe-media--4']

const mediaColor = computed<string>(() => MEDIA_COLORS[props.index % MEDIA_COLORS.length]!)

const dietLabel = computed<string | null>(() => DIET_LABELS[props.recipe.diet])
</script>

<template>
	<BaseCard
		as="article"
		class="recipe-card"
	>
		<template #media>
			<RecipeMedia
				class="aspect-4/3"
				:class="mediaColor"
				:image-url="props.recipe.imageUrl"
			/>
		</template>

		<div class="flex flex-col gap-2.5">
			<ul class="flex flex-wrap gap-2">
				<li
					v-if="dietLabel"
					class="tag tag--accent"
				>
					{{ dietLabel }}
				</li>

				<li class="tag">
					{{ props.recipe.durationMinutes }} Min.
				</li>
			</ul>

			<div class="flex flex-col gap-1.5">
				<component
					:is="`h${props.headingLevel}`"
					class="recipe-card__title"
				>
					<RouterLink
						:to="{ name: 'recipe-detail', params: recipeParams(props.recipe) }"
						class="after:absolute after:inset-0 focus-visible:outline-none"
					>
						{{ props.recipe.title }}
					</RouterLink>
				</component>

				<p class="text-md text-foreground/80">
					<strong class="figure text-lg text-foreground">
						{{ formatNumber(props.recipe.kcalPerServing) }}
					</strong>

					kcal pro Portion
				</p>
			</div>
		</div>
	</BaseCard>
</template>

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
	/** Position in the list, determines the image's background color */
	index?: number
	/** 2 directly below the page title, 3 inside a section with its own heading */
	headingLevel?: 2 | 3
}

const props = withDefaults(defineProps<Props>(), {
	index: 0,
	headingLevel: 3,
})

const MEDIA_COLORS = ['bg-[#ffdcab]', 'bg-[#bfecce]', 'bg-[#ffd6c0]', 'bg-[#fff0b0]']

const mediaColor = computed<string>(() => MEDIA_COLORS[props.index % MEDIA_COLORS.length]!)

const dietLabel = computed<string | null>(() => DIET_LABELS[props.recipe.diet])
</script>

<template>
	<BaseCard
		as="article"
		class="relative hover:ring-2 hover:ring-leaf has-[a:focus-visible]:ring-3 has-[a:focus-visible]:ring-brand-ink"
	>
		<template #media>
			<RecipeMedia
				class="aspect-4/3"
				:class="mediaColor"
				:image-url="props.recipe.imageUrl"
			/>
		</template>

		<div class="flex flex-col gap-2.5">
			<ul class="flex flex-wrap gap-2 text-sm font-bold">
				<li
					v-if="dietLabel"
					class="px-3 py-0.5 rounded-full bg-brand-soft text-brand-ink"
				>
					{{ dietLabel }}
				</li>

				<li class="px-3 py-0.5 rounded-full bg-surface-muted text-ink">
					{{ props.recipe.durationMinutes }} Min.
				</li>
			</ul>

			<div class="flex flex-col gap-1.5">
				<component
					:is="`h${props.headingLevel}`"
					class="text-xl"
				>
					<!-- after:inset-0 makes the whole card clickable -->
					<RouterLink
						:to="{ name: 'recipe-detail', params: recipeParams(props.recipe) }"
						class="after:absolute after:inset-0 focus-visible:outline-none"
					>
						{{ props.recipe.title }}
					</RouterLink>
				</component>

				<p class="text-sm text-ink-soft">
					<strong class="font-display text-lg font-extrabold tabular-nums text-ink">
						{{ formatNumber(props.recipe.kcalPerServing) }}
					</strong>
					kcal pro Portion
				</p>
			</div>
		</div>
	</BaseCard>
</template>

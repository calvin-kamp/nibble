<script setup lang="ts">
import type { RecipeSummary } from '@features/recipes/recipes.types'

import { ArrowRightIcon } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'

import RecipeCard from '@features/recipes/components/RecipeCard.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { searchRecipes } from '@features/recipes/recipes.api'
import { EMPTY_FILTERS } from '@features/recipes/recipes.constants'

const COUNT = 3

const recipes = ref<RecipeSummary[]>([])
const loading = ref<boolean>(true)

// A single card looks like an empty shelf: the section only shows with a full row. Errors and
// an empty catalogue hide it as well, the hero already links to the recipes.
const isShown = computed<boolean>(() => loading.value || recipes.value.length >= COUNT)

onMounted(async () => {
	try {
		recipes.value = (await searchRecipes('all', EMPTY_FILTERS, 1)).recipes.slice(0, COUNT)
	} catch {
		recipes.value = []
	} finally {
		loading.value = false
	}
})
</script>

<template>
	<section
		v-if="isShown"
		class="section"
		aria-labelledby="landing-recipes-title"
	>
		<div class="section__header">
			<div class="section__intro">
				<h2 id="landing-recipes-title">
					Frisch aus der Community
				</h2>

				<p class="text-lg section__lead">
					Rezepte von Menschen, die auch auf ihre Ernährung achten. Jedes mit Nährwerten
					pro Portion, geprüft, bevor es online geht.
				</p>
			</div>

			<BaseButton
				variant="outline"
				route-name="recipe-list"
			>
				Alle Rezepte

				<BaseIcon :icon="ArrowRightIcon" />
			</BaseButton>
		</div>

		<ul
			v-if="loading"
			class="grid grid-cols-12 gap-6"
			aria-hidden="true"
		>
			<li
				v-for="index in COUNT"
				:key="index"
				class="col-span-12 overflow-hidden rounded-lg border border-divider bg-card sm:col-span-6 lg:col-span-4"
			>
				<span class="block aspect-4/3 bg-muted animate-pulse" />

				<span class="block h-24" />
			</li>
		</ul>

		<ul
			v-else-if="recipes.length"
			class="grid grid-cols-12 gap-6"
		>
			<li
				v-for="(recipe, index) in recipes"
				:key="recipe.id"
				class="col-span-12 sm:col-span-6 lg:col-span-4"
			>
				<RecipeCard
					:recipe="recipe"
					:index="index"
				/>
			</li>
		</ul>
	</section>
</template>

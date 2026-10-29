<script setup lang="ts">
import type { RecipeSummary } from '@features/recipes/recipes.types'

import { ArrowRightIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'

import RecipeCard from '@features/recipes/components/RecipeCard.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { searchRecipes } from '@features/recipes/recipes.api'
import { EMPTY_FILTERS } from '@features/recipes/recipes.constants'

// The newest approved recipes. The list is sorted newest first in the backend.
const COUNT = 3

const recipes = ref<RecipeSummary[]>([])
const loading = ref<boolean>(true)
const failed = ref<boolean>(false)

onMounted(async () => {
	try {
		recipes.value = (await searchRecipes('all', EMPTY_FILTERS, 1)).recipes.slice(0, COUNT)
	} catch {
		failed.value = true
	} finally {
		loading.value = false
	}
})
</script>

<template>
	<section
		class="flex flex-col gap-6"
		aria-labelledby="landing-recipes-title"
	>
		<div class="flex flex-wrap items-end justify-between gap-4">
			<div class="flex flex-col gap-2 max-w-2xl">
				<h2 id="landing-recipes-title">Frisch aus der Community</h2>

				<p class="text-lg text-ink-soft">
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
				class="col-span-12 rounded-lg bg-surface overflow-hidden sm:col-span-6 lg:col-span-4"
			>
				<span class="block aspect-4/3 bg-surface-muted animate-pulse" />

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

		<p
			v-else-if="failed"
			class="notice notice--info"
		>
			Die Rezepte konnten gerade nicht geladen werden. In der Rezeptübersicht findest du alle.
		</p>

		<p
			v-else
			class="notice notice--info"
		>
			Noch sind keine Rezepte freigegeben. Leg mit einem Konto das erste an!
		</p>
	</section>
</template>

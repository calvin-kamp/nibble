<script setup lang="ts">
import type { RecipeSummary } from '@features/recipes/recipes.types'
import type { FoodEntry, NutritionGoals, WeightEntry } from '@features/tracking/tracking.types'

import { computed, ref, watch } from 'vue'

import RecipeCard from '@features/recipes/components/RecipeCard.vue'
import TodayCard from '@features/tracking/components/TodayCard.vue'
import WeightCard from '@features/tracking/components/WeightCard.vue'
import { BaseButton } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'

import { useAuthStore } from '@features/auth/auth.store'
import { searchRecipes } from '@features/recipes/recipes.api'
import { EMPTY_FILTERS } from '@features/recipes/recipes.constants'
import { fetchDay, fetchWeightEntries } from '@features/tracking/tracking.api'
import { toIsoDate } from '@shared/utils/date'

const auth = useAuthStore()

const foodEntries = ref<FoodEntry[]>([])
const goals = ref<NutritionGoals | null>(null)
const weightEntries = ref<WeightEntry[]>([])
const trackingLoaded = ref<boolean>(false)

// Today and the weight trend, refreshed after every new entry
watch(
	[() => auth.hasDataConsent, useTrackingChanges()],
	async ([consent]) => {
		if (!consent) return

		try {
			const [today, weights] = await Promise.all([
				fetchDay(toIsoDate()),
				fetchWeightEntries(),
			])

			foodEntries.value = today.entries
			goals.value = today.goals
			weightEntries.value = weights
		} catch {
			// The cards then stay empty, but logging still works
		} finally {
			trackingLoaded.value = true
		}
	},
	{ immediate: true },
)

// The first page of saved recipes
const savedRecipes = ref<RecipeSummary[]>([])

watch(
	() => auth.isLoggedIn,
	async (loggedIn) => {
		if (!loggedIn) return

		try {
			savedRecipes.value = (await searchRecipes('saved', EMPTY_FILTERS, 1)).recipes
		} catch {
			savedRecipes.value = []
		}
	},
	{ immediate: true },
)

const greeting = computed<string>(() => {
	const hour = new Date().getHours()
	const time = hour < 11 ? 'Guten Morgen' : hour < 18 ? 'Hallo' : 'Guten Abend'

	return auth.user?.username ? `${time}, ${auth.user.username}` : time
})
</script>

<template>
	<main class="content-wrapper flex flex-col gap-6 pt-6 pb-10">
		<h1>{{ greeting }}</h1>

		<template v-if="auth.hasDataConsent">
			<template v-if="trackingLoaded">
				<TodayCard
					:food-entries="foodEntries"
					:weight-entries="weightEntries"
					:goals="goals"
				/>

				<WeightCard :entries="weightEntries" />
			</template>
		</template>

		<!-- Without consent there are no entries, so instead of empty cards this explains why -->
		<section
			v-else
			class="flex flex-col items-center gap-5 px-6 py-10 border-2 border-dashed border-line rounded-lg text-center"
			aria-labelledby="tracking-off-title"
		>
			<div class="flex flex-col items-center gap-3">
				<h2
					id="tracking-off-title"
					class="text-2xl"
				>
					Tracking ist ausgeschaltet
				</h2>

				<p class="max-w-2xl text-ink-soft text-balance">
					Ohne deine Einwilligung speichern wir kein Gewicht, keine Mahlzeiten und keinen
					Tagesbedarf. Deshalb kannst du hier nichts eintragen. Rezepte und Rechner kannst
					du weiter nutzen.
				</p>
			</div>

			<BaseButton route-name="account-privacy"> In den Einstellungen einschalten </BaseButton>
		</section>

		<section
			v-if="savedRecipes.length"
			class="flex flex-col gap-4"
			aria-labelledby="saved-recipes-title"
		>
			<h2 id="saved-recipes-title">Gespeicherte Rezepte</h2>

			<ul class="grid grid-cols-12 gap-4">
				<li
					v-for="(recipe, index) in savedRecipes"
					:key="recipe.id"
					class="col-span-12 md:col-span-6 xl:col-span-4"
				>
					<RecipeCard
						:recipe="recipe"
						:index="index"
					/>
				</li>
			</ul>
		</section>
	</main>
</template>

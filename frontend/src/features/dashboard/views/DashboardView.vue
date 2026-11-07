<script setup lang="ts">
import type { RecipeSummary } from '@features/recipes/recipes.types'
import type { FoodEntry, NutritionGoals, WeightEntry } from '@features/tracking/tracking.types'

import { ShieldOffIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import RecipeCard from '@features/recipes/components/RecipeCard.vue'
import TodayCard from '@features/tracking/components/TodayCard.vue'
import WeightCard from '@features/tracking/components/WeightCard.vue'
import { BaseButton, BaseEmptyState } from '@shared/ui'

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
		} finally {
			trackingLoaded.value = true
		}
	},
	{ immediate: true },
)

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

const todayLabel = new Date().toLocaleDateString('de-DE', {
	weekday: 'long',
	day: 'numeric',
	month: 'long',
})
</script>

<template>
	<main class="page">
		<div class="page__header">
			<div class="page__intro">
				<h1 class="wrap-break-word">
					{{ greeting }}
				</h1>

				<p class="page__lead">
					{{ todayLabel }}
				</p>
			</div>
		</div>

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

		<BaseEmptyState
			v-else
			:icon="ShieldOffIcon"
			title="Tracking ist ausgeschaltet"
		>
			Ohne deine Einwilligung speichern wir kein Gewicht, keine Mahlzeiten und keinen
			Tagesbedarf. Deshalb kannst du hier nichts eintragen. Rezepte und Rechner kannst du
			weiter nutzen.

			<template #actions>
				<BaseButton route-name="account-privacy">
					In den Einstellungen einschalten
				</BaseButton>
			</template>
		</BaseEmptyState>

		<section
			v-if="savedRecipes.length"
			class="section"
			aria-labelledby="saved-recipes-title"
		>
			<h2 id="saved-recipes-title">
				Gespeicherte Rezepte
			</h2>

			<ul class="grid grid-cols-12 gap-4">
				<li
					v-for="(recipe, index) in savedRecipes"
					:key="recipe.id"
					class="col-span-12 md:col-span-6 lg:col-span-4"
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

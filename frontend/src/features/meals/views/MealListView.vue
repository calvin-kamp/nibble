<script setup lang="ts">
import type { SavedMeal } from '@features/meals/meals.types'

import { PlusIcon, UtensilsIcon } from '@lucide/vue'
import { ref, watch } from 'vue'

import MealCard from '@features/meals/components/MealCard.vue'
import { BaseButton, BaseEmptyState, BaseIcon } from '@shared/ui'

import { useTrackingChanges } from '@features/tracking/composables/tracking-changes'

import { listMeals } from '@features/meals/meals.api'

const meals = ref<SavedMeal[]>([])
const loaded = ref<boolean>(false)
const loadError = ref<boolean>(false)

watch(
	useTrackingChanges(),
	async () => {
		try {
			meals.value = await listMeals()
			loadError.value = false
		} catch {
			loadError.value = true
		} finally {
			loaded.value = true
		}
	},
	{ immediate: true },
)
</script>

<template>
	<main class="page">
		<div class="page__header">
			<div class="page__intro">
				<h1>
					Meine Mahlzeiten
				</h1>

				<p class="page__lead">
					Was du oft isst, als Mahlzeit gespeichert.

					<br />

					Ein Klick auf „Eintragen“, und sie steht im Tagebuch.
				</p>
			</div>

			<BaseButton route-name="meal-create">
				<BaseIcon :icon="PlusIcon" />

				Mahlzeit anlegen
			</BaseButton>
		</div>

		<p
			v-if="loadError"
			class="notice notice--danger"
			role="alert"
		>
			Deine Mahlzeiten konnten nicht geladen werden. Lad die Seite bitte neu.
		</p>

		<ul
			v-else-if="meals.length"
			class="grid grid-cols-12 gap-4"
			aria-label="Mahlzeiten"
		>
			<li
				v-for="meal in meals"
				:key="meal.id"
				class="col-span-12 sm:col-span-6 xl:col-span-4"
			>
				<MealCard :meal="meal" />
			</li>
		</ul>

		<BaseEmptyState
			v-else-if="loaded"
			:icon="UtensilsIcon"
			title="Noch keine Mahlzeiten"
		>
			Leg zum Beispiel dein übliches Frühstück an.

			<br />

			Danach trägst du es mit einem Klick ein, statt jedes Lebensmittel einzeln zu suchen.

			<template #actions>
				<BaseButton route-name="meal-create">
					<BaseIcon :icon="PlusIcon" />

					Mahlzeit anlegen
				</BaseButton>
			</template>
		</BaseEmptyState>
	</main>
</template>

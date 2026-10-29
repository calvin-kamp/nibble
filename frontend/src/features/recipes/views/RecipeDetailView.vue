<script setup lang="ts">
import type { Recipe, RecipeFact } from '@features/recipes/recipes.types'

import { BookmarkCheckIcon, BookmarkIcon, PencilIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import RecipeIngredients from '@features/recipes/components/RecipeIngredients.vue'
import RecipeMedia from '@features/recipes/components/RecipeMedia.vue'
import RecipeNotFound from '@features/recipes/components/RecipeNotFound.vue'
import NutritionCard from '@features/tracking/components/NutritionCard.vue'
import { BaseBreadcrumb, BaseButton, BaseIcon } from '@shared/ui'

import { useCanonicalRecipeRoute } from '@features/recipes/composables/canonical-recipe-route'
import { useRecipeListLocation } from '@features/recipes/composables/recipe-filters'
import { usePageTitle } from '@shared/composables/page-title'
import { useToast } from '@shared/composables/toast'

import { useAuthStore } from '@features/auth/auth.store'
import { fetchRecipe, setRecipeSaved } from '@features/recipes/recipes.api'
import { recipeFacts, recipeParams } from '@features/recipes/recipes.utils'

interface Props {
	id: string
}

const props = defineProps<Props>()

const auth = useAuthStore()
const toast = useToast()

// undefined: still loading, null: does not exist or is not visible
const recipe = ref<Recipe | null | undefined>(undefined)

usePageTitle(() => recipe.value?.title)

watch(
	() => props.id,
	async (id) => {
		recipe.value = undefined

		try {
			recipe.value = await fetchRecipe(id)
		} catch {
			recipe.value = null
		}
	},
	{ immediate: true },
)

useCanonicalRecipeRoute(recipe)

const listLocation = useRecipeListLocation()

const facts = computed<RecipeFact[]>(() => (recipe.value ? recipeFacts(recipe.value) : []))

const isSaved = computed<boolean>(() => recipe.value?.isSaved ?? false)

// Saving only works when signed in and only for approved recipes
const canSave = computed<boolean>(() => auth.isLoggedIn && recipe.value?.status === 'approved')

// Notice for the author while moderation has not approved it yet
const reviewNotice = computed<{ text: string; danger: boolean } | null>(() => {
	const current = recipe.value

	if (!current?.isOwn) return null

	if (current.status === 'pending') {
		return {
			text: 'Dein Rezept wird noch geprüft. Bis zur Freigabe siehst nur du es.',
			danger: false,
		}
	}

	if (current.status === 'rejected') {
		return {
			text: `Dein Rezept wurde nicht freigegeben${current.rejectionReason ? `: ${current.rejectionReason}` : '.'} Bearbeite es und reich es noch einmal ein.`,
			danger: true,
		}
	}

	const revision = current.pendingRevision

	if (revision?.status === 'pending') {
		return {
			text: 'Deine Änderungen werden geprüft. Bis dahin sehen alle die bisherige Fassung.',
			danger: false,
		}
	}

	if (revision?.status === 'rejected') {
		return {
			text: `Deine Änderungen wurden nicht freigegeben${revision.rejectionReason ? `: ${revision.rejectionReason}` : '.'}`,
			danger: true,
		}
	}

	return null
})

// The label changes; the status message tells screen readers what happened
const status = ref<string>('')
const savingState = ref<boolean>(false)

async function toggleSaved(): Promise<void> {
	if (!recipe.value) return

	const saved = !isSaved.value

	savingState.value = true

	try {
		await setRecipeSaved(recipe.value.id, saved)
		recipe.value = { ...recipe.value, isSaved: saved }
		status.value = saved ? 'Rezept gespeichert' : 'Aus gespeicherten Rezepten entfernt'
	} catch {
		toast.show('Das hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
	} finally {
		savingState.value = false
	}
}
</script>

<template>
	<main
		v-if="recipe"
		class="content-wrapper flex flex-col gap-6 pt-4 pb-10"
	>
		<div class="flex flex-col gap-4">
			<BaseBreadcrumb
				:items="[{ label: 'Rezepte', routeName: 'recipe-list', query: listLocation.query }]"
				:current="recipe.title"
			/>

			<RecipeMedia
				class="aspect-4/3 rounded-xl bg-lime md:aspect-21/9"
				:image-url="recipe.imageUrl"
			/>
		</div>

		<div class="flex flex-col gap-5">
			<!-- Buttons to the right of the title. Icon-only on phones; the text stays as the label for
           screen readers. -->
			<div class="flex items-start justify-between gap-4">
				<h1 class="min-w-0 wrap-break-word">{{ recipe.title }}</h1>

				<div class="flex shrink-0 gap-2 md:gap-3">
					<BaseButton
						v-if="recipe.isOwn"
						class="max-md:w-11 max-md:px-0"
						variant="outline"
						route-name="recipe-edit"
						:params="recipeParams(recipe)"
					>
						<BaseIcon :icon="PencilIcon" />

						<span class="max-md:sr-only">Bearbeiten</span>
					</BaseButton>

					<BaseButton
						v-if="canSave"
						class="max-md:w-11 max-md:px-0"
						:variant="isSaved ? 'selected' : 'primary'"
						:disabled="savingState"
						@click="toggleSaved"
					>
						<BaseIcon :icon="isSaved ? BookmarkCheckIcon : BookmarkIcon" />

						<span class="max-md:sr-only">{{
							isSaved ? 'Gespeichert' : 'Rezept speichern'
						}}</span>
					</BaseButton>
				</div>

				<p
					class="sr-only"
					role="status"
				>
					{{ status }}
				</p>
			</div>

			<p
				v-if="reviewNotice"
				class="notice"
				:class="reviewNotice.danger ? 'notice--danger' : 'notice--info'"
				role="status"
			>
				{{ reviewNotice.text }}
			</p>

			<p
				v-if="recipe.description"
				class="max-w-3xl text-lg text-ink-soft"
			>
				{{ recipe.description }}
			</p>

			<!-- Label above the value. Stacked on phones, all in one row from tablet up: a fixed number
           of columns would leave single details alone in the last row. -->
			<dl class="flex flex-col gap-4 py-5 border-y border-divider md:flex-row md:gap-6">
				<div
					v-for="fact in facts"
					:key="fact.label"
					class="flex flex-col gap-0.5 min-w-0 md:flex-1"
				>
					<dt class="text-sm text-muted">{{ fact.label }}</dt>

					<dd class="font-bold">{{ fact.value }}</dd>
				</div>
			</dl>
		</div>

		<NutritionCard
			title="Nährwerte pro Portion"
			:nutrition="{
				kcal: recipe.kcalPerServing,
				protein: recipe.protein,
				carbs: recipe.carbs,
				fat: recipe.fat,
			}"
		/>

		<div class="grid grid-cols-12 gap-10 xl:items-start xl:gap-6">
			<!-- Stays in place below the fixed header while scrolling through the instructions -->
			<RecipeIngredients
				class="col-span-12 xl:col-span-5 xl:sticky xl:top-[calc(var(--site-header-height)+1.5rem)]"
				:recipe="recipe"
			/>

			<section
				class="flex flex-col gap-5 col-span-12 xl:col-span-7 xl:pt-5"
				aria-labelledby="recipe-steps-title"
			>
				<h2
					id="recipe-steps-title"
					class="text-2xl"
				>
					Zubereitung
				</h2>

				<ol class="flex flex-col gap-5">
					<li
						v-for="(step, index) in recipe.steps"
						:key="index"
						class="flex items-baseline gap-4 text-base"
					>
						<!-- The list already provides the number; the visible one is only for orientation -->
						<span
							class="grid place-items-center shrink-0 size-11 rounded-full bg-lime font-display text-xl font-extrabold text-ink"
							aria-hidden="true"
						>
							{{ index + 1 }}
						</span>

						<p class="leading-relaxed">{{ step }}</p>
					</li>
				</ol>
			</section>
		</div>
	</main>

	<main
		v-else-if="recipe === null"
		class="content-wrapper"
	>
		<RecipeNotFound />
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>

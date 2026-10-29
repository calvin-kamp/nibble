<script setup lang="ts">
import type { Recipe, RecipeFormValues } from '@features/recipes/recipes.types'

import { computed, ref, watch } from 'vue'

import RecipeForm from '@features/recipes/components/RecipeForm.vue'
import RecipeNotFound from '@features/recipes/components/RecipeNotFound.vue'
import { BaseAlertDialog, BaseBreadcrumb } from '@shared/ui'

import { useCanonicalRecipeRoute } from '@features/recipes/composables/canonical-recipe-route'
import { useRecipeListLocation } from '@features/recipes/composables/recipe-filters'
import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import { fetchRecipe, updateRecipe } from '@features/recipes/recipes.api'
import { recipeParams, toFormValues } from '@features/recipes/recipes.utils'

interface Props {
	id: string
}

const props = defineProps<Props>()

const toast = useToast()
const listLocation = useRecipeListLocation()

const form = ref<InstanceType<typeof RecipeForm> | null>(null)

// Confirm on "Abbrechen" and in the breadcrumbs once something has changed
const {
	open: leaveDialogOpen,
	leave,
	confirm: confirmLeave,
	interceptLink,
} = useLeaveConfirmation(computed(() => form.value?.isDirty ?? false))

// Only own recipes can be edited. undefined: still loading, null: missing or someone else's.
const recipe = ref<Recipe | null | undefined>(undefined)

watch(
	() => props.id,
	async (id) => {
		recipe.value = undefined

		try {
			const loaded = await fetchRecipe(id)

			recipe.value = loaded.isOwn ? loaded : null
		} catch {
			recipe.value = null
		}
	},
	{ immediate: true },
)

useCanonicalRecipeRoute(recipe)

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: RecipeFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		const updated = await updateRecipe(props.id, values)

		toast.show(
			updated.status === 'approved'
				? 'Änderungen eingereicht. Nach der Prüfung sehen sie alle.'
				: 'Änderungen gespeichert. Das Rezept wird noch geprüft.',
		)
		await form.value?.finish({ name: 'recipe-detail', params: recipeParams(updated) })
	} catch {
		submitError.value =
			'Die Änderungen konnten nicht gespeichert werden. Versuch es bitte noch einmal.'
	} finally {
		submitting.value = false
	}
}
</script>

<template>
	<main
		v-if="recipe"
		class="content-wrapper pt-4 pb-10"
	>
		<!-- Form centered in the page, header and form at the same width -->
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[
					{ label: 'Rezepte', routeName: 'recipe-list', query: listLocation.query },
					{
						label: recipe.title,
						routeName: 'recipe-detail',
						params: recipeParams(recipe),
					},
				]"
				current="Bearbeiten"
				@click.capture="interceptLink"
			/>

			<h1>Rezept bearbeiten</h1>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<!-- key: switching to another recipe restarts the form -->
			<RecipeForm
				:key="recipe.id"
				ref="form"
				:initial-values="toFormValues(recipe)"
				submit-label="Änderungen speichern"
				:submitting="submitting"
				@cancel="leave({ name: 'recipe-detail', params: recipeParams(recipe) })"
				@submit="onSubmit"
			/>

			<BaseAlertDialog
				v-model:open="leaveDialogOpen"
				title="Änderungen verwerfen?"
				description="Was du eingetragen hast, ist dann weg."
				confirm-label="Verwerfen"
				cancel-label="Weiter bearbeiten"
				variant="danger"
				@confirm="confirmLeave"
			/>
		</div>
	</main>

	<main
		v-else-if="recipe === null"
		class="content-wrapper"
	>
		<RecipeNotFound
			message="Vielleicht wurde es gelöscht, oder es ist nicht deins. Bearbeiten kannst du nur eigene Rezepte."
		/>
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>

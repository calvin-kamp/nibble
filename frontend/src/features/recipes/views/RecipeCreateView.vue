<script setup lang="ts">
import type { RecipeFormValues } from '@features/recipes/recipes.types'

import { computed, ref } from 'vue'

import RecipeForm from '@features/recipes/components/RecipeForm.vue'
import { BaseAlertDialog, BaseBreadcrumb } from '@shared/ui'

import { useRecipeListLocation } from '@features/recipes/composables/recipe-filters'
import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import { createRecipe } from '@features/recipes/recipes.api'
import { recipeParams } from '@features/recipes/recipes.utils'

const toast = useToast()
const listLocation = useRecipeListLocation()

const form = ref<InstanceType<typeof RecipeForm> | null>(null)

// Confirm on "Abbrechen" and in the breadcrumbs once something has been entered
const {
	open: leaveDialogOpen,
	leave,
	confirm: confirmLeave,
	interceptLink,
} = useLeaveConfirmation(computed(() => form.value?.isDirty ?? false))

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: RecipeFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		const recipe = await createRecipe(values)

		toast.show('Rezept eingereicht. Nach der Prüfung sehen es alle.')
		await form.value?.finish({ name: 'recipe-detail', params: recipeParams(recipe) })
	} catch {
		submitError.value =
			'Das Rezept konnte nicht gespeichert werden. Versuch es bitte noch einmal.'
	} finally {
		submitting.value = false
	}
}
</script>

<template>
	<main class="content-wrapper pt-4 pb-10">
		<!-- Form centered in the page, header and form at the same width -->
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[{ label: 'Rezepte', routeName: 'recipe-list', query: listLocation.query }]"
				current="Rezept anlegen"
				@click.capture="interceptLink"
			/>

			<div class="flex flex-col gap-3">
				<h1>Rezept anlegen</h1>

				<p class="max-w-3xl text-lg text-muted">
					Teile ein Rezept, das dir schmeckt. Nach einer kurzen Prüfung ist es für alle
					sichtbar.
				</p>
			</div>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<RecipeForm
				ref="form"
				submit-label="Rezept speichern"
				:submitting="submitting"
				@cancel="leave(listLocation)"
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
</template>

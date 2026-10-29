<script setup lang="ts">
import type { MealFormValues } from '@features/meals/meals.types'

import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import MealForm from '@features/meals/components/MealForm.vue'
import { BaseAlertDialog, BaseBreadcrumb } from '@shared/ui'

import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import { createMeal } from '@features/meals/meals.api'

const router = useRouter()
const toast = useToast()

const form = ref<InstanceType<typeof MealForm> | null>(null)

// Confirm on "Abbrechen" and in the breadcrumbs once something has been entered
const {
	open: leaveDialogOpen,
	leave,
	confirm: confirmLeave,
	interceptLink,
} = useLeaveConfirmation(computed(() => form.value?.isDirty ?? false))

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: MealFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		const meal = await createMeal(values)

		toast.show('Mahlzeit gespeichert')
		await router.push({ name: 'meal-detail', params: { id: meal.id } })
	} catch {
		submitError.value =
			'Die Mahlzeit konnte nicht gespeichert werden. Versuch es bitte noch einmal.'
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
				:items="[{ label: 'Meine Mahlzeiten', routeName: 'own-meals' }]"
				current="Mahlzeit anlegen"
				@click.capture="interceptLink"
			/>

			<div class="flex flex-col gap-3">
				<h1>Mahlzeit anlegen</h1>

				<p class="max-w-3xl text-lg text-muted">
					Stell zusammen, was du oft isst. Danach trägst du alles mit einem Klick ein.
				</p>
			</div>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<MealForm
				ref="form"
				submit-label="Mahlzeit speichern"
				:submitting="submitting"
				@submit="onSubmit"
				@cancel="leave({ name: 'own-meals' })"
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

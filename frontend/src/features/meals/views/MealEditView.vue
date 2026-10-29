<script setup lang="ts">
import type { MealFormValues, SavedMeal } from '@features/meals/meals.types'

import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import MealForm from '@features/meals/components/MealForm.vue'
import MealNotFound from '@features/meals/components/MealNotFound.vue'
import { BaseAlertDialog, BaseBreadcrumb } from '@shared/ui'

import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import { fetchMeal, updateMeal } from '@features/meals/meals.api'
import { toFormValues } from '@features/meals/meals.utils'

interface Props {
	id: string
}

const props = defineProps<Props>()

const router = useRouter()
const toast = useToast()

// undefined: still loading, null: does not exist
const meal = ref<SavedMeal | null | undefined>(undefined)

watch(
	() => props.id,
	async (id) => {
		meal.value = undefined

		try {
			meal.value = await fetchMeal(id)
		} catch {
			meal.value = null
		}
	},
	{ immediate: true },
)

const form = ref<InstanceType<typeof MealForm> | null>(null)

// Confirm on "Abbrechen" and in the breadcrumbs once something has changed
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
		await updateMeal(props.id, values)

		toast.show('Änderungen gespeichert')
		await router.push({ name: 'meal-detail', params: { id: props.id } })
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
		v-if="meal"
		class="content-wrapper pt-4 pb-10"
	>
		<!-- Form centered in the page, header and form at the same width -->
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[
					{ label: 'Meine Mahlzeiten', routeName: 'own-meals' },
					{ label: meal.name, routeName: 'meal-detail', params: { id: meal.id } },
				]"
				current="Bearbeiten"
				@click.capture="interceptLink"
			/>

			<h1>Mahlzeit bearbeiten</h1>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<!-- key: switching to another meal restarts the form -->
			<MealForm
				:key="meal.id"
				ref="form"
				:initial-values="toFormValues(meal)"
				submit-label="Änderungen speichern"
				:submitting="submitting"
				@submit="onSubmit"
				@cancel="leave({ name: 'meal-detail', params: { id: meal.id } })"
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
		v-else-if="meal === null"
		class="content-wrapper"
	>
		<MealNotFound />
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>

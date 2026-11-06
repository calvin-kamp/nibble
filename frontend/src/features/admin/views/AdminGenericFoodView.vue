<script setup lang="ts">
import type { FoodFormValues } from '@features/admin/admin.types'

import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import FoodProductForm from '@features/admin/components/FoodProductForm.vue'
import { BaseAlertDialog, BaseBreadcrumb } from '@shared/ui'

import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import { addGenericFood, FOOD_FIELD_NAMES } from '@features/admin/admin.api'
import { ApiError } from '@shared/api/client'

const router = useRouter()
const toast = useToast()

const form = ref<InstanceType<typeof FoodProductForm> | null>(null)

const {
	open: leaveDialogOpen,
	leave,
	confirm: confirmLeave,
	interceptLink,
} = useLeaveConfirmation(computed(() => form.value?.isDirty ?? false))

const LIST = { name: 'admin-foods' }

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: FoodFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		await addGenericFood(values)
		toast.show(`${values.name} angelegt`)
		await router.push(LIST)
	} catch (error) {
		if (error instanceof ApiError && error.status === 400) {
			for (const [field, messages] of Object.entries(error.fieldErrors)) {
				const name = FOOD_FIELD_NAMES[field]

				if (name && messages[0]) form.value?.setFieldError(name, messages[0])
			}
		}

		submitError.value =
			error instanceof ApiError && error.status !== 400
				? error.message
				: 'Das Lebensmittel konnte nicht gespeichert werden. Prüf die markierten Felder.'
	} finally {
		submitting.value = false
	}
}
</script>

<template>
	<main class="page">
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[{ label: 'Lebensmittel', routeName: 'admin-foods' }]"
				current="Ohne Barcode"
				@click.capture="interceptLink"
			/>

			<div class="flex flex-col gap-3">
				<h1>
					Lebensmittel ohne Barcode
				</h1>

				<p class="page__lead">
					Für lose Ware wie Obst, Gemüse oder Eier vom Markt. Es steht nur in nibble und
					in der Suche ganz oben. Nimm die Werte für den essbaren Teil.
				</p>
			</div>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<FoodProductForm
				ref="form"
				mode="generic"
				:submitting="submitting"
				@submit="onSubmit"
				@cancel="leave(LIST)"
			/>
		</div>

		<BaseAlertDialog
			v-model:open="leaveDialogOpen"
			title="Änderungen verwerfen?"
			description="Was du eingetragen hast, wird nicht gespeichert."
			confirm-label="Verwerfen"
			variant="danger"
			@confirm="confirmLeave"
		/>
	</main>
</template>

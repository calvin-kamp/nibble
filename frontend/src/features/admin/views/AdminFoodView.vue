<script setup lang="ts">
import type { FoodFormValues, MissingBarcodeDetail } from '@features/admin/admin.types'

import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import FoodProductForm from '@features/admin/components/FoodProductForm.vue'
import { BaseAlertDialog, BaseBreadcrumb, BaseButton, BaseLink } from '@shared/ui'

import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import {
	addFoodProduct,
	dismissMissingBarcode,
	FOOD_FIELD_NAMES,
	fetchMissingBarcode,
} from '@features/admin/admin.api'
import { formatTimestamp } from '@features/admin/admin.utils'
import { ApiError } from '@shared/api/client'
import { formatNumber } from '@shared/utils/number'

interface Props {
	code: string
}

const props = defineProps<Props>()

const router = useRouter()
const toast = useToast()

const missing = ref<MissingBarcodeDetail | null | undefined>(undefined)

watch(
	() => props.code,
	async (code) => {
		missing.value = undefined

		try {
			missing.value = await fetchMissingBarcode(code)
		} catch {
			missing.value = null
		}
	},
	{ immediate: true },
)

const form = ref<InstanceType<typeof FoodProductForm> | null>(null)

const {
	open: leaveDialogOpen,
	leave,
	confirm: confirmLeave,
	interceptLink,
} = useLeaveConfirmation(computed(() => form.value?.isDirty ?? false))

const LIST = { name: 'admin-foods' }

const intro = computed<string>(() => {
	if (!missing.value) return ''

	const { lookups, lastSearchedAt } = missing.value
	const times = lookups === 1 ? 'einmal' : `${formatNumber(lookups)}-mal`

	return `${times} gesucht, zuletzt am ${formatTimestamp(lastSearchedAt)}.`
})

const offUrl = computed<string>(() => `https://world.openfoodfacts.org/product/${props.code}`)

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: FoodFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		const { offSynced } = await addFoodProduct(props.code, values)

		toast.show(
			offSynced
				? `${values.name} gespeichert und an Open Food Facts gesendet`
				: `${values.name} gespeichert, nur in nibble (kein Open-Food-Facts-Konto eingerichtet)`,
		)
		await router.push(LIST)
	} catch (error) {
		if (error instanceof ApiError && error.code === 'product_exists') {
			toast.show(`Zum Barcode ${props.code} gibt es inzwischen ein Lebensmittel.`, 'info')
			await router.push(LIST)

			return
		}

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

const dismissOpen = ref<boolean>(false)

async function confirmDismiss(): Promise<void> {
	try {
		await dismissMissingBarcode(props.code)
		toast.show(`Barcode ${props.code} verworfen`, 'info')
		await router.push(LIST)
	} catch {
		toast.show('Der Barcode konnte nicht verworfen werden. Versuch es bitte noch einmal.', 'danger')
	}
}
</script>

<template>
	<main
		v-if="missing"
		class="page"
	>
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[{ label: 'Lebensmittel', routeName: 'admin-foods' }]"
				:current="props.code"
				@click.capture="interceptLink"
			/>

			<div class="flex flex-col gap-3">
				<h1>
					Lebensmittel anlegen
				</h1>

				<p class="page__lead">
					Barcode <span class="font-semibold tabular-nums">
						{{ props.code }}
					</span>,

					{{ intro }}
				</p>

				<BaseLink
					class="self-start"
					:href="offUrl"
				>
					Bei Open Food Facts ansehen
				</BaseLink>
			</div>

			<p
				v-if="missing.offProduct"
				class="notice notice--info"
			>
				Open Food Facts kennt das Produkt schon, nur unvollständig. Was dort steht, ist
				eingetragen. Prüf es mit der Packung und ergänz den Rest.
			</p>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<FoodProductForm
				ref="form"
				:initial-values="missing.offProduct ?? undefined"
				:submitting="submitting"
				@submit="onSubmit"
				@cancel="leave(LIST)"
				@dismiss="dismissOpen = true"
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

		<BaseAlertDialog
			v-model:open="dismissOpen"
			title="Barcode verwerfen?"
			:description="`${props.code} verschwindet aus der Liste. Sucht ihn jemand wieder, taucht er erneut auf.`"
			confirm-label="Verwerfen"
			variant="danger"
			@confirm="confirmDismiss"
		/>
	</main>

	<main
		v-else-if="missing === null"
		class="page"
	>
		<h1>
			Barcode nicht gefunden
		</h1>

		<p class="text-lg text-muted-foreground">
			Vielleicht hat ihn schon jemand eingetragen oder verworfen.
		</p>

		<BaseButton
			class="self-start"
			route-name="admin-foods"
		>
			Zu den Lebensmitteln
		</BaseButton>
	</main>

	<main
		v-else
		class="content-wrapper"
		aria-busy="true"
	/>
</template>

<script setup lang="ts">
import type { FoodFormValues, ModerationFood } from '@features/admin/admin.types'

import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import FoodProductForm from '@features/admin/components/FoodProductForm.vue'
import { BaseAlertDialog, BaseBreadcrumb, BaseButton, BaseCard, BaseLink } from '@shared/ui'

import { useLeaveConfirmation } from '@shared/composables/leave-confirmation'
import { useToast } from '@shared/composables/toast'

import {
	correctFood,
	dismissFoodReports,
	FOOD_FIELD_NAMES,
	fetchModerationFood,
} from '@features/admin/admin.api'
import { FOOD_REPORT_REASON_LABELS } from '@features/admin/admin.constants'
import { formatTimestamp } from '@features/admin/admin.utils'
import { ApiError } from '@shared/api/client'

interface Props {
	code: string
}

const props = defineProps<Props>()

const router = useRouter()
const toast = useToast()

const food = ref<ModerationFood | null | undefined>(undefined)

watch(
	() => props.code,
	async (code) => {
		food.value = undefined

		try {
			food.value = await fetchModerationFood(code)
		} catch {
			food.value = null
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

const LIST = { name: 'admin-foods', query: { liste: 'gemeldet' } }

const offUrl = computed<string>(() => `https://world.openfoodfacts.org/product/${props.code}`)

const submitting = ref<boolean>(false)
const submitError = ref<string | null>(null)

async function onSubmit(values: FoodFormValues): Promise<void> {
	submitting.value = true
	submitError.value = null

	try {
		const { offSynced } = await correctFood(props.code, values)

		toast.show(
			offSynced || food.value?.generic
				? `${values.name} korrigiert`
				: `${values.name} korrigiert, nur in nibble (kein Open-Food-Facts-Konto eingerichtet)`,
		)
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
				: 'Die Korrektur konnte nicht gespeichert werden. Prüf die markierten Felder.'
	} finally {
		submitting.value = false
	}
}

const dismissOpen = ref<boolean>(false)

async function confirmDismiss(): Promise<void> {
	try {
		await dismissFoodReports(props.code)
		toast.show('Meldungen verworfen', 'info')
		await router.push(LIST)
	} catch {
		toast.show('Die Meldungen konnten nicht verworfen werden. Versuch es bitte noch einmal.', 'danger')
	}
}
</script>

<template>
	<main
		v-if="food"
		class="page"
	>
		<div class="content-column content-column--form gap-6">
			<BaseBreadcrumb
				:items="[{ label: 'Lebensmittel', routeName: 'admin-foods' }]"
				:current="food.values.name"
				@click.capture="interceptLink"
			/>

			<div class="flex flex-col gap-3">
				<h1>
					Lebensmittel korrigieren
				</h1>

				<p class="page__lead">
					<template v-if="food.generic">
						Lebensmittel ohne Barcode, es steht nur in nibble.
					</template>

					<template v-else>
						Barcode <span class="font-semibold tabular-nums">
							{{ props.code }}
						</span>.
						Prüf die Werte mit der Packung. Werte und Mengen gehen auch an Open Food
						Facts, der Name bleibt in nibble.
					</template>
				</p>

				<BaseLink
					v-if="!food.generic"
					class="self-start"
					:href="offUrl"
				>
					Bei Open Food Facts ansehen
				</BaseLink>
			</div>

			<BaseCard
				v-if="food.reports.length"
				as="section"
				aria-labelledby="food-reports-title"
			>
				<div class="flex flex-col gap-4">
					<h2
						id="food-reports-title"
						class="text-xl"
					>
						{{ food.reports.length === 1 ? 'Meldung' : `${food.reports.length} Meldungen` }}
					</h2>

					<ul class="data-list">
						<li
							v-for="report in food.reports"
							:key="report.id"
							class="data-list__row"
						>
							<span class="data-list__label">
								<span class="font-semibold text-foreground">
									{{ FOOD_REPORT_REASON_LABELS[report.reason] }}
								</span>

								<span
									v-if="report.comment"
									class="text-foreground wrap-break-word"
								>
									„{{ report.comment }}“
								</span>

								<time
									class="data-list__meta"
									:datetime="report.createdAt"
								>
									{{ formatTimestamp(report.createdAt) }}
								</time>
							</span>
						</li>
					</ul>
				</div>
			</BaseCard>

			<p
				v-if="submitError"
				class="notice notice--danger"
				role="alert"
			>
				{{ submitError }}
			</p>

			<FoodProductForm
				ref="form"
				:mode="food.generic ? 'generic' : 'correct'"
				:initial-values="food.values"
				:submitting="submitting"
				@submit="onSubmit"
				@cancel="leave(LIST)"
			>
				<template
					v-if="food.reports.length"
					#actions
				>
					<BaseButton
						variant="ghost"
						class="sm:ml-auto"
						@click="dismissOpen = true"
					>
						Stimmt alles, Meldungen verwerfen
					</BaseButton>
				</template>
			</FoodProductForm>
		</div>

		<BaseAlertDialog
			v-model:open="leaveDialogOpen"
			title="Änderungen verwerfen?"
			description="Was du geändert hast, wird nicht gespeichert."
			confirm-label="Verwerfen"
			variant="danger"
			@confirm="confirmLeave"
		/>

		<BaseAlertDialog
			v-model:open="dismissOpen"
			title="Meldungen verwerfen?"
			description="Das Lebensmittel bleibt, wie es ist, und verschwindet aus der Liste."
			confirm-label="Verwerfen"
			@confirm="confirmDismiss"
		/>
	</main>

	<main
		v-else-if="food === null"
		class="page"
	>
		<h1>
			Lebensmittel nicht gefunden
		</h1>

		<p class="text-lg text-muted-foreground">
			Vielleicht hat es der letzte Import entfernt.
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

<script setup lang="ts">
import type { FoodProduct, FoodReportReason } from '@features/tracking/tracking.types'
import type { SelectOption } from '@shared/ui/types'

import { FlagIcon } from '@lucide/vue'
import { useId } from 'reka-ui'
import { nextTick, ref, watch } from 'vue'

import { BaseButton, BaseIcon, BaseSelect } from '@shared/ui'

import { reportFood } from '@features/tracking/tracking.api'
import { FOOD_REPORT_REASON_LABELS } from '@features/tracking/tracking.constants'

// Sits inside the entry form, so no form of its own and no vee-validate fields: they would
// register with the entry form and block it.

interface Props {
	product: FoodProduct
}

const props = defineProps<Props>()

const MAX_COMMENT_LENGTH = 500

const REASON_OPTIONS: SelectOption[] = (
	Object.entries(FOOD_REPORT_REASON_LABELS) as [FoodReportReason, string][]
).map(([value, label]) => ({ value, label }))

const ids = {
	panel: useId(undefined, 'food-report'),
	reason: useId(undefined, 'food-report-reason'),
	comment: useId(undefined, 'food-report-comment'),
	error: useId(undefined, 'food-report-error'),
}

const open = ref<boolean>(false)
const sent = ref<boolean>(false)
const sending = ref<boolean>(false)
const error = ref<string | null>(null)
const reason = ref<string | undefined>(undefined)
const comment = ref<string>('')

const panel = ref<HTMLElement | null>(null)

// Another product, another report
watch(
	() => props.product.code,
	() => {
		open.value = false
		sent.value = false
		reset()
	},
)

function reset(): void {
	reason.value = undefined
	comment.value = ''
	error.value = null
}

async function show(): Promise<void> {
	open.value = true
	await nextTick()
	panel.value?.querySelector<HTMLElement>('button')?.focus()
}

const root = ref<HTMLElement | null>(null)

async function close(): Promise<void> {
	open.value = false
	reset()
	await nextTick()
	root.value?.querySelector<HTMLElement>('[data-report-toggle]')?.focus()
}

async function send(): Promise<void> {
	if (!reason.value) {
		error.value = 'Wähl aus, was nicht stimmt.'

		return
	}

	sending.value = true
	error.value = null

	try {
		await reportFood(props.product.code, reason.value as FoodReportReason, comment.value)
		open.value = false
		sent.value = true
		reset()
	} catch {
		error.value = 'Die Meldung konnte nicht gesendet werden. Versuch es bitte noch einmal.'
	} finally {
		sending.value = false
	}
}
</script>

<template>
	<div
		ref="root"
		class="flex flex-col gap-3"
	>
		<p
			v-if="sent"
			class="text-md text-muted-foreground"
			role="status"
		>
			Danke! Wir prüfen es und korrigieren das Lebensmittel.
		</p>

		<BaseButton
			v-else-if="!open"
			data-report-toggle
			class="self-center"
			variant="ghost"
			size="sm"
			:aria-controls="ids.panel"
			aria-expanded="false"
			@click="show"
		>
			<BaseIcon
				:icon="FlagIcon"
				:size="16"
			/>

			Stimmt etwas nicht? Melden
		</BaseButton>

		<div
			v-else
			:id="ids.panel"
			ref="panel"
			class="flex flex-col gap-4 p-4 rounded-md bg-muted"
			role="group"
			aria-label="Fehler bei diesem Lebensmittel melden"
		>
			<p class="text-md">
				Was stimmt bei <strong>
					{{ props.product.name }}
				</strong> nicht? Wir prüfen es mit
				der Packung. Wer gemeldet hat, speichern wir nicht.
			</p>

			<div class="field">
				<label
					:for="ids.reason"
					class="field__label"
				>
					Was ist falsch?
				</label>

				<BaseSelect
					:id="ids.reason"
					v-model="reason"
					:options="REASON_OPTIONS"
					placeholder="Bitte auswählen"
					:aria-invalid="error && !reason ? 'true' : undefined"
					:aria-describedby="error ? ids.error : undefined"
				/>
			</div>

			<div class="field">
				<label
					:for="ids.comment"
					class="field__label"
				>
					Was steht auf der Packung? (optional)
				</label>

				<textarea
					:id="ids.comment"
					v-model="comment"
					class="field__input field__input--textarea"
					rows="2"
					:maxlength="MAX_COMMENT_LENGTH"
					placeholder="z. B. „Ist ein Getränk, 64 kcal pro 100 ml“"
				/>
			</div>

			<p
				v-if="error"
				:id="ids.error"
				class="field__error"
				role="alert"
			>
				{{ error }}
			</p>

			<div class="flex flex-col gap-2">
				<BaseButton
					class="w-full"
					:disabled="sending"
					@click="send"
				>
					Meldung senden
				</BaseButton>

				<BaseButton
					class="w-full"
					variant="ghost"
					@click="close"
				>
					Abbrechen
				</BaseButton>
			</div>
		</div>
	</div>
</template>

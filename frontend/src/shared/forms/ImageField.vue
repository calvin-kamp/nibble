<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { ImageIcon, TrashIcon, UploadIcon } from '@lucide/vue'
import { useField } from 'vee-validate'
import { computed, onBeforeUnmount, ref, toRef, watch } from 'vue'

import FormField from './FormField.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

// Form value: a newly chosen file (File), the URL of an already
// saved image (string), or null.
type ImageValue = File | string | null

interface Props extends BaseFieldProps<ImageValue | undefined> {
	accept?: string
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	accept: 'image/jpeg, image/png, image/webp',
})

const ids = useFieldIds(() => props.hint)

// Validates immediately on selection
const { value, errorMessage } = useField<ImageValue | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)

const input = ref<HTMLInputElement | null>(null)
const objectUrl = ref<string | null>(null)

// A temporary URL is created for a chosen file and released again
watch(
	value,
	(image) => {
		if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
		objectUrl.value = image instanceof File ? URL.createObjectURL(image) : null
	},
	{ immediate: true },
)

onBeforeUnmount(() => {
	if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
})

const previewUrl = computed<string | null>(() =>
	typeof value.value === 'string' && value.value ? value.value : objectUrl.value,
)

function onChange(event: Event): void {
	value.value = (event.target as HTMLInputElement).files?.[0] ?? null
}

// After removing, the button disappears and focus returns to the file input
function remove(): void {
	value.value = null

	if (input.value) {
		input.value.value = ''
		input.value.focus()
	}
}
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
		:class="{ 'image-field--invalid': errorMessage }"
	>
		<div class="image-field__media">
			<img
				v-if="previewUrl"
				:src="previewUrl"
				alt="Vorschau des ausgewählten Fotos"
				class="image-field__preview"
			/>

			<!-- Empty area; clicking it opens the file picker. For screen readers the file input below is
           enough, so the area is hidden from them. -->
			<label
				v-else
				:for="ids.id"
				class="image-field__empty"
				aria-hidden="true"
			>
				<BaseIcon
					:icon="ImageIcon"
					:size="32"
				/>

				<span class="font-semibold text-ink">Noch kein Foto</span>

				<span class="text-sm">Tippen oder klicken, um eins auszuwählen</span>
			</label>
		</div>

		<div class="image-field__actions">
			<!-- The real file input is invisible; the button next to it is a second label for it. Its text
           thus becomes part of the field's name, for voice control too. -->
			<input
				:id="ids.id"
				ref="input"
				type="file"
				class="image-field__input"
				:name="props.name"
				:accept="props.accept"
				:disabled="props.disabled"
				:aria-invalid="!!errorMessage || undefined"
				:aria-describedby="ids.describedBy(errorMessage)"
				@change="onChange"
			/>

			<label
				:for="ids.id"
				class="button button--outline image-field__trigger"
			>
				<BaseIcon :icon="UploadIcon" />
				{{ previewUrl ? 'Foto ersetzen' : 'Foto auswählen' }}
			</label>

			<BaseButton
				v-if="previewUrl"
				variant="ghost"
				:disabled="props.disabled"
				@click="remove"
			>
				<BaseIcon :icon="TrashIcon" />
				Foto entfernen
			</BaseButton>
		</div>
	</FormField>
</template>

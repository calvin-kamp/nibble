<script setup lang="ts">
import type { BaseFieldProps } from './types'
import type { HTMLAttributes } from 'vue'

import { useField } from 'vee-validate'
import { toRef, watch } from 'vue'

import FormField from './FormField.vue'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string> {
	type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
	placeholder?: string
	autocomplete?: string
	inputmode?: HTMLAttributes['inputmode']
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	type: 'text',
	placeholder: undefined,
	autocomplete: undefined,
	inputmode: undefined,
})

const ids = useFieldIds(() => props.hint)

// Validates on blur, and on every keystroke once there is an error
const { value, errorMessage, handleBlur, validate } = useField<string>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), validateOnValueUpdate: false, syncVModel: false },
)

watch(value, () => {
	if (errorMessage.value) validate()
})
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<input
			:id="ids.id"
			v-model="value"
			class="field__input"
			:type="props.type"
			:name="props.name"
			:placeholder="props.placeholder"
			:autocomplete="props.autocomplete"
			:inputmode="props.inputmode"
			:disabled="props.disabled"
			:aria-invalid="!!errorMessage || undefined"
			:aria-describedby="ids.describedBy(errorMessage)"
			@blur="handleBlur($event, true)"
		/>
	</FormField>
</template>

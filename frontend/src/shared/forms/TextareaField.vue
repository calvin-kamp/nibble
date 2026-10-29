<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { useField } from 'vee-validate'
import { toRef, watch } from 'vue'

import FormField from './FormField.vue'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string> {
	placeholder?: string
	rows?: number
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	placeholder: undefined,
	rows: 4,
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
		<textarea
			:id="ids.id"
			v-model="value"
			class="field__input field__input--textarea"
			:name="props.name"
			:rows="props.rows"
			:placeholder="props.placeholder"
			:disabled="props.disabled"
			:aria-invalid="!!errorMessage || undefined"
			:aria-describedby="ids.describedBy(errorMessage)"
			@blur="handleBlur($event, true)"
		/>
	</FormField>
</template>

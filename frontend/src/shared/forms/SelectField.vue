<script setup lang="ts">
import type { BaseFieldProps, FieldOption, FieldOptionGroup } from './types'

import { useField } from 'vee-validate'
import { toRef } from 'vue'

import FormField from './FormField.vue'
import { BaseSelect } from '@shared/ui'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string | undefined> {
	/** Options without groups */
	options?: FieldOption[]
	/** Options with group headings, instead of options */
	groups?: FieldOptionGroup[]
	placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	options: () => [],
	groups: () => [],
	placeholder: 'Bitte auswählen',
})

const ids = useFieldIds(() => props.hint)

// Validates immediately on selection
const { value, errorMessage, handleBlur } = useField<string | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)

function onOpenChange(open: boolean): void {
	if (!open) handleBlur()
}
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<BaseSelect
			:id="ids.id"
			v-model="value"
			:options="props.options"
			:groups="props.groups"
			:placeholder="props.placeholder"
			:disabled="props.disabled"
			:aria-invalid="!!errorMessage || undefined"
			:aria-describedby="ids.describedBy(errorMessage)"
			@update:open="onOpenChange"
		/>
	</FormField>
</template>

<script setup lang="ts">
import type { FieldIds } from './field-ids'

import { Label } from 'reka-ui'

// Frame for fields with the label above the input. Checkbox and radio have their own
// markup because label and control are arranged differently there.
interface Props {
	ids: FieldIds
	label: string
	hint?: string
	error?: string
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	error: undefined,
})
</script>

<template>
	<div
		class="field"
		:class="{ 'field--invalid': props.error }"
	>
		<Label
			:id="props.ids.labelId"
			:for="props.ids.id"
			class="field__label"
		>
			{{ props.label }}
		</Label>

		<p
			v-if="props.hint"
			:id="props.ids.hintId"
			class="field__hint"
		>
			{{ props.hint }}
		</p>

		<slot />

		<p
			v-if="props.error"
			:id="props.ids.errorId"
			class="field__error"
		>
			{{ props.error }}
		</p>
	</div>
</template>

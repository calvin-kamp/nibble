<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { EyeIcon, EyeOffIcon } from '@lucide/vue'
import { useField } from 'vee-validate'
import { ref, toRef, watch } from 'vue'

import FormField from './FormField.vue'
import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string> {
	autocomplete?: 'current-password' | 'new-password'
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	autocomplete: 'current-password',
})

const ids = useFieldIds(() => props.hint)

const { value, errorMessage, handleBlur, validate } = useField<string>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), validateOnValueUpdate: false, syncVModel: false },
)

watch(value, () => {
	if (errorMessage.value) validate()
})

const visible = ref<boolean>(false)
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<div class="password-field">
			<input
				:id="ids.id"
				v-model="value"
				class="field__input password-field__input"
				:type="visible ? 'text' : 'password'"
				:name="props.name"
				:autocomplete="props.autocomplete"
				autocapitalize="none"
				spellcheck="false"
				:disabled="props.disabled"
				:aria-invalid="!!errorMessage || undefined"
				:aria-describedby="ids.describedBy(errorMessage)"
				@blur="handleBlur($event, true)"
			/>

			<button
				type="button"
				class="password-field__toggle"
				aria-label="Passwort anzeigen"
				:aria-pressed="visible"
				:aria-controls="ids.id"
				:disabled="props.disabled"
				@click="visible = !visible"
			>
				<BaseIcon :icon="visible ? EyeOffIcon : EyeIcon" />
			</button>
		</div>
	</FormField>
</template>

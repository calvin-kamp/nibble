<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { EyeIcon, EyeOffIcon } from '@lucide/vue'
import { useField } from 'vee-validate'
import { ref, toRef, watch } from 'vue'

import FormField from './FormField.vue'
import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string> {
	/** current-password for signing in, new-password for registering */
	autocomplete?: 'current-password' | 'new-password'
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	autocomplete: 'current-password',
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

const visible = ref<boolean>(false)
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<!-- Own element so the button can sit inside the field -->
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

			<!-- Constant label with aria-pressed, so screen readers say "on" or "off" -->
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

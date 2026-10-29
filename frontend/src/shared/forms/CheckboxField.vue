<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { CheckIcon } from '@lucide/vue'
import { CheckboxIndicator, CheckboxRoot, Label } from 'reka-ui'
import { useField } from 'vee-validate'
import { toRef } from 'vue'

import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

type Props = BaseFieldProps<boolean | undefined>

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
})

const ids = useFieldIds(() => props.hint)

// Validates immediately on click
const { value, errorMessage, handleBlur } = useField<boolean | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)
</script>

<template>
	<div
		class="checkbox-field"
		:class="{ 'checkbox-field--invalid': errorMessage }"
	>
		<!-- The label wraps the checkbox, so the text is clickable too.
         The slot replaces the text, e.g. for a link in the consent. -->
		<Label
			class="checkbox-field__label"
			:for="ids.id"
		>
			<CheckboxRoot
				:id="ids.id"
				v-model="value"
				class="checkbox-field__box"
				:disabled="props.disabled"
				:aria-invalid="!!errorMessage || undefined"
				:aria-describedby="ids.describedBy(errorMessage)"
				@blur="handleBlur()"
			>
				<CheckboxIndicator>
					<BaseIcon
						:icon="CheckIcon"
						:size="16"
					/>
				</CheckboxIndicator>
			</CheckboxRoot>

			<slot>{{ props.label }}</slot>
		</Label>

		<p
			v-if="props.hint"
			:id="ids.hintId"
			class="checkbox-field__hint"
		>
			{{ props.hint }}
		</p>

		<p
			v-if="errorMessage"
			:id="ids.errorId"
			class="checkbox-field__error"
		>
			{{ errorMessage }}
		</p>
	</div>
</template>

<script setup lang="ts">
import type { BaseFieldProps, FieldOption } from './types'
import type { AcceptableValue } from 'reka-ui'

import { CheckIcon } from '@lucide/vue'
import { CheckboxGroupRoot, CheckboxIndicator, CheckboxRoot, Label } from 'reka-ui'
import { useField } from 'vee-validate'
import { computed, toRef } from 'vue'

import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

// Multiple choice as checkboxes, e.g. for recipe properties. The value is an array.
interface Props extends BaseFieldProps<string[] | undefined> {
	options: FieldOption[]
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
})

const ids = useFieldIds(() => props.hint)

// Validates immediately on selection
const { value, errorMessage } = useField<string[] | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)

// reka-ui always expects an array, but the form value may still be missing
const selected = computed<AcceptableValue[]>({
	get: () => value.value ?? [],
	set: (values) => {
		value.value = values as string[]
	},
})
</script>

<template>
	<fieldset
		class="checkbox-group"
		:class="{ 'checkbox-group--invalid': errorMessage }"
	>
		<legend class="checkbox-group__legend">{{ props.label }}</legend>

		<p
			v-if="props.hint"
			:id="ids.hintId"
			class="checkbox-group__hint"
		>
			{{ props.hint }}
		</p>

		<!-- rovingFocus off: every checkbox is reachable with Tab as usual -->
		<CheckboxGroupRoot
			v-model="selected"
			class="checkbox-group__options"
			:roving-focus="false"
			:disabled="props.disabled"
		>
			<Label
				v-for="(option, index) in props.options"
				:key="option.value"
				class="checkbox-group__option"
				:for="`${ids.id}-${index}`"
			>
				<!-- Same box as in CheckboxField -->
				<CheckboxRoot
					:id="`${ids.id}-${index}`"
					class="checkbox-field__box"
					:value="option.value"
					:disabled="option.disabled"
					:aria-invalid="!!errorMessage || undefined"
					:aria-describedby="ids.describedBy(errorMessage)"
				>
					<CheckboxIndicator>
						<BaseIcon
							:icon="CheckIcon"
							:size="16"
						/>
					</CheckboxIndicator>
				</CheckboxRoot>

				{{ option.label }}
			</Label>
		</CheckboxGroupRoot>

		<p
			v-if="errorMessage"
			:id="ids.errorId"
			class="checkbox-group__error"
		>
			{{ errorMessage }}
		</p>
	</fieldset>
</template>

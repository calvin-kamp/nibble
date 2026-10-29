<script setup lang="ts">
import type { BaseFieldProps, FieldOption } from './types'

import { Label, RadioGroupIndicator, RadioGroupItem, RadioGroupRoot } from 'reka-ui'
import { useField } from 'vee-validate'
import { toRef } from 'vue'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<string | undefined> {
	options: FieldOption[]
	orientation?: 'vertical' | 'horizontal'
	/** Legend for screen readers only, when a heading already asks the question */
	labelHidden?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	orientation: 'vertical',
	labelHidden: false,
})

const ids = useFieldIds(() => props.hint)

// Validates immediately on selection
const { value, errorMessage } = useField<string | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)
</script>

<template>
	<!-- fieldset and legend group the options under one shared question -->
	<fieldset
		class="radio-field"
		:class="{ 'radio-field--invalid': errorMessage }"
	>
		<legend
			class="radio-field__legend"
			:class="{ 'sr-only': props.labelHidden }"
		>
			{{ props.label }}
		</legend>

		<p
			v-if="props.hint"
			:id="ids.hintId"
			class="radio-field__hint"
		>
			{{ props.hint }}
		</p>

		<RadioGroupRoot
			v-model="value"
			class="radio-field__options"
			:orientation="props.orientation"
			:disabled="props.disabled"
			:aria-invalid="!!errorMessage || undefined"
			:aria-describedby="ids.describedBy(errorMessage)"
		>
			<!-- The label wraps the radio button, so the text is clickable too -->
			<Label
				v-for="(option, index) in props.options"
				:key="option.value"
				class="radio-field__option"
				:for="`${ids.id}-${index}`"
			>
				<RadioGroupItem
					:id="`${ids.id}-${index}`"
					class="radio-field__radio"
					:value="option.value"
					:disabled="option.disabled"
				>
					<RadioGroupIndicator class="radio-field__indicator" />
				</RadioGroupItem>

				<span class="radio-field__text">
					{{ option.label }}
					<span
						v-if="option.description"
						class="radio-field__description"
					>
						{{ option.description }}
					</span>
				</span>
			</Label>
		</RadioGroupRoot>

		<p
			v-if="errorMessage"
			:id="ids.errorId"
			class="radio-field__error"
		>
			{{ errorMessage }}
		</p>
	</fieldset>
</template>

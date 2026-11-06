<script setup lang="ts">
import type { BaseFieldProps } from './types'

import { MinusIcon, PlusIcon } from '@lucide/vue'
import {
	NumberFieldDecrement,
	NumberFieldIncrement,
	NumberFieldInput,
	NumberFieldRoot,
} from 'reka-ui'
import { useField } from 'vee-validate'
import { computed, toRef } from 'vue'

import FormField from './FormField.vue'
import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

interface Props extends BaseFieldProps<number | undefined> {
	unit?: string
	/**
	 * Limits that reka-ui silently clamps the value to. For plausibility checks, prefer the schema,
	 * which produces an error message instead of a changed value.
	 */
	min?: number
	max?: number
	step?: number
	stepper?: boolean
	incrementLabel?: string
	decrementLabel?: string
	formatOptions?: Intl.NumberFormatOptions
	/** Label of the Enter key on phone keyboards, e.g. "next" or "done" */
	enterKeyHint?: 'enter' | 'done' | 'go' | 'next' | 'previous' | 'search' | 'send'
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	unit: undefined,
	min: undefined,
	max: undefined,
	step: 1,
	stepper: false,
	incrementLabel: 'Mehr',
	decrementLabel: 'Weniger',
	formatOptions: () => ({ maximumFractionDigits: 1 }),
	enterKeyHint: undefined,
})

const ids = useFieldIds(() => props.hint)
const unitId = `${ids.id}-unit`

const { value, errorMessage, handleBlur } = useField<number | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)

// reka-ui returns null for an empty field; the form then holds undefined
const numberValue = computed<number | undefined>({
	get: () => value.value,
	set: (number) => {
		value.value = number ?? undefined
	},
})

const describedBy = computed<string | undefined>(() => {
	const describedByIds = [props.unit ? unitId : null, ids.describedBy(errorMessage.value)]

	return describedByIds.filter(Boolean).join(' ') || undefined
})
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<NumberFieldRoot
			v-model="numberValue"
			class="number-field"
			:class="{ 'number-field--stepper': props.stepper }"
			:style="
				props.unit ? { '--number-field-unit-length': `${props.unit.length}ch` } : undefined
			"
			locale="de-DE"
			:min="props.min"
			:max="props.max"
			:step="props.step"
			:step-snapping="false"
			:format-options="props.formatOptions"
			:disabled="props.disabled"
		>
			<NumberFieldDecrement
				v-if="props.stepper"
				class="number-field__button"
				:aria-label="props.decrementLabel"
			>
				<BaseIcon
					:icon="MinusIcon"
					:size="18"
				/>
			</NumberFieldDecrement>

			<NumberFieldInput
				:id="ids.id"
				class="field__input number-field__input"
				:name="props.name"
				:aria-invalid="!!errorMessage || undefined"
				:aria-describedby="describedBy"
				:enterkeyhint="props.enterKeyHint"
				@blur="handleBlur($event, true)"
			/>

			<span
				v-if="props.unit"
				:id="unitId"
				class="number-field__unit"
			>
				{{ props.unit }}
			</span>

			<NumberFieldIncrement
				v-if="props.stepper"
				class="number-field__button"
				:aria-label="props.incrementLabel"
			>
				<BaseIcon
					:icon="PlusIcon"
					:size="18"
				/>
			</NumberFieldIncrement>
		</NumberFieldRoot>
	</FormField>
</template>

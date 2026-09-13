<script setup lang="ts">
import { Field as VeeField } from 'vee-validate'
import { computed, useId, useSlots } from 'vue'
import { Field, FieldDescription, FieldError, FieldLabel } from '../ui/field'
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from '../ui/number-field'

interface Props {
  fieldName: string
  label: string
  srOnlyLabel?: boolean
  description?: string
  srOnlyDescription?: boolean
  unit?: string
  min?: number
  max?: number
  step?: number
  fractionDigits?: number
  variant?: 'plain' | 'stepper'
  required?: boolean
  disabled?: boolean
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  srOnlyLabel: false,
  description: undefined,
  srOnlyDescription: false,
  unit: undefined,
  min: 0,
  max: undefined,
  step: undefined,
  placeholder: undefined,
  fractionDigits: 0,
  variant: 'plain',
  required: false,
  disabled: false,
})

const slots = useSlots()

const fieldId: string = useId()
const descriptionId: string = `${fieldId}-description`
const unitId: string = `${fieldId}-unit`
const errorId: string = `${fieldId}-error`

const isStepper = computed<boolean>(() => props.variant === 'stepper')

const hasDescription = computed<boolean>(() => Boolean(props.description || slots.description))

const formatOptions = computed<Intl.NumberFormatOptions>(() => ({
  minimumFractionDigits: 0,
  maximumFractionDigits: props.fractionDigits,
}))

function describedBy(invalid: boolean): string | undefined {
  const ids: string[] = []

  if (hasDescription.value) ids.push(descriptionId)
  if (props.unit) ids.push(unitId)
  if (invalid) ids.push(errorId)

  return ids.join(' ') || undefined
}

function toModelValue(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function toFieldValue(next: number | null | undefined): number | undefined {
  return next === null || next === undefined || Number.isNaN(next) ? undefined : next
}
</script>

<template>
  <VeeField
    v-slot="{ value, errors, handleChange, handleBlur }"
    :name="props.fieldName"
  >
    <Field :data-invalid="errors.length > 0">
      <FieldLabel
        :for="fieldId"
        :required-mark="props.required"
        :class="{ 'sr-only': props.srOnlyLabel }"
      >
        {{ props.label }}
      </FieldLabel>

      <FieldDescription
        v-if="hasDescription"
        :id="descriptionId"
        :class="{ 'sr-only': props.srOnlyDescription }"
      >
        <slot name="description">
          {{ props.description }}
        </slot>
      </FieldDescription>

      <NumberField
        :model-value="toModelValue(value)"
        :min="props.min"
        :max="props.max"
        :step="props.step"
        :step-snapping="false"
        :disabled="props.disabled"
        :format-options="formatOptions"
        locale="de-DE"
        @update:model-value="(next) => handleChange(toFieldValue(next), true)"
      >
        <NumberFieldContent>
          <NumberFieldDecrement
            v-if="isStepper"
            :label="`${props.label} verringern`"
          />

          <NumberFieldInput
            :id="fieldId"
            :placeholder="props.placeholder"
            :aria-required="props.required"
            :aria-invalid="errors.length > 0"
            :aria-describedby="describedBy(errors.length > 0)"
            :class="{ 'text-center': isStepper }"
            @blur="(event: FocusEvent) => handleBlur(event, true)"
          />

          <span
            v-if="props.unit"
            :id="unitId"
            class="text-muted-foreground shrink-0 pr-1.5 text-sm select-none"
          >
            {{ props.unit }}
          </span>

          <NumberFieldIncrement
            v-if="isStepper"
            :label="`${props.label} erhöhen`"
          />
        </NumberFieldContent>
      </NumberField>

      <FieldError
        v-if="errors.length > 0"
        :id="errorId"
        :errors="errors"
      />
    </Field>
  </VeeField>
</template>

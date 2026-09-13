<script setup lang="ts">
import { Field as VeeField } from 'vee-validate'
import { computed, useId, useSlots } from 'vue'
import { Field, FieldContent, FieldDescription, FieldError, FieldLabel } from '../ui/field'
import { Checkbox } from '../ui/checkbox'

interface Props {
  fieldName: string
  label: string
  description?: string
  srOnlyDescription?: boolean
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  description: undefined,
  srOnlyDescription: false,
  required: false,
  disabled: false,
})

const slots = useSlots()

const fieldId: string = useId()
const descriptionId: string = `${fieldId}-description`
const errorId: string = `${fieldId}-error`

const hasDescription = computed<boolean>(() => Boolean(props.description || slots.description))

function toModelValue(value: unknown): boolean {
  return value === true
}

function describedBy(invalid: boolean): string | undefined {
  const ids: string[] = []

  if (hasDescription.value) ids.push(descriptionId)
  if (invalid) ids.push(errorId)

  return ids.join(' ') || undefined
}
</script>

<template>
  <VeeField
    v-slot="{ value, errors, handleChange }"
    :name="props.fieldName"
  >
    <Field
      orientation="horizontal"
      :data-invalid="errors.length > 0"
    >
      <Checkbox
        :id="fieldId"
        :model-value="toModelValue(value)"
        :disabled="props.disabled"
        :aria-required="props.required"
        :aria-invalid="errors.length > 0"
        :aria-describedby="describedBy(errors.length > 0)"
        @update:model-value="(next) => handleChange(next, true)"
      />

      <FieldContent>
        <FieldLabel
          :for="fieldId"
          :required-mark="props.required"
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

        <FieldError
          v-if="errors.length > 0"
          :id="errorId"
          :errors="errors"
        />
      </FieldContent>
    </Field>
  </VeeField>
</template>

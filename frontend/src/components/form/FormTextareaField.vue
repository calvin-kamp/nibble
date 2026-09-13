<script setup lang="ts">
import { Field as VeeField } from 'vee-validate'
import { computed, useId, useSlots } from 'vue'
import { Field, FieldDescription, FieldError, FieldLabel } from '../ui/field'
import { Textarea } from '../ui/textarea'

interface Props {
  fieldName: string
  label: string
  placeholder: string
  rows?: number
  srOnlyLabel?: boolean
  description?: string
  srOnlyDescription?: boolean
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  rows: undefined,
  srOnlyLabel: false,
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

function describedBy(invalid: boolean): string | undefined {
  const ids: string[] = []

  if (hasDescription.value) ids.push(descriptionId)
  if (invalid) ids.push(errorId)

  return ids.join(' ') || undefined
}
</script>

<template>
  <VeeField
    v-slot="{ componentField, errors }"
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

      <Textarea
        v-bind="componentField"
        :id="fieldId"
        :rows="props.rows"
        :placeholder="props.placeholder"
        :disabled="props.disabled"
        :aria-required="props.required"
        :aria-invalid="errors.length > 0"
        :aria-describedby="describedBy(errors.length > 0)"
      />

      <FieldError
        v-if="errors.length > 0"
        :id="errorId"
        :errors="errors"
      />
    </Field>
  </VeeField>
</template>

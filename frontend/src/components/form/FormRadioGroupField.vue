<script setup lang="ts">
import { Field as VeeField } from 'vee-validate'
import { computed, useId, useSlots } from 'vue'
import { FieldDescription, FieldError, FieldLegend, FieldSet } from '../ui/field'
import { ChoiceButton, ChoiceGroup, ChoiceTile } from './choice-group'
import type { Option } from '@/types/form.types'

interface Props {
  fieldName: string
  label: string
  options: Option[]
  variant?: 'button' | 'tile'
  description?: string
  srOnlyDescription?: boolean
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'button',
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
    <FieldSet :data-invalid="errors.length > 0">
      <FieldLegend>
        {{ props.label }}
      </FieldLegend>

      <FieldDescription
        v-if="hasDescription"
        :id="descriptionId"
        :class="{ 'sr-only': props.srOnlyDescription }"
      >
        <slot name="description">
          {{ props.description }}
        </slot>
      </FieldDescription>

      <ChoiceGroup
        v-bind="componentField"
        :layout="props.variant === 'tile' ? 'responsive' : 'row'"
        :disabled="props.disabled"
        :aria-label="props.label"
        :aria-required="props.required"
        :aria-invalid="errors.length > 0"
        :aria-describedby="describedBy(errors.length > 0)"
      >
        <template v-if="props.variant === 'tile'">
          <ChoiceTile
            v-for="option in props.options"
            :key="option.value"
            :value="option.value"
            :label="option.label"
            :description="option.description"
            :disabled="props.disabled || option.disabled"
          />
        </template>

        <template v-else>
          <ChoiceButton
            v-for="option in props.options"
            :key="option.value"
            :value="option.value"
            :disabled="props.disabled || option.disabled"
          >
            {{ option.label }}
          </ChoiceButton>
        </template>
      </ChoiceGroup>

      <FieldError
        v-if="errors.length > 0"
        :id="errorId"
        :errors="errors"
      />
    </FieldSet>
  </VeeField>
</template>

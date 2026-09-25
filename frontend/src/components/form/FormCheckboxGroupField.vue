<script setup lang="ts">
import type { CheckboxOption, FormFieldProps } from '@interfaces/form.types'

import { CheckboxGroup, CheckboxGroupItem } from './controls'
import { FormFieldset } from '.'

interface Props extends FormFieldProps {
  options: CheckboxOption[]
}

defineOptions({ inheritAttrs: false })

const props = defineProps<Props>()
</script>

<template>
  <FormFieldset
    :field-name="props.fieldName"
    :label="props.label"
    :required="props.required"
    :description="props.description"
  >
    <template #control="{ id, labelledBy, componentField, invalid, describedBy }">
      <CheckboxGroup
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :required="props.required"
        :aria-labelledby="labelledBy"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      >
        <CheckboxGroupItem
          v-for="option in props.options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </CheckboxGroupItem>
      </CheckboxGroup>
    </template>
  </FormFieldset>
</template>

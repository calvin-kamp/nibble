<script setup lang="ts">
import type { FormFieldProps, SelectEntry } from './form.types'

import FormField from './FormField.vue'
import { SelectControl } from './controls'

interface Props extends FormFieldProps {
  options: SelectEntry[]
}

defineOptions({ inheritAttrs: false })

const props = defineProps<Props>()
</script>

<template>
  <FormField
    :field-name="props.fieldName"
    :label="props.label"
    :required="props.required"
    :description="props.description"
  >
    <template #control="{ id, componentField, invalid, describedBy }">
      <SelectControl
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :options="props.options"
        :required="props.required"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      />
    </template>
  </FormField>
</template>

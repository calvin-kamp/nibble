<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import FormField from './FormField.vue'
import { TextareaControl } from './controls'

defineOptions({ inheritAttrs: false })

const props = defineProps<FormFieldProps>()
</script>

<template>
  <FormField v-bind="props">
    <template #control="{ id, componentField, invalid, describedBy }">
      <TextareaControl
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :required="props.required"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      />
    </template>
  </FormField>
</template>

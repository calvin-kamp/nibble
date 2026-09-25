<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import { useValidateField } from 'vee-validate'
import { nextTick, toRef } from 'vue'
import FormField from './FormField.vue'
import { ImageControl } from './controls'

defineOptions({ inheritAttrs: false })

const props = defineProps<FormFieldProps>()

const validateField = useValidateField(toRef(props, 'fieldName'))

/** A wrong file is reported right away instead of on submit */
async function validateAfterChange(): Promise<void> {
  await nextTick()
  await validateField()
}
</script>

<template>
  <FormField v-bind="props">
    <template #control="{ id, componentField, invalid, describedBy }">
      <ImageControl
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
        @update:model-value="validateAfterChange"
      />
    </template>
  </FormField>
</template>

<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import FormField from './FormField.vue'
import { NumberInputControl } from './controls'

defineOptions({ inheritAttrs: false })

const props = defineProps<FormFieldProps>()
</script>

<template>
  <FormField v-bind="props">
    <template
      v-if="$slots.description"
      #description
    >
      <slot name="description" />
    </template>

    <template #control="{ id, componentField, invalid, describedBy }">
      <NumberInputControl
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :required="props.required"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      >
        <template
          v-if="$slots.leading"
          #leading
        >
          <slot name="leading" />
        </template>

        <template
          v-if="$slots.trailing"
          #trailing
        >
          <slot name="trailing" />
        </template>
      </NumberInputControl>
    </template>
  </FormField>
</template>

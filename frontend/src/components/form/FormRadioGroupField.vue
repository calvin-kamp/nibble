<script setup lang="ts">
import type { RadioItemVariants } from './controls'
import type { FormFieldProps, RadioOption } from './form.types'

import FormFieldSet from './FormFieldSet.vue'
import { RadioGroup, RadioGroupItem } from './controls'

interface Props extends FormFieldProps {
  options: RadioOption[]
  variant?: RadioItemVariants['variant']
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
  variant: 'card',
})
</script>

<template>
  <FormFieldSet
    :field-name="props.fieldName"
    :label="props.label"
    :required="props.required"
    :description="props.description"
  >
    <template #control="{ id, labelledBy, componentField, invalid, describedBy }">
      <RadioGroup
        v-bind="{ ...$attrs, ...componentField }"
        :id="id"
        :required="props.required"
        :aria-labelledby="labelledBy"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedBy"
      >
        <RadioGroupItem
          v-for="option in props.options"
          :key="option.value"
          :value="option.value"
          :variant="props.variant"
          :disabled="option.disabled"
        >
          <template #title>{{ option.label }}</template>

          <template v-if="props.variant === 'card' && option.description">
            {{ option.description }}
          </template>
        </RadioGroupItem>
      </RadioGroup>
    </template>
  </FormFieldSet>
</template>

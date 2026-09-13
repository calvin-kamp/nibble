<script setup lang="ts">
import { computed, useId, useSlots } from 'vue'
import { FieldDescription, FieldLegend, FieldSet } from '../ui/field'

interface Props {
  label: string
  srOnlyLabel?: boolean
  labelVariant?: 'legend' | 'label'
  description?: string
  srOnlyDescription?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  srOnlyLabel: false,
  labelVariant: 'legend',
  description: undefined,
  srOnlyDescription: false,
})

const slots = useSlots()

const fieldId: string = useId()
const descriptionId: string = `${fieldId}-description`

const hasDescription = computed<boolean>(() => Boolean(props.description || slots.description))

const describedBy = computed<string | undefined>(() =>
  hasDescription.value ? descriptionId : undefined,
)
</script>

<template>
  <FieldSet :aria-describedby="describedBy">
    <FieldLegend
      :variant="props.labelVariant"
      :class="{ 'sr-only': props.srOnlyLabel }"
    >
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

    <slot />
  </FieldSet>
</template>

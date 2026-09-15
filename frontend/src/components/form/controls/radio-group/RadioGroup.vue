<script setup lang="ts">
import type { RadioGroupRootProps } from 'reka-ui'

import { RadioGroupRoot } from 'reka-ui'

interface Props {
  columns?: 1 | 2 | 3
}

const props = withDefaults(defineProps<Props>(), {
  columns: 1,
})

const modelValue = defineModel<RadioGroupRootProps['modelValue']>()
</script>

<template>
  <RadioGroupRoot
    v-model="modelValue"
    :class="[
      'group grid grid-cols-1 gap-x-4 gap-y-3',
      props.columns === 2 && 'md:grid-cols-2',
      props.columns === 3 && 'md:grid-cols-3',
    ]"
  >
    <slot />
  </RadioGroupRoot>
</template>

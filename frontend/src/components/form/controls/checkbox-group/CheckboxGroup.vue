<script setup lang="ts">
import type { CheckboxGroupRootProps } from 'reka-ui'

import { CheckboxGroupRoot } from 'reka-ui'

const modelValue = defineModel<CheckboxGroupRootProps['modelValue']>()
</script>

<template>
  <CheckboxGroupRoot
    v-model="modelValue"
    :roving-focus="false"
    class="group flex flex-wrap gap-2"
  >
    <slot />
  </CheckboxGroupRoot>
</template>

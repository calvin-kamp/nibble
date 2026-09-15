<script setup lang="ts">
import type { RadioItemVariants } from '.'

import { RadioGroupItem } from 'reka-ui'
import { radioItemVariants } from '.'

interface Props {
  variant?: RadioItemVariants['variant']
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'card',
})
</script>

<template>
  <RadioGroupItem :class="radioItemVariants({ variant: props.variant })">
    <span class="font-medium">
      <slot name="title" />
    </span>

    <span
      v-if="$slots.default"
      class="text-muted-foreground text-sm text-center"
    >
      <slot />
    </span>
  </RadioGroupItem>
</template>

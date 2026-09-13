<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import {
  focusRingWithin,
  invalidRingWithin,
  transitionInteractive,
} from '@/lib/interactive-styles'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="number-field-content"
    :class="cn(
      focusRingWithin,
      invalidRingWithin,
      transitionInteractive,
      'bg-input/30 border-input flex h-11 w-full items-center gap-1 rounded-lg border px-1.5',
      'group-data-disabled/number-field:cursor-not-allowed group-data-disabled/number-field:opacity-50',
      props.class,
    )"
  >
    <slot />
  </div>
</template>

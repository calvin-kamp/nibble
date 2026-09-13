<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { MinusIcon } from '@lucide/vue'
import { NumberFieldDecrement } from 'reka-ui'
import { cn } from '@/lib/utils'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { focusRingOffset, transitionInteractive } from '@/lib/interactive-styles'

const props = withDefaults(defineProps<{
  class?: HTMLAttributes['class']
  label?: string
}>(), {
  label: 'Wert verringern',
})
</script>

<template>
  <NumberFieldDecrement
    data-slot="number-field-decrement"
    :aria-label="props.label"
    :class="cn(
      focusRingOffset,
      transitionInteractive,
      'text-muted-foreground relative flex size-8 shrink-0 items-center justify-center rounded-lg border border-transparent',
      'hover:bg-accent hover:text-accent-foreground',
      'after:absolute after:-inset-1.5',
      'data-disabled:pointer-events-none data-disabled:opacity-50 disabled:pointer-events-none disabled:opacity-50',
      props.class,
    )"
  >
    <slot>
      <LucideIcon
        :icon="MinusIcon"
      />
    </slot>
  </NumberFieldDecrement>
</template>

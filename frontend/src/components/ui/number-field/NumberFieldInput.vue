<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { NumberFieldInput } from 'reka-ui'
import { cn } from '@/lib/utils'
import { focusRingReset, transitionInteractive } from '@/lib/interactive-styles'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <NumberFieldInput
    data-slot="number-field-input"
    :class="cn(
      focusRingReset,
      transitionInteractive,
      'h-full w-full min-w-0 bg-transparent px-1.5 text-base tabular-nums outline-hidden',
      'placeholder:text-muted-foreground',
      'disabled:cursor-not-allowed',
      props.class,
    )"
  />
</template>

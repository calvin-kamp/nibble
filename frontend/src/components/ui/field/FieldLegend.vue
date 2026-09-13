<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  class?: HTMLAttributes['class']
  variant?: 'legend' | 'label'
}>(), {
  variant: 'legend',
})
</script>

<template>
  <legend
    data-slot="field-legend"
    :data-variant="variant"
    :class="cn(
      'mb-3 leading-snug',
      'data-[variant=legend]:text-lg data-[variant=legend]:font-semibold data-[variant=legend]:tracking-tight',
      'data-[variant=label]:text-base data-[variant=label]:font-medium',
      props.class,
    )"
  >
    <slot />
  </legend>
</template>

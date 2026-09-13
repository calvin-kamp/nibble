<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { Textarea } from '@/components/ui/textarea'
import { focusRingReset } from '@/lib/interactive-styles'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <Textarea
    data-slot="input-group-control"
    :class="cn(
      focusRingReset,
      'flex-1 resize-none rounded-none border-0 bg-transparent py-2 dark:bg-transparent',
      props.class,
    )"
  />
</template>

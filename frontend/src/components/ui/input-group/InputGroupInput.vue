<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { focusRingReset } from '@/lib/interactive-styles'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <Input
    data-slot="input-group-control"
    :class="cn(
      focusRingReset,
      'flex-1 rounded-none border-0 bg-transparent dark:bg-transparent [&::-webkit-search-cancel-button]:hidden',
      props.class,
    )"
  />
</template>

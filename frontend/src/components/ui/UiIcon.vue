<script lang="ts" setup>
import type { LucideIcon } from '@lucide/vue'
import type { HTMLAttributes } from 'vue'

import { mergeClasses } from '@lib/merge-classes'

interface Props {
  icon: LucideIcon
  size?: number
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  size: 16,
  class: undefined,
})
</script>

<template>
  <component
    :is="props.icon"
    :size="props.size"
    :class="mergeClasses('shrink-0', props.class)"
    aria-hidden="true"
  />
</template>

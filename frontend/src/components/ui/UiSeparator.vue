<script setup lang="ts">
import type { SeparatorProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'

import { Separator } from 'reka-ui'
import { mergeClasses } from '@lib/merge-classes'

interface Props extends SeparatorProps {
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'div',
  asChild: false,
  orientation: 'horizontal',
  decorative: true,
  class: undefined,
})
</script>

<template>
  <Separator
    :as="props.as"
    :as-child="props.asChild"
    :orientation="props.orientation"
    :decorative="props.decorative"
    :class="
      mergeClasses(
        'bg-border shrink-0',
        props.orientation === 'vertical' ? 'w-px self-stretch' : 'h-px w-full',
        props.class,
      )
    "
  />
</template>

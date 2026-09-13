<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { Primitive, type PrimitiveProps } from 'reka-ui'
import { cn } from '@/lib/utils'
import { interactiveCardLink, transitionInteractive } from '@/lib/interactive-styles'

interface Props extends PrimitiveProps {
  class?: HTMLAttributes['class']
  size?: 'default' | 'sm'
}

const props = withDefaults(defineProps<Props>(), {
  as: 'div',
  size: 'default',
})
</script>

<template>
  <Primitive
    data-slot="card"
    :as="props.as"
    :as-child="props.asChild"
    :data-size="props.size"
    :class="cn(
      transitionInteractive,
      interactiveCardLink,
      'ring-foreground/10 bg-card text-card-foreground gap-6 overflow-hidden rounded-lg py-6 text-sm ring-1 has-[>img:first-child]:pt-0 data-[size=sm]:gap-3 data-[size=sm]:py-0 data-[size=sm]:pbe-4 *:[img:first-child]:rounded-t-xl *:[img:last-child]:rounded-b-xl group/card flex flex-col',
      props.class,
    )"
  >
    <slot />
  </Primitive>
</template>

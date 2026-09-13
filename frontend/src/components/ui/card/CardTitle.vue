<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { Primitive, type PrimitiveProps } from 'reka-ui'
import { cn } from '@/lib/utils'

interface Props extends PrimitiveProps {
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'div',
})
</script>

<template>
  <Primitive
    data-slot="card-title"
    :as="props.as"
    :as-child="props.asChild"
    :class="cn('text-base font-medium font-heading leading-snug tracking-normal text-balance', props.class)"
  >
    <slot />
  </Primitive>
</template>

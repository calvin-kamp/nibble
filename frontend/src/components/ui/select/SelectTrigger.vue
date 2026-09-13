<script setup lang="ts">
import type { SelectTriggerProps } from 'reka-ui'

import type { HTMLAttributes } from 'vue'
import { ChevronDownIcon } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import { SelectIcon, SelectTrigger, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { focusRing, invalidRing, transitionInteractive } from '@/lib/interactive-styles'

const props = withDefaults(
  defineProps<SelectTriggerProps & { class?: HTMLAttributes['class'], size?: 'sm' | 'default' }>(),
  { size: 'default' },
)

const delegatedProps = reactiveOmit(props, 'class', 'size')
const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <SelectTrigger
    data-slot="select-trigger"
    :data-size="size"
    v-bind="forwardedProps"
    :class="cn(
      focusRing,
      invalidRing,
      transitionInteractive,
      'flex h-11 w-full items-center justify-between px-3 py-2',
      'border-input bg-input/30 gap-2 rounded-lg border text-sm whitespace-nowrap',
      'data-placeholder:text-muted-foreground',
      '*:data-[slot=select-value]:flex *:data-[slot=select-value]:min-w-0 *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-2 *:data-[slot=select-value]:truncate',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'dark:hover:bg-input/50',
      '[&_svg:not([class*=size-])]:size-4 [&_svg]:pointer-events-none [&_svg]:shrink-0',
      props.class,
    )"
  >
    <slot />
    <SelectIcon :as-child="true">
      <LucideIcon
        :icon="ChevronDownIcon"
        class="text-muted-foreground pointer-events-none"
      />
    </SelectIcon>
  </SelectTrigger>
</template>

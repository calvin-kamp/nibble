<script setup lang="ts">
import type { RadioGroupItemProps } from 'reka-ui'

import type { HTMLAttributes } from 'vue'
import { CircleIcon } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import {
  RadioGroupIndicator,
  RadioGroupItem,
  useForwardProps,
} from 'reka-ui'
import { cn } from '@/lib/utils'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { focusRingOffset, invalidRing, transitionInteractive } from '@/lib/interactive-styles'

const props = defineProps<RadioGroupItemProps & { class?: HTMLAttributes['class'] }>()

const delegatedProps = reactiveOmit(props, 'class')

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <RadioGroupItem
    data-slot="radio-group-item"
    v-bind="forwardedProps"
    :class="cn(
      focusRingOffset,
      invalidRing,
      transitionInteractive,
      'group/radio-group-item peer relative flex aspect-square size-4 shrink-0 rounded-full border border-input dark:bg-input/30',
      'data-checked:border-primary data-checked:bg-primary data-checked:text-primary-foreground dark:data-checked:bg-primary aria-invalid:aria-checked:border-primary',
      'after:absolute after:-inset-3.5',
      'disabled:cursor-not-allowed disabled:opacity-50',
      props.class,
    )"
  >
    <RadioGroupIndicator
      data-slot="radio-group-indicator"
      class="flex size-4 items-center justify-center"
    >
      <slot>
        <LucideIcon
          :icon="CircleIcon"
          class="bg-primary-foreground absolute top-1/2 left-1/2 size-2 -translate-x-1/2 -translate-y-1/2 rounded-full"
        />
      </slot>
    </RadioGroupIndicator>
  </RadioGroupItem>
</template>

<script setup lang="ts">
import type { CheckboxRootEmits, CheckboxRootProps } from 'reka-ui'

import type { HTMLAttributes } from 'vue'
import { CheckIcon } from '@lucide/vue'
import { reactiveOmit } from '@vueuse/core'
import { CheckboxIndicator, CheckboxRoot, useForwardPropsEmits } from 'reka-ui'
import { cn } from '@/lib/utils'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { focusRingOffset, invalidRing, transitionInteractive } from '@/lib/interactive-styles'

const props = defineProps<CheckboxRootProps & { class?: HTMLAttributes['class'] }>()
const emits = defineEmits<CheckboxRootEmits>()

const delegatedProps = reactiveOmit(props, 'class')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <CheckboxRoot
    v-slot="slotProps"
    data-slot="checkbox"
    v-bind="forwarded"
    :class="cn(
      focusRingOffset,
      invalidRing,
      transitionInteractive,
      'relative flex shrink-0 items-center justify-center size-4 peer',
      'border-input dark:bg-input/30 border rounded-md aria-invalid:aria-checked:border-primary',
      'data-checked:bg-primary data-checked:text-primary-foreground dark:data-checked:bg-primary data-checked:border-primary',
      'after:absolute after:-inset-x-3 after:-inset-y-2',
      'group-has-disabled/field:opacity-50 disabled:cursor-not-allowed disabled:opacity-50',
      props.class)"
  >
    <CheckboxIndicator
      data-slot="checkbox-indicator"
      class="[&>svg]:size-3.5 grid place-content-center text-current transition-none"
    >
      <slot v-bind="slotProps">
        <LucideIcon :icon="CheckIcon" />
      </slot>
    </CheckboxIndicator>
  </CheckboxRoot>
</template>

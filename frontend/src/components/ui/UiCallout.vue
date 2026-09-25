<script setup lang="ts">
import type { LucideIcon } from '@lucide/vue'
import type { HTMLAttributes } from 'vue'
import type { CalloutVariants } from './variants'

import { computed } from 'vue'
import { InfoIcon, TriangleAlertIcon } from '@lucide/vue'
import { mergeClasses } from '@lib/merge-classes'
import { calloutVariants } from './variants'
import UiIcon from './UiIcon.vue'

interface Props {
  variant?: CalloutVariants['variant']
  title?: string
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  title: undefined,
  class: undefined,
})

const icon = computed<LucideIcon | undefined>(() => {
  if (props.variant === 'warning') return TriangleAlertIcon
  if (props.variant === 'info') return InfoIcon

  return undefined
})

const iconClass = computed<string>(() =>
  props.variant === 'warning' ? 'text-destructive' : 'text-primary',
)
</script>

<template>
  <div :class="mergeClasses(calloutVariants({ variant: props.variant }), props.class)">
    <span
      v-if="icon"
      class="flex h-6 items-center"
    >
      <UiIcon
        :icon="icon"
        :class="iconClass"
      />
    </span>

    <div class="flex min-w-0 flex-col gap-1">
      <p
        v-if="props.title"
        class="font-medium"
      >
        {{ props.title }}
      </p>

      <p class="max-w-prose mt-0.5 text-muted-foreground text-sm">
        <slot />
      </p>
    </div>
  </div>
</template>

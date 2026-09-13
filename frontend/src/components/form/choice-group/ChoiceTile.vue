<script setup lang="ts">
import type { RadioGroupItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { useId } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { RadioGroupItem, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'
import { focusRingOffset, transitionInteractive } from '@/lib/interactive-styles'

interface Props extends RadioGroupItemProps {
  label: string
  description?: string
  class?: HTMLAttributes['class']
}

const props = defineProps<Props>()

const tileId: string = useId()
const titleId: string = `${tileId}-title`
const descriptionId: string = `${tileId}-description`

const delegatedProps = reactiveOmit(props, 'class', 'label', 'description')

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <RadioGroupItem
    data-slot="choice-tile"
    v-bind="forwardedProps"
    :aria-labelledby="titleId"
    :aria-describedby="props.description ? descriptionId : undefined"
    :class="
      cn(
        focusRingOffset,
        transitionInteractive,
        'group/choice-tile border-border bg-input/30 flex w-full flex-col items-center gap-1 rounded-xl border p-4 select-none',
        'hover:not-data-checked:bg-input/50',
        'data-checked:border-primary data-checked:bg-primary/8 data-checked:ring-primary data-checked:ring-1 data-checked:ring-inset',
        'group-aria-invalid/choice-group:border-destructive group-aria-invalid/choice-group:ring-0',
        'disabled:pointer-events-none disabled:opacity-50',
        props.class,
      )
    "
  >
    <span
      :id="titleId"
      class="leading-snug font-medium group-data-checked/choice-tile:font-bold"
    >
      {{ props.label }}
    </span>

    <span
      v-if="props.description"
      :id="descriptionId"
      class="text-muted-foreground text-sm leading-normal font-normal"
    >
      {{ props.description }}
    </span>
  </RadioGroupItem>
</template>

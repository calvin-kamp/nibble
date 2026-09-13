<script setup lang="ts">
import type { RadioGroupItemProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { RadioGroupItem, useForwardProps } from 'reka-ui'
import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'

interface Props extends RadioGroupItemProps {
  class?: HTMLAttributes['class']
}

const props = defineProps<Props>()

const delegatedProps = reactiveOmit(props, 'class')

const forwardedProps = useForwardProps(delegatedProps)
</script>

<template>
  <RadioGroupItem
    data-slot="choice-button"
    v-bind="forwardedProps"
    :class="
      cn(
        buttonVariants({ variant: 'outline' }),
        'w-full',
        'data-checked:border-primary data-checked:bg-primary data-checked:text-primary-foreground data-checked:font-semibold',
        'data-checked:hover:bg-primary data-checked:hover:text-primary-foreground',
        'group-aria-invalid/choice-group:border-destructive',
        props.class,
      )
    "
  >
    <slot />
  </RadioGroupItem>
</template>

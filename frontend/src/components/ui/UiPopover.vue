<script setup lang="ts">
import type { LucideIcon } from '@lucide/vue'
import type { ButtonVariants } from './variants'

import { useId } from 'vue'
import { PopoverArrow, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'

import { UiButton, UiIcon } from '.'

interface Props {
  triggerLabel?: string
  triggerVariant?: ButtonVariants['variant']
  triggerIcon?: LucideIcon
  triggerSize?: ButtonVariants['size']
  triggerIconSize?: number
  srOnlyTriggerLabel?: boolean
  title: string
  description?: string
  srOnlyDescription?: boolean
  side?: 'top' | 'right' | 'bottom' | 'left'
  align?: 'start' | 'center' | 'end'
}

const props = withDefaults(defineProps<Props>(), {
  triggerLabel: undefined,
  triggerVariant: 'ghost',
  triggerIcon: undefined,
  triggerSize: 'icon',
  triggerIconSize: 24,
  description: undefined,
  srOnlyTriggerLabel: false,
  srOnlyDescription: false,
  side: 'bottom',
  align: 'center',
})

const titleId = useId()
const descriptionId = useId()
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <slot name="trigger">
        <UiButton
          :variant="props.triggerVariant"
          :size="props.triggerSize"
        >
          <UiIcon
            v-if="props.triggerIcon"
            :icon="props.triggerIcon"
            :size="props.triggerIconSize"
          />

          <span :class="{ 'sr-only': props.srOnlyTriggerLabel }">
            {{ props.triggerLabel || 'Öffnen' }}
          </span>
        </UiButton>
      </slot>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side="props.side"
        :align="props.align"
        :side-offset="4"
        :aria-labelledby="titleId"
        :aria-describedby="props.description ? descriptionId : undefined"
        class="z-50 flex w-72 max-w-(--reka-popover-content-available-width) flex-col gap-4 p-4 bg-popover rounded-lg shadow-md ring-1 ring-foreground/10 outline-hidden text-popover-foreground origin-(--reka-popover-content-transform-origin) duration-100 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
      >
        <div class="flex flex-col gap-1 pr-6">
          <p
            :id="titleId"
            class="font-heading text-base leading-none font-medium"
          >
            {{ props.title }}
          </p>

          <p
            v-if="props.description"
            :id="descriptionId"
            :class="[
              'text-sm text-muted-foreground *:[a]:underline *:[a]:underline-offset-3 *:[a]:hover:text-foreground',
              { 'sr-only': props.srOnlyDescription },
            ]"
          >
            {{ props.description }}
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <slot name="content" />
        </div>

        <PopoverArrow class="fill-popover" />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

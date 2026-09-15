<script setup lang="ts">
import type { LucideIcon } from '@lucide/vue'
import type { ButtonVariants } from './variants'

import { XIcon } from '@lucide/vue'
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from 'reka-ui'

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
})
</script>

<template>
  <DialogRoot>
    <DialogTrigger as-child>
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
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay
        class="fixed inset-0 z-50 bg-black/10 duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 supports-backdrop-filter:backdrop-blur-xs"
      />

      <DialogContent
        class="fixed top-1/2 left-1/2 z-50 grid w-full max-w-[calc(100%-2rem)] gap-4 p-4 bg-popover rounded-xl ring-1 ring-foreground/10 outline-hidden text-popover-foreground -translate-x-1/2 -translate-y-1/2 duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 md:max-w-sm"
      >
        <div class="flex flex-col gap-2 pr-10">
          <DialogTitle class="font-heading text-base leading-none font-medium">
            {{ props.title }}
          </DialogTitle>

          <DialogDescription
            v-if="props.description"
            :class="[
              'text-sm text-muted-foreground *:[a]:underline *:[a]:underline-offset-3 *:[a]:hover:text-foreground',
              { 'sr-only': props.srOnlyDescription },
            ]"
          >
            {{ props.description }}
          </DialogDescription>
        </div>

        <DialogClose as-child>
          <UiButton
            variant="ghost"
            size="icon-sm"
            class="absolute top-2 right-2"
          >
            <UiIcon :icon="XIcon" />

            <span class="sr-only">Schließen</span>
          </UiButton>
        </DialogClose>

        <div class="flex flex-col gap-2">
          <slot name="content" />
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

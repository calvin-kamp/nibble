<script setup lang="ts">
import type { ButtonVariants } from './variants'
import type { LucideIcon } from '@lucide/vue'

import { UiButton, UiIcon } from '.'

import {
  DrawerContent,
  DrawerDescription,
  DrawerHandle,
  DrawerOverlay,
  DrawerPortal,
  DrawerRoot,
  DrawerTitle,
  DrawerTrigger,
} from 'reka-ui'

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

const open = defineModel<boolean>('open')
</script>

<template>
  <DrawerRoot v-model:open="open">
    <DrawerTrigger as-child>
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
    </DrawerTrigger>

    <DrawerPortal>
      <DrawerOverlay
        class="fixed inset-0 z-50 bg-black/10 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 supports-backdrop-filter:backdrop-blur-xs"
      />

      <DrawerContent
        :class="[
          'fixed inset-x-0 bottom-0 z-50 mt-24 flex h-auto max-h-[80vh] flex-col bg-popover rounded-t-xl border-t outline-hidden text-popover-foreground',
          'will-change-transform transform-[translate3d(0,var(--drawer-swipe-movement-y,0px),0)]',
          'transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] data-swiping:duration-0 data-swiping:select-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=open]:slide-in-from-bottom data-[state=closed]:slide-out-to-bottom',
        ]"
      >
        <DrawerHandle class="mx-auto mt-4 h-1 w-25 shrink-0 bg-muted rounded-full" />

        <div class="p-6">
          <div class="mx-auto flex max-w-lg flex-col gap-0.5 pb-4">
            <DrawerTitle class="text-foreground font-heading text-base text-center font-medium">
              {{ props.title }}
            </DrawerTitle>

            <DrawerDescription
              v-if="props.description"
              :class="[
                'text-muted-foreground text-sm text-center',
                { 'sr-only': props.srOnlyDescription },
              ]"
            >
              {{ props.description }}
            </DrawerDescription>
          </div>

          <div class="mx-auto flex max-w-lg flex-col gap-2">
            <slot name="content" />
          </div>

          <div
            v-if="$slots.footer"
            class="mx-auto mt-6 flex max-w-lg flex-col gap-3 pt-4 border-border border-t md:flex-row"
          >
            <slot name="footer" />
          </div>
        </div>
      </DrawerContent>
    </DrawerPortal>
  </DrawerRoot>
</template>

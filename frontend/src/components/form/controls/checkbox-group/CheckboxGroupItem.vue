<script setup lang="ts">
import { CheckboxIndicator, CheckboxRoot } from 'reka-ui'
import { CheckIcon } from '@lucide/vue'
import { UiIcon } from '@components/ui'

interface Props {
  value: string
  disabled?: boolean
}

const props = defineProps<Props>()
</script>

<template>
  <CheckboxRoot
    :value="props.value"
    :disabled="props.disabled"
    :class="[
      'relative before:absolute before:inset-x-0 before:-inset-y-1',
      'inline-flex items-center gap-1.5 min-h-9 px-3.5 py-1',
      'border border-input rounded-full',
      'not-data-[state=checked]:hover:bg-muted',
      'data-[state=checked]:pl-2.5 data-[state=checked]:border-primary data-[state=checked]:bg-primary/10 data-[state=checked]:font-medium',
      'transition-interactive focus-visible:focus-ring',
      'group-aria-invalid:border-destructive group-aria-invalid:focus-visible:focus-ring-destructive',
      'disabled:inactive',
    ]"
  >
    <CheckboxIndicator class="flex">
      <UiIcon
        :icon="CheckIcon"
        :size="16"
        :stroke-width="2.5"
      />
    </CheckboxIndicator>

    <slot />
  </CheckboxRoot>
</template>

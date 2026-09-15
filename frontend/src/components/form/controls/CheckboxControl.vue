<script setup lang="ts">
import type { CheckboxRootProps } from 'reka-ui'

import { CheckboxIndicator, CheckboxRoot } from 'reka-ui'
import { CheckIcon, MinusIcon } from '@lucide/vue'
import { UiIcon } from '@components/ui'

const modelValue = defineModel<CheckboxRootProps['modelValue']>()
</script>

<template>
  <CheckboxRoot
    v-model="modelValue"
    :class="[
      'flex size-5 shrink-0 items-center justify-center',
      'border border-input rounded-sm',
      'data-[state=checked]:bg-primary data-[state=checked]:border-primary data-[state=checked]:text-primary-foreground',
      'data-[state=indeterminate]:bg-primary data-[state=indeterminate]:border-primary data-[state=indeterminate]:text-primary-foreground',
      'transition-interactive focus-visible:focus-ring',
      'aria-invalid:border-destructive aria-invalid:focus-visible:focus-ring-destructive',
      'disabled:inactive',
    ]"
  >
    <CheckboxIndicator>
      <UiIcon
        :icon="modelValue === 'indeterminate' ? MinusIcon : CheckIcon"
        :size="14"
        :stroke-width="3"
      />
    </CheckboxIndicator>
  </CheckboxRoot>
</template>

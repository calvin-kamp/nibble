<script setup lang="ts">
import {
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
  NumberFieldRoot,
} from 'reka-ui'
import { MinusIcon, PlusIcon } from '@lucide/vue'
import { UiButton, UiIcon } from '@components/ui'
import { computed } from 'vue'

interface Props {
  min?: number
  max?: number
  step?: number
  fractionDigits?: number
  stepper?: boolean
  disabled?: boolean
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
  min: undefined,
  max: undefined,
  step: 1,
  fractionDigits: 0,
  stepper: false,
  disabled: false,
})

const modelValue = defineModel<number>()

const formatOptions = computed<Intl.NumberFormatOptions>(() => ({
  maximumFractionDigits: props.fractionDigits,
}))
</script>

<template>
  <NumberFieldRoot
    v-model="modelValue"
    locale="de-DE"
    :min="props.min"
    :max="props.max"
    :step="props.step"
    :format-options="formatOptions"
    :disabled="props.disabled"
    :class="[
      'flex items-center gap-2 w-full min-w-0 h-11 px-4',
      'bg-input/30 border border-input rounded-md',
      'transition-interactive has-[input:focus-visible]:focus-ring',
      'has-aria-invalid:border-destructive has-aria-invalid:has-[input:focus-visible]:focus-ring-destructive',
      'has-[input:disabled]:inactive',
    ]"
  >
    <NumberFieldDecrement
      v-if="props.stepper"
      as-child
    >
      <UiButton
        variant="ghost"
        size="icon-sm"
        aria-label="Wert verringern"
      >
        <UiIcon
          :icon="MinusIcon"
          :size="18"
        />
      </UiButton>
    </NumberFieldDecrement>

    <span
      v-if="$slots.leading"
      class="text-muted-foreground"
    >
      <slot name="leading" />
    </span>

    <NumberFieldInput
      v-bind="$attrs"
      :class="[
        'min-w-0 flex-1 bg-transparent outline-hidden text-base',
        props.stepper ? 'text-center' : 'text-start',
      ]"
    />

    <span
      v-if="$slots.trailing"
      class="text-muted-foreground"
    >
      <slot name="trailing" />
    </span>

    <NumberFieldIncrement
      v-if="props.stepper"
      as-child
    >
      <UiButton
        variant="ghost"
        size="icon-sm"
        aria-label="Wert erhöhen"
      >
        <UiIcon
          :icon="PlusIcon"
          :size="18"
        />
      </UiButton>
    </NumberFieldIncrement>
  </NumberFieldRoot>
</template>

<script setup lang="ts">
import type { PrimitiveProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { ButtonVariants } from './variants'

import { computed } from 'vue'
import { Primitive } from 'reka-ui'
import { mergeClasses } from '@lib/merge-classes'
import { buttonVariants } from './variants'

interface Props extends PrimitiveProps {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
  variant: 'default',
  size: 'default',
  type: 'button',
  disabled: false,
  loading: false,
  class: undefined,
})

const isNativeButton = computed<boolean>(() => !props.asChild && props.as === 'button')
</script>

<template>
  <Primitive
    :as="props.as"
    :as-child="props.asChild"
    :type="isNativeButton ? props.type : undefined"
    :disabled="isNativeButton ? props.disabled || props.loading : undefined"
    :aria-busy="props.loading ? true : undefined"
    :class="mergeClasses(buttonVariants({ variant: props.variant, size: props.size }), props.class)"
  >
    <slot v-if="props.asChild" />

    <template v-else>
      <span :class="['contents', props.loading && 'invisible']">
        <slot />
      </span>

      <span
        v-if="props.loading"
        aria-hidden="true"
        class="absolute inset-0 m-auto size-4.5 rounded-full border-2 border-current border-t-transparent animate-spin"
      />
    </template>
  </Primitive>
</template>

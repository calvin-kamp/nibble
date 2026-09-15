<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { LinkVariant } from './variants'

import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { mergeClasses } from '@lib/merge-classes'
import { linkVariants } from './variants'

interface Props {
  href?: string
  routeName?: string
  hash?: string
  variant?: LinkVariant
  class?: HTMLAttributes['class']
  activeClass?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  href: undefined,
  routeName: undefined,
  hash: undefined,
  variant: 'inline',
  class: undefined,
  activeClass: undefined,
})

const isExternal = computed<boolean>(() => !!props.href?.startsWith('http'))

const linkClasses = computed<string>(() =>
  mergeClasses('transition-interactive focus-visible:focus-ring', linkVariants[props.variant], props.class),
)
</script>

<template>
  <RouterLink
    v-if="props.routeName"
    :to="{ name: props.routeName, hash: props.hash }"
    :class="linkClasses"
    :active-class="mergeClasses(props.activeClass)"
  >
    <slot />
  </RouterLink>

  <a
    v-else-if="props.href"
    :href="props.href"
    :target="isExternal ? '_blank' : undefined"
    :rel="isExternal ? 'noopener noreferrer' : undefined"
    :class="linkClasses"
  >
    <slot />

    <span
      v-if="isExternal"
      class="sr-only"
    >
      (öffnet in neuem Tab)
    </span>
  </a>
</template>

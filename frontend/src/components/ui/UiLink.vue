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
  newTab?: boolean
  class?: HTMLAttributes['class']
  activeClass?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
  href: undefined,
  routeName: undefined,
  hash: undefined,
  variant: 'inline',
  newTab: false,
  class: undefined,
  activeClass: undefined,
})

const isExternal = computed<boolean>(() => !!props.href?.startsWith('http'))
const opensNewTab = computed<boolean>(() => props.newTab || isExternal.value === true)

const linkClasses = computed<string>(() =>
  mergeClasses(
    'transition-interactive focus-visible:focus-ring',
    linkVariants[props.variant],
    props.class,
  ),
)
</script>

<template>
  <RouterLink
    v-if="props.routeName"
    :to="{ name: props.routeName, hash: props.hash }"
    :target="opensNewTab ? '_blank' : undefined"
    :class="linkClasses"
    :active-class="mergeClasses(props.activeClass)"
  >
    <slot />

    <span
      v-if="opensNewTab"
      class="sr-only"
    >
      (öffnet in neuem Tab)
    </span>
  </RouterLink>

  <a
    v-else-if="props.href"
    :href="props.href"
    :target="opensNewTab ? '_blank' : undefined"
    :rel="opensNewTab ? 'noopener noreferrer' : undefined"
    :class="linkClasses"
  >
    <slot />

    <span
      v-if="opensNewTab"
      class="sr-only"
    >
      (öffnet in neuem Tab)
    </span>
  </a>
</template>

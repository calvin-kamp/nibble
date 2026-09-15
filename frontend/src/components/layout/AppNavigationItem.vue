<script setup lang="ts">
import type { NavItem } from '@interfaces/navigation.types'

import { UiIcon } from '@components/ui'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

interface Props {
  navItem: NavItem
  variant?: 'default' | 'mobile'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const activeClass = computed<string>(() =>
  props.variant === 'mobile'
    ? 'text-primary font-medium before:absolute before:inset-x-2 before:-top-2 before:mx-auto before:h-0.5 before:max-w-15 before:rounded-full before:bg-primary'
    : 'text-primary font-medium after:absolute after:inset-x-3 after:-bottom-2.5 after:h-0.5 after:rounded-full after:bg-primary',
)
</script>

<template>
  <RouterLink
    :to="{ name: props.navItem.routeName }"
    :class="[
      'relative transition-interactive focus-visible:focus-ring hover:text-primary',
      {
        'flex h-16 flex-col items-center justify-center rounded-md hover:bg-primary/10 active:translate-y-0.5':
          props.variant === 'mobile',
      },
      {
        'inline-flex h-11 items-center rounded-md px-3 hover:bg-muted': props.variant === 'default',
      },
    ]"
    :active-class="activeClass"
  >
    <UiIcon
      v-if="props.variant === 'mobile' && props.navItem.icon"
      :icon="props.navItem.icon"
      :size="24"
    />

    <span class="text-sm md:text-base">
      {{ props.navItem.label }}
    </span>
  </RouterLink>
</template>

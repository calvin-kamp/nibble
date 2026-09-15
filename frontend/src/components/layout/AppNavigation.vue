<script setup lang="ts">
import type { NavItem } from '@interfaces/navigation.types'

import { navigation } from '@data/main-navigation.data'
import { AppNavigationItem, AppTrackingMenuDrawer, AppUserMenuDrawer } from '.'
import { computed } from 'vue'
import { useAuthStore } from '@stores/auth.store'

interface Props {
  variant?: 'default' | 'mobile'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const auth = useAuthStore()

const filteredNavigation = computed<NavItem[]>(() =>
  navigation.filter(
    (item) =>
      item.visibility === 'always' || item.visibility === (auth.isLoggedIn ? 'user' : 'guest'),
  ),
)

const splitIndex = computed<number>(() => Math.ceil(filteredNavigation.value.length / 2))

const leadingNavigation = computed<NavItem[]>(() =>
  filteredNavigation.value.slice(0, splitIndex.value),
)

const trailingNavigation = computed<NavItem[]>(() =>
  filteredNavigation.value.slice(splitIndex.value),
)
</script>

<template>
  <nav
    :class="{
      'bg-background fixed inset-x-0 bottom-0 z-40 border-t py-2': props.variant === 'mobile',
    }"
    aria-label="Hauptnavigation"
  >
    <ul class="flex content-wrapper md:gap-3 lg:gap-4">
      <li
        v-for="navItem of leadingNavigation"
        :key="navItem.routeName"
        class="flex-1"
      >
        <AppNavigationItem
          :nav-item="navItem"
          :variant="props.variant"
        />
      </li>

      <li
        v-if="auth.isLoggedIn && props.variant === 'mobile'"
        class="-mt-8 flex-1 text-center"
      >
        <AppTrackingMenuDrawer />
      </li>

      <li
        v-for="navItem of trailingNavigation"
        :key="navItem.routeName"
        class="flex-1"
      >
        <AppNavigationItem
          :nav-item="navItem"
          :variant="props.variant"
        />
      </li>

      <li
        v-if="props.variant === 'mobile' && auth.isLoggedIn"
        class="flex-1"
      >
        <AppUserMenuDrawer />
      </li>
    </ul>
  </nav>
</template>

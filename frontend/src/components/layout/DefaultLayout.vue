<script setup lang="ts">
import { RouterView } from 'vue-router'
import { AppFooter, AppHeader, AppNavigation } from '.'
import { useBreakpoint } from '@composables/breakpoint'

const { activeBreakpoint } = useBreakpoint()
</script>

<template>
  <AppHeader />

  <main class="content-wrapper py-6">
    <RouterView />
  </main>

  <AppFooter />

  <AppNavigation
    v-if="activeBreakpoint !== 'desktop'"
    variant="mobile"
  />
</template>

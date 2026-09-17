<script setup lang="ts">
import { RouterView } from 'vue-router'
import { AppFooter, AppHeader, AppNavigation } from '.'
import { useBreakpoint } from '@composables/breakpoint'

const { activeBreakpoint } = useBreakpoint()
</script>

<template>
  <div class="flex flex-1 flex-col pb-26 lg:pb-0">
    <AppHeader />

    <main class="flex-1 content-wrapper py-6">
      <RouterView />
    </main>

    <AppFooter />

    <AppNavigation
      v-if="activeBreakpoint !== 'desktop'"
      variant="mobile"
    />
  </div>
</template>

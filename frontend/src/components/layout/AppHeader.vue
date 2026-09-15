<script setup lang="ts">
import { useBreakpoint } from '@composables/breakpoint'
import { AppLogo, AppNavigation, AppThemeToggle, AppTrackingMenuModal, AppUserMenuPopover } from '.'
import { useAuthStore } from '@stores/auth.store'

const { activeBreakpoint } = useBreakpoint()
const auth = useAuthStore()
</script>

<template>
  <header class="py-2 border-b">
    <div class="flex gap-10 content-wrapper">
      <AppLogo />

      <div class="flex items-center justify-between w-full">
        <AppNavigation
          v-if="activeBreakpoint === 'desktop'"
          variant="default"
        />

        <div class="flex items-center gap-2 ml-auto">
          <AppTrackingMenuModal v-if="activeBreakpoint === 'desktop'" />

          <AppThemeToggle />

          <AppUserMenuPopover v-if="activeBreakpoint === 'desktop' && auth.isLoggedIn" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useColorTheme } from '@composables/color-theme'
import { UiButton, UiIcon } from './ui'
import { MoonIcon, SunIcon } from '@lucide/vue'

const { theme, changeTheme } = useColorTheme()
</script>

<template>
  <UiButton
    variant="ghost"
    size="icon"
    :aria-label="
      theme === 'dark' ? 'Zu hellem Farbschema wechseln' : 'Zu dunklem Farbschema wechseln'
    "
    @click="changeTheme()"
  >
    <UiIcon
      :icon="theme === 'dark' ? SunIcon : MoonIcon"
      :size="20"
    />
  </UiButton>
</template>

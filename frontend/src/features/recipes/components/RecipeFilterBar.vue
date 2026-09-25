<script setup lang="ts">
import { useBreakpoint } from '@composables/breakpoint'
import RecipeFilterDrawer from './RecipeFilterDrawer.vue'
import RecipeFilterPanel from './RecipeFilterPanel.vue'

const { isDesktop } = useBreakpoint()
</script>

<template>
  <RecipeFilterPanel v-if="isDesktop" />

  <RecipeFilterDrawer v-else />
</template>

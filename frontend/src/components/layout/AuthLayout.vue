<script setup lang="ts">
import { RouterView } from 'vue-router'
import { AppFooter, AppHeader } from '.'
</script>

<template>
  <AppHeader />

  <main class="content-wrapper">
    <RouterView />
  </main>

  <AppFooter />
</template>

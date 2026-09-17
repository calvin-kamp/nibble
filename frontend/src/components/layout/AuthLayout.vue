<script setup lang="ts">
import { RouterView } from 'vue-router'
import { AppFooter, AppHeader } from '.'
import BenefitPanel from '@features/auth/components/BenefitPanel.vue'
</script>

<template>
  <div class="flex flex-1 flex-col">
    <AppHeader />

    <div class="flex flex-col min-h-dvh overflow-clip">
      <div class="grid flex-1 content-center content-wrapper lg:grid-cols-2">
        <main class="lg:col-start-2 lg:row-start-1">
          <RouterView />
        </main>

        <BenefitPanel class="hidden lg:block lg:col-start-1 lg:row-start-1" />
      </div>
    </div>

    <AppFooter />
  </div>
</template>

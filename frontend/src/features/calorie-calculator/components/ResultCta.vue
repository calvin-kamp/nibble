<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { UiButton } from '@components/ui'
</script>

<template>
  <div
    class="flex flex-col gap-4 p-6 bg-primary rounded-2xl text-primary-foreground md:flex-row md:items-center md:justify-between md:p-8"
  >
    <div class="flex flex-col gap-1 md:max-w-prose">
      <h3>Behalt die Zahl im Blick</h3>

      <p class="text-sm">
        Mit einem kostenlosen Account speicherst du dein Ziel, trackst Mahlzeiten und siehst jeden
        Tag, wo du stehst.
      </p>
    </div>

    <UiButton
      as-child
      class="w-full shrink-0 bg-primary-foreground text-primary hover:bg-primary-foreground/90 focus-visible:focus-ring-primary-foreground [--ring-offset:var(--primary)] md:w-auto"
    >
      <RouterLink :to="{ name: 'auth-register' }">Kostenlos registrieren</RouterLink>
    </UiButton>
  </div>
</template>

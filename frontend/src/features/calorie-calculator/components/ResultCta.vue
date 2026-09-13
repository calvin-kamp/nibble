<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
</script>

<template>
  <div
    class="bg-primary text-primary-foreground flex flex-col gap-4 rounded-2xl p-6 md:flex-row md:items-center md:justify-between md:p-8"
  >
    <div class="flex flex-col gap-1 md:max-w-[60ch]">
      <h3 class="text-lg leading-snug">Behalt die Zahl im Blick</h3>

      <p class="text-sm">
        Mit einem kostenlosen Account speicherst du dein Ziel, trackst Mahlzeiten und siehst jeden
        Tag, wo du stehst.
      </p>
    </div>

    <Button
      :as-child="true"
      class="bg-primary-foreground text-primary hover:bg-primary-foreground/90 w-full shrink-0 md:w-auto"
    >
      <RouterLink to="/registrieren">Kostenlos registrieren</RouterLink>
    </Button>
  </div>
</template>

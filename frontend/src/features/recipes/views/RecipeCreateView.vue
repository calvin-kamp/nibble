<script setup lang="ts">
import { UiLink } from '@components/ui'
import RecipeForm from '../components/RecipeForm.vue'
</script>

<template>
  <div class="flex flex-col gap-6 w-full max-w-2xl mx-auto md:gap-8">
    <div class="flex flex-col items-start gap-2">
      <UiLink
        route-name="recipe-list"
        variant="standalone"
      >
        Zu den Rezepten
      </UiLink>

      <h1>Rezept erstellen</h1>
    </div>

    <RecipeForm />
  </div>
</template>

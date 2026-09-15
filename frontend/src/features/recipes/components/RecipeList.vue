<script setup lang="ts">
import RecipeCard from './RecipeCard.vue'
import { UiEmptyState, UiIcon } from '@components/ui'
import { SoupIcon } from '@lucide/vue'
import { useRecipeStore } from '@stores/recipe.store'

const recipeStore = useRecipeStore()
</script>

<template>
  <UiEmptyState
    v-if="recipeStore.recipes.length === 0"
    title="Keine Rezepte gefunden"
    description="Setz einen Filter zurück oder such nach einem anderen Begriff."
  >
    <template #media>
      <UiIcon
        :icon="SoupIcon"
        :size="24"
      />
    </template>
  </UiEmptyState>

  <ul
    v-else
    aria-label="Rezepte"
    class="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-4"
  >
    <li
      v-for="recipe in recipeStore.recipes"
      :key="recipe.id"
    >
      <RecipeCard :recipe="recipe" />
    </li>
  </ul>
</template>

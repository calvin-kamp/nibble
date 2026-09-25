<script setup lang="ts">
import { SoupIcon } from '@lucide/vue'
import { UiButton, UiEmptyState, UiIcon } from '@components/ui'
import { useRecipeStore } from '@stores/recipe.store'
import { useRecipeFilters } from '../recipe-filters'
import RecipeCard from './RecipeCard.vue'

const recipeStore = useRecipeStore()

const { apiQuery, resetPage } = useRecipeFilters()
</script>

<template>
  <!-- Loading state stays empty until the skeleton is built. -->
  <template v-if="recipeStore.isLoading" />

  <UiEmptyState
    v-else-if="recipeStore.loadError"
    title="Rezepte konnten nicht geladen werden"
    description="Die Verbindung wurde unterbrochen."
  >
    <UiButton
      variant="ghost"
      class="border border-input"
      @click="recipeStore.loadRecipes(apiQuery)"
    >
      Erneut versuchen
    </UiButton>
  </UiEmptyState>

  <UiEmptyState
    v-else-if="recipeStore.pageNotFound"
    title="Diese Seite gibt es nicht"
    description="Der Link ist wahrscheinlich veraltet."
  >
    <UiButton
      variant="ghost"
      class="border border-input"
      @click="resetPage"
    >
      Zur ersten Seite
    </UiButton>
  </UiEmptyState>

  <UiEmptyState
    v-else-if="recipeStore.recipes.length === 0"
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
    class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
  >
    <li
      v-for="recipe in recipeStore.recipes"
      :key="recipe.id"
    >
      <RecipeCard :recipe="recipe" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { RecipeListItem } from '../recipes.types'

import { SoupIcon } from '@lucide/vue'
import { computed } from 'vue'
import { UiButton, UiEmptyState, UiIcon } from '@components/ui'
import { useRecipeStore } from '@stores/recipe.store'
import { filterRecipes, useRecipeFilters } from '../recipe-filters'
import RecipeCard from './RecipeCard.vue'

const recipeStore = useRecipeStore()

const { filters, search } = useRecipeFilters()

const visibleRecipes = computed<RecipeListItem[]>(() =>
  filterRecipes(recipeStore.recipes, filters, search.value),
)
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
      @click="recipeStore.loadRecipes"
    >
      Erneut versuchen
    </UiButton>
  </UiEmptyState>

  <UiEmptyState
    v-else-if="visibleRecipes.length === 0"
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
      v-for="recipe in visibleRecipes"
      :key="recipe.id"
    >
      <RecipeCard :recipe="recipe" />
    </li>
  </ul>
</template>

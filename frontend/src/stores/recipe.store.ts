import type { RecipeListItem } from '@features/recipes/recipes.types'

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as recipesApi from '@api/recipes.api'

export const useRecipeStore = defineStore('recipe', () => {
  const recipes = ref<RecipeListItem[]>([])
  const isLoading = ref<boolean>(false)
  const loadError = ref<string | null>(null)

  async function loadRecipes(): Promise<void> {
    isLoading.value = true
    loadError.value = null

    try {
      recipes.value = await recipesApi.getRecipes()
    } catch {
      loadError.value = 'Rezepte konnten nicht geladen werden.'
    } finally {
      isLoading.value = false
    }
  }

  return { recipes, isLoading, loadError, loadRecipes }
})

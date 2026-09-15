import type { Recipe } from '@features/recipes/recipes.types'

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRecipeStore = defineStore('recipe', () => {
  const recipes = ref<Recipe[]>([])
  const isLoading = ref<boolean>(false)
  const loadError = ref<string | null>(null)

  return { recipes, isLoading, loadError }
})

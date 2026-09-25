import type {
  RecipeDetail,
  RecipeFormValues,
  RecipeListItem,
  RecipeListQuery,
  RecipePayload,
} from '@features/recipes/recipes.types'

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as recipesApi from '@api/recipes.api'
import { HttpError } from '@lib/http'

export const useRecipeStore = defineStore('recipe', () => {
  const recipes = ref<RecipeListItem[]>([])
  /** Number of recipes across all pages */
  const totalCount = ref<number>(0)
  const isLoading = ref<boolean>(false)
  const loadError = ref<string | null>(null)
  /** The requested page does not exist; the answer carries no total, so the last page stays unknown */
  const pageNotFound = ref<boolean>(false)

  // Only the newest request may write its result, older ones are dropped.
  let latestRequest = 0

  async function loadRecipes(query: RecipeListQuery = {}): Promise<void> {
    const request = ++latestRequest

    isLoading.value = true
    loadError.value = null
    pageNotFound.value = false

    try {
      const page = await recipesApi.getRecipes(query)

      if (request === latestRequest) {
        recipes.value = page.results
        totalCount.value = page.count
      }
    } catch (error) {
      if (request !== latestRequest) return

      if (error instanceof HttpError && error.status === 404) {
        pageNotFound.value = true

        return
      }

      loadError.value = 'Rezepte konnten nicht geladen werden.'
    } finally {
      if (request === latestRequest) isLoading.value = false
    }
  }

  function upsertInList(recipe: RecipeDetail): void {
    const exists = recipes.value.some((item) => item.id === recipe.id)

    recipes.value = exists
      ? recipes.value.map((item) => (item.id === recipe.id ? recipe : item))
      : [recipe, ...recipes.value]
  }

  /** Errors are left to the caller, the form shows them next to its buttons */
  async function saveRecipe(id: number | null, payload: RecipePayload): Promise<RecipeDetail> {
    const recipe =
      id === null
        ? await recipesApi.createRecipe(payload)
        : await recipesApi.updateRecipe(id, payload)

    upsertInList(recipe)

    return recipe
  }

  /** Uploads a new file, removes a cleared image, leaves an unchanged URL alone */
  async function saveRecipeImage(
    recipe: RecipeDetail,
    image: RecipeFormValues['image'],
  ): Promise<RecipeDetail> {
    if (image instanceof File) {
      const updated = await recipesApi.uploadRecipeImage(recipe.id, image)

      upsertInList(updated)

      return updated
    }

    if (image === null && recipe.image !== null) {
      await recipesApi.deleteRecipeImage(recipe.id)

      const updated = { ...recipe, image: null }

      upsertInList(updated)

      return updated
    }

    return recipe
  }

  async function deleteRecipe(id: number): Promise<void> {
    await recipesApi.deleteRecipe(id)

    recipes.value = recipes.value.filter((recipe) => recipe.id !== id)
  }

  return {
    recipes,
    totalCount,
    isLoading,
    loadError,
    pageNotFound,
    loadRecipes,
    saveRecipe,
    saveRecipeImage,
    deleteRecipe,
  }
})

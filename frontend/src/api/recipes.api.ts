import type { Paginated } from '@interfaces/pagination.types'
import type {
  RecipeDetail,
  RecipeListItem,
  RecipeListQuery,
  RecipePayload,
} from '@features/recipes/recipes.types'

import { http } from '@lib/http'

const RECIPES_PREFIX = '/recipes'

export function getRecipes(query: RecipeListQuery = {}): Promise<Paginated<RecipeListItem>> {
  const params = new URLSearchParams(query).toString()

  return http.get<Paginated<RecipeListItem>>(`${RECIPES_PREFIX}/${params ? `?${params}` : ''}`)
}

export function getRecipe(id: number): Promise<RecipeDetail> {
  return http.get<RecipeDetail>(`${RECIPES_PREFIX}/${id}/`)
}

export function createRecipe(payload: RecipePayload): Promise<RecipeDetail> {
  return http.post<RecipeDetail>(`${RECIPES_PREFIX}/`, payload)
}

export function updateRecipe(id: number, payload: RecipePayload): Promise<RecipeDetail> {
  return http.put<RecipeDetail>(`${RECIPES_PREFIX}/${id}/`, payload)
}

export function deleteRecipe(id: number): Promise<void> {
  return http.delete<void>(`${RECIPES_PREFIX}/${id}/`)
}

export function uploadRecipeImage(id: number, image: File): Promise<RecipeDetail> {
  const body = new FormData()

  body.append('image', image)

  return http.put<RecipeDetail>(`${RECIPES_PREFIX}/${id}/image/`, body)
}

export function deleteRecipeImage(id: number): Promise<void> {
  return http.delete<void>(`${RECIPES_PREFIX}/${id}/image/`)
}

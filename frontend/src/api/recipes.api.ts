import type { RecipeListItem } from '@features/recipes/recipes.types'

import { recipeListItems } from '@features/recipes/recipes.dummy'

// Dummy data until the backend is wired up. Later: http.get<RecipeListItem[]>('/recipes/')
export function getRecipes(): Promise<RecipeListItem[]> {
  return Promise.resolve(recipeListItems)
}

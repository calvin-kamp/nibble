import type { MaybeRefOrGetter, Ref } from 'vue'
import type { RecipeDetail } from './recipes.types'

import { ref, toValue, watch } from 'vue'
import * as recipesApi from '@api/recipes.api'
import { HttpError } from '@lib/http'

export type RecipeLoadStatus = 'loading' | 'loaded' | 'not-found' | 'error'

export function useRecipeDetail(id: MaybeRefOrGetter<number>): {
  recipe: Ref<RecipeDetail | null>
  status: Ref<RecipeLoadStatus>
  load: () => Promise<void>
} {
  const recipe = ref<RecipeDetail | null>(null)
  const status = ref<RecipeLoadStatus>('loading')

  /** Counts requests, so a slow answer for an old id can't overwrite a newer one */
  let requestCount = 0

  async function load(): Promise<void> {
    const request = ++requestCount

    status.value = 'loading'

    try {
      const result = await recipesApi.getRecipe(toValue(id))

      if (request !== requestCount) return

      recipe.value = result
      status.value = 'loaded'
    } catch (error) {
      if (request !== requestCount) return

      recipe.value = null
      status.value = error instanceof HttpError && error.status === 404 ? 'not-found' : 'error'
    }
  }

  watch(() => toValue(id), load, { immediate: true })

  return { recipe, status, load }
}
